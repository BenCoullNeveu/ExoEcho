import numpy as np
import pandas as pd
from astropy import constants as const
from astropy import units as u
import scipy.integrate as integrate

#-----# CONSTANTS #-----#
h = const.h.value # Planck constant
k_B = const.k_B.value # Boltzmann constant
c = const.c.value # speed of light in a vacuum
G = const.G.value # gravitational constant
m_p = const.m_p.value # proton mass

#-----# FUNCTIONS #-----#
# all from https://arxiv.org/abs/1502.00004 (Cowan et al 2015)

# helper function
def getConversion(units):
    if units in ["R_sun", "Rs"]:
        return const.R_sun.value
    elif units in ["R_jup", "Rj", "R_j"]:
        return const.R_jup.value
    elif units in ["R_earth", "Re", "R_e"]:
        return const.R_earth.value
    elif units in ["AU", "au"]:
        return const.au.value
    elif units in ["pc", "PC"]:
        return const.pc.value
    elif units in ["m"]:
       return 1.0
    elif units in ["um", "microns"]:
        return 1.0E-6
    elif units in ["nm"]:
        return 1.0E-9
    elif units in ["M_jup", "Mj", "M_j", "Mjup"]:
        return const.M_jup.value
    elif units in ["M_sun", "Ms", "M_s"]:
        return const.M_sun.value
    elif units in ["M_earth", "Me", "M_e", "Mearth"]:
        return const.M_earth.value
    else:
        raise ValueError('Invalid units. Can choose from: "R_sun", "R_jup", "R_earth", "AU", "pc", "m", "um", "nm", "M_jup", "M_sun", "M_earth".') 

# planck function
def planckFunc(wavelength:float,temperature:float, wavelength_units:str="um", h:float=h, k_B:float=k_B, c:float=c)->float:    
    """Returns the Planck function as a functions wavelength, λ, and temperature, T (in Kelvin).

    Args:
        wavelength (float): The provided wavelength, in units provided by wavelength_units.
        temperature (float): The provided temperature, in Kelvin.
        wavelength_units (str, optional): Units for wavelength. Defaults to "um".
        h (float, optional): Plank's constant. Defaults to astropy's constant value h.
        k_B (float, optional): Boltzmann constant. Defaults to astropy's constant value k_B.
        c (float, optional): Speed of light in a vacuum. Defaults to astropy's constant value c.
        

    Returns:
        float: Resulting value of the Plank function given the input values for wavelength and temperature.
    """
    w_conversion = getConversion(wavelength_units)
    
    exponent = h*c/((w_conversion*wavelength)*k_B*temperature)
    return 2 * h * c ** 2 / ((w_conversion*wavelength) ** 5) / (np.exp(exponent) - 1)

v_planckFunc = np.vectorize(planckFunc)
v_planckFunc.__doc__ = "Vectorized version of the function planckFunc."


# dayside emitting temperature
def Tday(T_star:float, R_star:float, a:float, Ab:float=0.3, E:float=0.2, R_units:str="R_sun", a_units:str="AU")->float:
    """Returns the dayside emitting temperature, as defined in Cowan et al 2015.

    Args:
        T_star (float): Stellar effective temperature, in K.
        R_star (float): Stellar radius, with units given by R_units. 
        a (float): Semi-major axis of planet, with units given by a_units.
        Ab (float, optional): Bond albedo. Defaults to 0.3.
        E (float, optional): Heat recirculation efficiency. Defaults to 0.2.
        R_units (str, optional): Units of provided stellar radius, R_star. Defaults to Solar radii, "R_sun".
        a_units (str, optional): Units of provided semi-major axis, a. Defaults to Astronomical units, "AU".

    Returns:
        floats: Resulting dayside emitting temperature.
    """
    # checking values for bond albedo and heat recirculation efficiency
    if Ab is None:
        Ab = 0.3
    if E is None:
        E = 0.2
    
    R_conversion = getConversion(R_units)
    a_conversion = getConversion(a_units)
    
    return T_star * (np.sqrt((R_star*R_conversion)/(a*a_conversion))) * ((1-Ab)*(2/3-E*5/12))**0.25

v_Tday = np.vectorize(Tday)
v_Tday.__doc__ = "Vectorized version of the function Tday."


