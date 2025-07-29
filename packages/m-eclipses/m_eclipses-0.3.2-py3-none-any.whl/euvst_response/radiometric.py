"""
Radiometric pipeline functions for converting intensities to detector signals.
"""

from __future__ import annotations
import numpy as np
import astropy.units as u
import astropy.constants as const
from ndcube import NDCube
from scipy.signal import convolve2d
from .utils import wl_to_vel, vel_to_wl
from scipy.special import voigt_profile


def _vectorized_fano_noise(photon_counts: np.ndarray, rest_wavelength: u.Quantity, det) -> np.ndarray:
    """
    Vectorized version of Fano noise calculation for improved performance.
    
    Parameters
    ----------
    photon_counts : np.ndarray
        Array of photon counts (unitless values)
    rest_wavelength : u.Quantity
        Rest wavelength with units
    det : Detector_SWC or Detector_EIS
        Detector object with fano noise parameters
        
    Returns
    -------
    np.ndarray
        Array of electron counts with Fano noise applied
    """
    # Handle zero or negative photon counts
    mask_positive = photon_counts > 0
    electron_counts = np.zeros_like(photon_counts)
    
    if not np.any(mask_positive):
        return electron_counts
    
    # Get CCD temperature - must be set via with_temperature()
    if not hasattr(det, '_ccd_temperature'):
        raise ValueError("CCD temperature not set. Use Detector_SWC.with_temperature() to create detector instance.")
    
    # Convert to Kelvin for the calculation
    temp_kelvin = det._ccd_temperature.to(u.K, equivalencies=u.temperature()).value
    
    # Convert wavelength to photon energy: E = hc/λ
    photon_energy_ev = (const.h * const.c / (rest_wavelength.to(u.angstrom))).to(u.eV).value
    
    # Calculate temperature-dependent energy per electron-hole pair
    w_T = 3.71 - 0.0006 * (temp_kelvin - 300.0)  # eV per electron-hole pair
    
    # Mean number of electrons per photon
    mean_electrons_per_photon = photon_energy_ev / w_T
    
    # Fano noise variance per photon
    sigma_fano_per_photon = np.sqrt(det.si_fano * mean_electrons_per_photon)
    
    # Work only with positive photon counts
    positive_photons = photon_counts[mask_positive]
    
    # For efficiency, use a simpler approximation for most cases
    # The exact method is: for each photon, sample from Normal(mean_e, sigma_fano)
    # Approximation: for N photons, sample from Normal(N*mean_e, sqrt(N)*sigma_fano)
    # This is mathematically equivalent for large N and much faster
    
    mean_total_electrons = positive_photons * mean_electrons_per_photon
    std_total_electrons = np.sqrt(positive_photons) * sigma_fano_per_photon
    
    # Sample total electrons per pixel
    total_electrons = np.random.normal(
        loc=mean_total_electrons,
        scale=std_total_electrons
    )
    
    # Ensure non-negative
    total_electrons = np.maximum(total_electrons, 0)
    
    # Map back to full array
    electron_counts[mask_positive] = total_electrons
    
    return electron_counts


def intensity_to_photons(I: NDCube) -> NDCube:
    """Convert intensity to photon flux."""
    wl_axis = I.axis_world_coords(2)[0]
    E_ph = (const.h * const.c / wl_axis).to("erg") * (1 / u.photon)
    
    photon_data = (I.data * I.unit / E_ph).to(u.photon / u.cm**2 / u.sr / u.cm)
    
    return NDCube(
        data=photon_data.value,
        wcs=I.wcs.deepcopy(),
        unit=photon_data.unit,
        meta=I.meta,
    )


def add_effective_area(ph_flux: NDCube, tel) -> NDCube:
    """Add telescope effective area to photon flux."""
    wl0 = ph_flux.meta['rest_wav']
    wl_axis = ph_flux.axis_world_coords(2)[0]
    A_eff = np.array([tel.ea_and_throughput(wl).cgs.value for wl in wl_axis]) * u.cm**2
    
    out_data = (ph_flux.data * ph_flux.unit * A_eff)
    
    return NDCube(
        data=out_data.value,
        wcs=ph_flux.wcs.deepcopy(),
        unit=out_data.unit,
        meta=ph_flux.meta,
    )