def Tdayunc(wavelength_range:tuple, Td, Ts, Rs, Rp, Flux, w_units='microns', Rs_units='Rs', Rp_units='Rj')->float: 
    """Return the uncertainty on Tday*ESM. As such, to get Tday_unc, divide the result by ESM.
    
    Args:
        wavelength_range (tuple): Wavelength range over which to integrate.
        Td (float): Dayside temperature.
        Ts (float): Stellar temperature.
        Rs (float): Stellar radius.
        Rp (float): Planetary radius.
        Flux (float): Flux.
        w_units (str, optional): Wavelength units. Defaults to 'microns'.
        Rs_units (str, optional): Stellar radius units. Defaults to 'Rs'.
        Rp_units (str, optional): Planetary radius units. Defaults to 'Rj'.
        
    Returns:
        float: Uncertainty on Tday*ESM.
        """
        
    w_con = getConversion(w_units)
    Rs_con = getConversion(Rs_units)
    Rp_con = getConversion(Rp_units)
        
    def integrand(wavelength):
        return wavelength * (1 - (Rs*Rs_con)**2 / ((Rp*Rp_con)**2 * (np.exp(k_B * Ts * wavelength / (h * c)) - 1) / Flux + (Rs*Rs_con)**2)  )

    def integrate_range(wavelength_range):
        lower_bound, upper_bound = wavelength_range
        lower_bound *= w_con
        upper_bound *= w_con
        
        integral, _ = integrate.quad(integrand, lower_bound, upper_bound)
        return integral / (upper_bound - lower_bound)  # Averaging over the range
    
    return Td * k_B / (h * c) * integrate_range(wavelength_range)

v_Tdayunc = np.vectorize(Tdayunc)
v_Tdayunc.__doc__ = "Vectorized version of the function Tdayunc."



# thermal contrast ratio
def eclipseFlux(Rp:float, R_star:float, wavelength:float, tday:float, teff:float, Rp_units:str="R_jup", R_star_units:str="R_sun", wavelength_units:str="um")->float:
    """Returns the thermal contrast ratio.

    Args:
        Rp (float): Planetary radius, in units provided by Rp_units.
        R_star (float): Stellar radius, in units provided by R_star_units.
        wavelength (float): Wavelength, in units provided by wavelength_units. Can also be a tuple or list-like data structure with two wavelengths indicating the lower bound and the upper bound of an instrument having "integrated band" capabilities.
        tday (float): Planetary dayside emitting temperature.
        teff (float): Stellar effective temperature
        Rp_units (str, optional): Units of provided planetary radius, Rp. Defaults to "R_jup".
        R_star_units (str, optional): Units of provided stellar radius, R_star. Defaults to "R_sun".
        wavelength_units (str, optional): Units of wavelength. Defaults to "um".

    Returns:
        float: Resulting thermal contrast ratio.
    """
    
    if type(wavelength) in [float, int, np.int_, np.float_]:
        radius_ratio = ( (Rp*getConversion(Rp_units)) / (R_star*getConversion(R_star_units)) )**2
        planck_function_planet = planckFunc(wavelength, tday, wavelength_units)
        planck_function_star = planckFunc(wavelength, teff, wavelength_units)
    
        return (radius_ratio*(planck_function_planet/planck_function_star))
    
    try:
        if len(wavelength) == 2:
            
            def integrand(wavelength):
                return eclipseFlux(Rp, R_star, wavelength, tday, teff, Rp_units, R_star_units, wavelength_units)
            
        I = integrate.quad(integrand, wavelength[0], wavelength[1])
        return I[0] / abs(wavelength[0] - wavelength[1])  # Average over the wavelength range
            
    except:
        raise Exception(f"wavelength must be of type float or list-like with length 2. Received type: {wavelength} which is of type {type(wavelength)}.")
    
v_eclipseFlux = np.vectorize(eclipseFlux)
v_eclipseFlux.__doc__ = "Vectorized version of the function eclipseFlux."
        
# transit flux ratio
def transitFlux(Rp:float, R_star:float, Mp:float, T:float, mu:float, Nh:float=4, Rp_units:str="R_jup", R_star_units:str="R_sun", Mp_units:str="M_jup")->float:
    """Returns the transit flux ratio.

    Args:
        Rp (float): Planetary radius, in units provided by Rp_units.
        R_star (float): Stellar radius, in units provided by R_star_units.
        Mp (float): Planet mass, in units provided by Mp_units.
        T (float): Surface temperature.
        mu (float): Atmospheric mean molecular mass.
        Nh (float, optional): Number of scale heights probed. Defaults to 4 (Griffiths 2014).
        Rp_units (str, optional): Units of provided planetary radius, Rp. Defaults to "R_jup".
        R_star_units (str, optional): Units of wavelength. Defaults to "R_sun".
        Mp_units (str, optional): Units of provided planetary mass, Mp. Defaults to "M_jup".

    Returns:
        float: Resulting transit flux ratio.
    """
    Rp = Rp*getConversion(Rp_units)
    Mp = Mp*getConversion(Mp_units)
    R_star = R_star*getConversion(R_star_units)
    
    g = G * Mp / Rp**2
    H = k_B * T / (mu*m_p * g)
    return 2 * Rp * Nh * H / R_star**2