def photons_to_pixel_counts(ph_flux: NDCube, wl_pitch: u.Quantity, plate_scale: u.Quantity, slit_width: u.Quantity) -> NDCube:
    """Convert photon flux to pixel counts (total over exposure)."""
    pixel_solid_angle = ((plate_scale * u.pixel * slit_width).cgs / const.au.cgs ** 2) * u.sr
    
    out_data = (ph_flux.data * ph_flux.unit * pixel_solid_angle * wl_pitch)
    
    return NDCube(
        data=out_data.value,
        wcs=ph_flux.wcs.deepcopy(),
        unit=out_data.unit,
        meta=ph_flux.meta,
    )


def apply_psf(signal: NDCube, tel) -> NDCube:
    """
    Convolve each detector row (first axis) of an NDCube with a parameterized PSF.

    Parameters
    ----------
    signal : NDCube
        Input cube with shape (n_scan, n_slit, n_lambda).
        The first axis is stepped by the raster scan.
    tel : Telescope_EUVST or Telescope_EIS
        Telescope configuration containing PSF parameters.
        For Gaussian: psf_params = [width]
        For Voigt: psf_params = [width, gamma]

    Returns
    -------
    NDCube
        New cube with identical WCS / unit / meta but PSF-blurred data.
    """
    
    # Extract data and units
    data_in = signal.data  # ndarray view (no units)
    unit = signal.unit
    n_scan, n_slit, n_lambda = data_in.shape

    # Get PSF parameters from telescope
    psf_type = tel.psf_type.lower()
    psf_params = tel.psf_params
    
    # Extract width parameter (first parameter for both Gaussian and Voigt)
    width_pixels = psf_params[0].to(u.pixel).value
    
    # Create 2D PSF kernel
    # Make kernel size based on width (use 6*width to capture most of the profile)
    kernel_size = max(7, int(6 * width_pixels))
    if kernel_size % 2 == 0:  # Ensure odd size for symmetric kernel
        kernel_size += 1
    
    # Create coordinate grids centered at 0
    center = kernel_size // 2
    y, x = np.mgrid[:kernel_size, :kernel_size]
    y = y - center
    x = x - center
    
    # Create radial distance from center
    r = np.sqrt(x**2 + y**2)
    
    # Create PSF based on type
    if psf_type == "gaussian":
        sigma = width_pixels
        psf = np.exp(-0.5 * (r / sigma)**2)
        
    elif psf_type == "voigt":
        # For Voigt: need both width and gamma parameters
        if len(psf_params) < 2:
            raise ValueError("Voigt PSF requires two parameters: [width, gamma]")

        sigma_gauss = width_pixels
        # Get gamma parameter for Lorentzian component
        gamma_lorentz = psf_params[1].to(u.pixel).value
        
        # Create 2D Voigt PSF (approximate as radially symmetric)
        psf = voigt_profile(r, sigma_gauss, gamma_lorentz)
        
    else:
        raise ValueError(f"Unsupported PSF type: {psf_type}. Supported types: 'gaussian', 'voigt'")
    
    # Normalize PSF
    psf = psf / np.sum(psf)

    # Convolve each scan position
    blurred = np.empty_like(data_in)
    for i in range(n_scan):
        blurred[i] = convolve2d(data_in[i], psf, mode="same")

    return NDCube(
        data=blurred,
        wcs=signal.wcs.deepcopy(),
        unit=unit,
        meta=signal.meta,
    )


def to_electrons(photon_counts: NDCube, t_exp: u.Quantity, det) -> NDCube:
    """
    Convert a photon-count NDCube to an electron-count NDCube.

    Parameters
    ----------
    photon_counts : NDCube
        Cube of total photon counts per pixel (over exposure).
    t_exp : Quantity
        Exposure time (used for dark current and read noise).
    det : Detector_SWC or Detector_EIS
        Detector description.

    Returns
    -------
    NDCube
        Electron counts per pixel for the given exposure.
    """
    # Get rest wavelength from metadata (keep as Quantity with units)
    rest_wavelength = photon_counts.meta['rest_wav']  # Should be a Quantity

    # Apply quantum efficiency first using binomial distribution (proper physics)
    photons_detected = np.random.binomial(
        photon_counts.to(u.photon/u.pix).data.astype(int),  # Extract unitless data
        det.qe_euv
    )

    # Apply proper Fano noise per pixel using a vectorized approach
    electron_counts = _vectorized_fano_noise(photons_detected.astype(float), rest_wavelength, det)

    e = electron_counts * (u.electron / u.pixel)

    # Add dark current and read noise (these still depend on exposure time)
    e += det.dark_current * t_exp                                     # dark current
    e += np.random.normal(0, det.read_noise_rms.value,
                          photon_counts.data.shape) * (u.electron / u.pixel)  # read noise

    e = e.to(u.electron / u.pixel)
    e_val = e.value
    e_val[e_val < 0] = 0                                              # clip negatives

    return NDCube(
        data=e_val,
        wcs=photon_counts.wcs.deepcopy(),
        unit=e.unit,
        meta=photon_counts.meta,
    )