v_transitFlux = np.vectorize(transitFlux)
v_transitFlux.__doc__ = "Vectorized version of the function transitFlux."


# reflected light contrast
def reflectionFlux(Rp:float, a:float, Ag:float, Rp_units:str="R_jup", a_units:str="au")->float:
    """Returns the reflected light contrast.

    Args:
        Rp (float): Planetary radius, in units provided by Rp_units.
        a (float): Stellar radius, in units provided by R_star_units.
        Ag (float): Geometric albedo.
        Rp_units (str, optional): Units of provided planetary radius, Rp. Defaults to "R_jup".
        a_units (str, optional): Units of wavelength. Defaults to "a_units".

    Returns:
        float: reflected light contrast.
    """
    return Ag * (Rp*getConversion(Rp_units) / (a*getConversion(a_units)))**2

v_reflectionFlux = np.vectorize(reflectionFlux)
v_reflectionFlux.__doc__ = "Vectorized version of the function reflectionFlux."
   
   
# Number of photons
def NPhotons(T_star:float, wavelengths:tuple[float], throughput:float, 
             integration_time:float, R_star:float, D_telescope:float, distance:float=20,
             wavelength_units:str="um", R_star_units:str="R_sun", distance_units="pc")->float:
    """Returns the number of photons collected by a telescope system. 

    Args:
        T_star (float): Stellar temperature, in K.
        wavelengths (tuple[float]): Lower and upper wavelength bounds (i.e., minimum and maxiomum wavelengths that system observes).
        throughput (float): System throughput (i.e., number of electrons out per photon in).
        integration_time (float): Total observation time, in s.
        R_star (float): Stellar radius, in units given by R_star_units.
        D_telescope (float): Diameter of telescope, in m.
        distance (float, optional): Distance to target. Defaults to 20pc (or whatever units provided by distance_units).
        wavelength_units (str, optional): Units for wavelength. Defaults to "um".
        R_star_units (str, optional): Stellar radius units. Defaults to solar radii, "R_sun".
        distance_units (str, optional): Distance to target units. Defaults to parsecs, "pc".

    Returns:
        float: Number of photons collected by a telescope system.
    """
    def planckInt(wavelength, T_star, wavelength_units):
        return planckFunc(wavelength, T_star, wavelength_units) * wavelength * getConversion(wavelength_units)
    
    lambda1 = wavelengths[0] * getConversion(wavelength_units)
    lambda2 = wavelengths[1] * getConversion(wavelength_units)
    I = integrate.quad(planckInt, lambda1, lambda2, args=(T_star, "m"))
    
    return np.pi**2 * throughput * integration_time / (h*c) * (R_star*getConversion(R_star_units) * D_telescope / (2*distance*getConversion(distance_units)))**2 * I[0]

v_NPhotons = np.vectorize(NPhotons)
v_NPhotons.__doc__ = "Vectorized version of the function NPhotons."


# Noise estimate
def noiseEstimate(T_star:float, wavelengths:tuple[float], throughput:float, 
                      integration_time:float, R_star:float, D_telescope:float, distance:float=20,
                      wavelength_units="um", R_star_units:str="R_sun", distance_units="pc")->float:
    """Returns the precision (i.e., noise) estimate of a particular telescope system when observing a particular object. 

    Args:
        T_star (float): Stellar temperature, in K.
        wavelengths (tuple[float]): Lower and upper wavelength bounds (i.e., minimum and maxiomum wavelengths that system observes).
        throughput (float): System throughput (i.e., number of electrons out per photon in).
        integration_time (float): Total observation time, in s.
        R_star (float): Stellar radius, in units given by R_star_units.
        D_telescope (float): Diameter of telescope, in m.
        distance (float, optional): Distance to target. Defaults to 20pc (or whatever units provided by distance_units).
        wavelength_units (str, optional): Units for wavelength. Defaults to "um".
        R_star_units (str, optional): Stellar radius units. Defaults to solar radii, "R_sun".
        distance_units (str, optional): Distance to target units. Defaults to parsecs, "pc".

    Returns:
        float: Noise estimate given the telescope, stellar, and planetary parameters.
    """
    return np.sqrt(2 / NPhotons(T_star, wavelengths, throughput, integration_time, R_star, D_telescope, distance, wavelength_units, R_star_units, distance_units))

v_noiseEstimate = np.vectorize(noiseEstimate)
v_noiseEstimate.__doc__ = "Vectorized version of the function noiseEstimate."