def to_dn(electrons: NDCube, det) -> NDCube:
    """
    Convert an electron-count NDCube to DN and clip at the detector's full-well.

    Parameters
    ----------
    electrons : NDCube
        Electron counts per pixel (u.electron / u.pixel).
    det : Detector_SWC or Detector_EIS
        Detector description containing the gain and max DN.

    Returns
    -------
    NDCube
        Same cube in DN / pixel, with values clipped to det.max_dn.
    """
    dn_q = (electrons.data * electrons.unit) / det.gain_e_per_dn          # Quantity
    dn_q = dn_q.to(det.max_dn.unit)

    dn_val = dn_q.value
    dn_val[dn_val > det.max_dn.value] = det.max_dn.value                  # clip

    return NDCube(
        data=dn_val,
        wcs=electrons.wcs.deepcopy(),
        unit=dn_q.unit,
        meta=electrons.meta,
    )


def add_poisson(cube: NDCube) -> NDCube:
    """
    Apply Poisson noise to an input NDCube and return a new NDCube
    with the same WCS, unit, and metadata.

    Parameters
    ----------
    cube : NDCube
        Input data cube.

    Returns
    -------
    NDCube
        New cube containing Poisson-noised data.
    """
    noisy = np.random.poisson(cube.data) * cube.unit
    return NDCube(
        data=noisy.value,
        wcs=cube.wcs.deepcopy(),
        unit=noisy.unit,
        meta=cube.meta,
    )


def apply_exposure_and_poisson(I: NDCube, t_exp: u.Quantity) -> NDCube:
    """
    Apply exposure time to intensity and add Poisson noise.
    
    This converts intensity (per second) to total counts over the exposure
    and applies appropriate Poisson noise.

    Parameters
    ----------
    I : NDCube
        Input intensity cube (per second).
    t_exp : u.Quantity
        Exposure time.

    Returns
    -------
    NDCube
        New cube with exposure applied and Poisson noise added.
    """
    # Convert intensity rate to total intensity over exposure
    total_intensity = (I.data * I.unit * t_exp)
    
    # Apply Poisson noise
    noisy = np.random.poisson(total_intensity.value) * total_intensity.unit
    
    return NDCube(
        data=noisy.value,
        wcs=I.wcs.deepcopy(),
        unit=noisy.unit,
        meta=I.meta,
    )


def add_stray_light(electrons: NDCube, t_exp: u.Quantity, det, sim) -> NDCube:
    """
    Add visible-light stray-light to a cube of electron counts.

    Parameters
    ----------
    electrons : NDCube
        Electron counts per pixel (unit: u.electron / u.pixel).
    t_exp : astropy.units.Quantity
        Exposure time.
    det : Detector_SWC or Detector_EIS
        Detector description.
    sim : Simulation
        Simulation parameters (contains vis_sl - photon/s/pix).

    Returns
    -------
    NDCube
        New cube with stray-light signal added.
    """
    # Draw Poisson realisation of stray-light photons
    n_vis_ph = np.random.poisson(
        (sim.vis_sl * t_exp).to_value(u.photon / u.pixel),
        size=electrons.data.shape
    ) * (u.photon / u.pixel)

    # Assume visible stray light is ~600nm (typical visible wavelength)
    visible_wavelength = 600 * u.nm  # Keep as Quantity with units
    
    # Apply quantum efficiency first, then vectorized Fano noise
    vis_photons_detected = np.random.binomial(
        n_vis_ph.to_value(u.photon / u.pixel).astype(int),
        det.qe_vis
    )
    
    # Apply vectorized Fano noise to detected visible photons
    stray_electrons_values = _vectorized_fano_noise(vis_photons_detected.astype(float), visible_wavelength, det)
    stray_electrons = stray_electrons_values * (u.electron / u.pixel)

    # Add to original signal
    out_q = electrons.data * electrons.unit + stray_electrons
    out_q = out_q.to(electrons.unit)

    return NDCube(
        data=out_q.value,
        wcs=electrons.wcs.deepcopy(),
        unit=out_q.unit,
        meta=electrons.meta,
    )