# ESM estimate
def ESM(wavelengths:tuple[float], throughput:float, 
        integration_time:float,Rp:float, R_star:float, D_telescope:float, 
        tday:float, teff:float, distance:float=20,
        wavelength_units:str="um", Rp_units:str="R_jup", R_star_units:str="R_sun", distance_units:str="pc")->float:
    """Returns the ESM based on the input parameters.

    Args:
        wavelengths (tuple[float]): Lower and upper wavelength bounds (i.e., minimum and maxiomum wavelengths that system observes).
        throughput (float): System throughput (i.e., number of electrons out per photon in).
        integration_time (float): Total observation time, in s.
        Rp (float): Planet radiy, in units given by Rp_units.
        R_star (float): Stellar radius, in units given by R_star_units.
        D_telescope (float): Diameter of telescope, in m.
        tday (float): Planet's dayside emitting temperature, in K.
        teff (float): Stellar effective temperature, in K.
        distance (float, optional): Distance to target. Defaults to 20pc (or whatever units provided by distance_units).
        wavelength_units (str, optional): Units for wavelength. Defaults to "um".
        Rp_units (str, optional): Planet radius units. Defaults to Jupiter radii, "R_jup".
        R_star_units (str, optional): Stellar radius units. Defaults to solar radii, "R_sun".
        distance_units (str, optional): Distance to target units. Defaults to parsecs, "pc".

    Returns:
        float: Estimated ESM
    """
    
    signal = eclipseFlux(Rp, R_star, wavelengths, tday, teff, Rp_units, R_star_units, wavelength_units)
    noise = noiseEstimate(teff, wavelengths, throughput, 
                              integration_time, R_star, D_telescope, distance, 
                              wavelength_units, R_star_units, distance_units)
    
    return signal / noise

v_ESM = np.vectorize(ESM)
v_ESM.__doc__ = "Vectorized version of the function ESM."


# TSM estimate
def TSM(wavelengths:tuple[float], T_star:float, throughput:float, Rp:float, R_star:float, Mp:float, T:float, mu:float, integration_time:float,
        D_telescope:float, Nh:float=4, Rp_units:str="R_jup", R_star_units:str="R_sun", Mp_units:str="M_jup", 
        distance:float=20, wavelength_units="um", distance_units="pc")->float:
    """_summary_

    Args:
        wavelengths (tuple[float]): Lower and upper wavelength bounds (i.e., minimum and maxiomum wavelengths that system observes).
        T_star (float): _description_
        throughput (float): _description_
        Rp (float): _description_
        R_star (float): _description_
        Mp (float): _description_
        T (float): _description_
        mu (float): _description_
        integration_time (float): _description_
        D_telescope (float): _description_
        Nh (float, optional): _description_. Defaults to 4.
        Rp_units (str, optional): _description_. Defaults to "R_jup".
        R_star_units (str, optional): _description_. Defaults to "R_sun".
        Mp_units (str, optional): _description_. Defaults to "M_jup".
        distance (float, optional): _description_. Defaults to 20.
        wavelength_units (str, optional): _description_. Defaults to "um".
        distance_units (str, optional): _description_. Defaults to "pc".

    Returns:
        float: _description_
    """
    
    signal = transitFlux(Rp, R_star, Mp, T, mu, Nh, Rp_units, R_star_units, Mp_units)
    noise = noiseEstimate(T_star, wavelengths, throughput, integration_time, R_star, D_telescope, distance, wavelength_units, R_star_units, distance_units)
    return signal / noise

v_TSM = np.vectorize(TSM)
v_TSM.__doc__ = "Vectorized version of the function TSM."


# direct star SNR. Useful for brown dwarfs
def stellarSNR(T_star:float, wavelengths:tuple[float], throughput:float, 
                integration_time:float, R_star:float, D_telescope:float, distance:float=20,
                wavelength_units="um", R_star_units:str="R_sun", distance_units="pc")->float:
    """_summary_

    Args:
        T_star (float): _description_
        wavelengths (tuple[float]): _description_
        throughput (float): _description_
        integration_time (float): _description_
        R_star (float): _description_
        D_telescope (float): _description_
        distance (float, optional): _description_. Defaults to 20.
        wavelength_units (str, optional): _description_. Defaults to "um".
        R_star_units (str, optional): _description_. Defaults to "R_sun".
        distance_units (str, optional): _description_. Defaults to "pc".

    Returns:
        float: _description_
    """
    return np.sqrt(NPhotons(T_star, wavelengths, throughput, integration_time, R_star, D_telescope, distance, wavelength_units, R_star_units, distance_units))