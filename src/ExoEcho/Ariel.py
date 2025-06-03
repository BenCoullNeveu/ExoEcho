import pandas as pd 
import matplotlib.pyplot as plt
from matplotlib.transforms import Bbox
import seaborn as sns
# from .Functions import *
# from .Telescope import *
from Functions import *
from Telescope import *
from RuntimeAnimation import animated_coffee

from numba import jit, prange
import time

from warnings import simplefilter
simplefilter(action="ignore", category=pd.errors.PerformanceWarning)

# target list directory
target_lists = os.path.join(cur_dir, "target_lists")
telescopes = os.path.join(cur_dir, "Telescopes")

# working directory
work_dir = os.getcwd()


# getting target list
target_list_name = "Ariel_MCS_Known_2024-03-27"
target_list = pd.read_csv(f"{target_lists}/{target_list_name}.csv")


### Opening telescopes for Ariel ###
def openArielInstruments(target_list_name=None, show:bool=True):
    global instruments
    targets = target_list_name
    if target_list_changed:
        targets = getTargetList()[0]
    
    instruments = openInstruments(telescope="Ariel", target_list=targets, show=show)
    
print("________________________________________________________________\n"+
      "Opening all instruments into dictionary object 'instruments'...\n")

# getting the instruments dictionary
instruments = {}
openArielInstruments()


# construct ariel instruments with custom target list
# @animated_coffee
def constructArielInstruments(target_list_name:str=target_list_name, target_list=None):
    if target_list is None:
        target_list = pd.read_csv(f"{target_lists}/{target_list_name}.csv")
        
    ## TIER 1 ##
    Telescope("Ariel NIRSpec", 1, (1.10, 1.95), 1, 0.27, target_list, target_list_name).constructTable()
    Telescope("Ariel AIRS CH0", 1, (1.95, 3.9), 3, 0.18, target_list, target_list_name).constructTable()
    Telescope("Ariel AIRS CH1", 1, (3.9, 7.8), 1, 0.18, target_list, target_list_name).constructTable()


    ## TIER 2 ##
    Telescope("Ariel NIRSpec", 1, (1.10, 1.95), 10, 0.27, target_list, target_list_name).constructTable()
    Telescope("Ariel AIRS CH0", 1, (1.95, 3.9), 50, 0.18, target_list, target_list_name).constructTable()
    Telescope("Ariel AIRS CH1", 1, (3.9, 7.8), 10, 0.18, target_list, target_list_name).constructTable()


    ## TIER 3 ##
    Telescope("Ariel NIRSpec", 1, (1.10, 1.95), 20, 0.27, target_list, target_list_name).constructTable()
    Telescope("Ariel AIRS CH0", 1, (1.95, 3.9), 100, 0.18, target_list, target_list_name).constructTable()
    Telescope("Ariel AIRS CH1", 1, (3.9, 7.8), 30, 0.18, target_list, target_list_name).constructTable()

    ## Photometric instruments ##
    Telescope("Ariel FGS1", 1, (0.6, .8), 1, 0.17, target_list, target_list_name).constructTable()
    Telescope("Ariel FGS2", 1, (0.8, 1.10), 1, 0.25, target_list, target_list_name).constructTable()
    Telescope("Ariel VISPhot", 1, (0.5, .6), 1, 0.2, target_list, target_list_name).constructTable()
    
    setTargetList(target_list_name)
    openArielInstruments(show=False)
    print("Successfully updated the Ariel.instruments dictionary with the newly constructed Ariel instruments.")



# data retrieval
def getInstrument(instrument_name:str, target_list_name=target_list_name):
    try: 
        instruments["Ariel"][target_list_name]
    except:
        setTargetList(target_list_name)
        openArielInstruments(show=False)
    
    keys = instruments["Ariel"][target_list_name].keys()
    
    
    normalized_instrument_name = normalize_name(instrument_name)

    telescope = ''
    for instrument in keys:
        normalized_telescope_name = normalize_name(instrument)

        is_in = all(word in normalized_telescope_name for word in normalized_instrument_name)
        # is_in = check_all(normalized_telescope_name, normalized_instrument_name)
                
        if is_in:
            if telescope != '':
                raise ValueError(f"Cannot find desired instrument. Note that this error is raised if the name is degenerate, in which case consider being more specific. The available instruments are in the following sorted list.\n\n {sorted(keys, key=str.lower)}")
            telescope = instruments["Ariel"][target_list_name][instrument]
            
    if telescope == '':
        raise ValueError(f"No matching instrument found with '{instrument_name}'. Check spelling and the following sorted list of included instruments.\n\n {sorted(keys, key=str.lower)}")
        
        
        
        
    # except:
    # telescope = getTelescope("Ariel " + instrument_name)
    # if make_table:
    #     if target_list is None:
    #         raise ValueError("Be sure to inclide desired target_list if wanting to construct the table (i.e., if make_table=True)")
    #     else:
    #         telescope.target_list = target_list
    #         telescope.constructTable()
                
    return telescope


def checkInstrument(instrument:str)->Telescope:
    if type(instrument) == str:
        return getInstrument(instrument, target_list_name)
    elif type(instrument) != Telescope:
        raise ValueError("instruments must be a list of strings or Telescope objects")
    
    # implicit elif type(instrument) == Telescope
    return instrument # returning the instrument as Telescope object


# plotting fill space for instrument sensitivity range
def plotSensitivityRange(instruments:dict=["VISPhot", "FGS1", "FGS2", "NIRSpec R=1", "AIRS CH0 R=3", "AIRS CH1 R=1"], 
                         ax:plt.Axes=None, cmap=None, pad=10, label_on_plot=True):
    
    # check if ax is provided
    if ax is None:
        fig, ax = plt.subplots()
        
    # fill color palette
    if cmap is None:
        cmap = sns.color_palette('tab10')
    sns.set_palette(sns.color_palette(cmap, len(instruments)))
    
    y0 = ax.get_ylim()[0]
    
    # plot the sensitivity range of the instruments
    for i, instrument in enumerate(instruments):
        
        # check if instruments are strings or Telescope objects
        instrument = checkInstrument(instrument)
    
        # plot the wavelength range of the instrument
        w1, w2 = instrument.wavelength_range
        
        label = None
        if not label_on_plot:
            label = instrument.name.replace("Ariel ", '')
        else:
            text = ax.text((w1+w2)/2, y0, instrument.name.replace("Ariel ", ''), fontsize=10, color=cmap[i], rotation=0, ha='center', va='top')
            
            renderer = ax.get_figure().canvas.get_renderer()
            bbox_text = text.get_window_extent(renderer=renderer)

            # transform bounding box to data coordinates
            transformer = ax.transData.inverted().transform
            bbox_text = Bbox(transformer(bbox_text))
            
            w = bbox_text.width
            if w > w2 - w1:
                text.set_rotation(270)
                text.set_va('top')
                text.set_ha('center')
                _, y0 = transformer([ax.get_window_extent().x0, (100-pad)/100 *ax.get_window_extent().y0])
                text.set_position((text.get_position()[0], y0))
            
        ax.axvspan(w1, w2, alpha=0.2, color=cmap[i], label=label)
        

def getTieredInstruments(tier:str):
    """Return a list of instruments based on the given tier.

    Args:
        tier (str): The tier for which to retrieve the instruments.

    Returns:
        list: A list of instruments corresponding to the given tier.
    """
    
    if type(tier) in [int, float]:
        tier = f'tier {round(tier)}'
    
    if tier.lower().replace(" ", "") in ['tier1', 'tieri', 'tierone']:
        return ["VISPhot", "FGS1", "FGS2", "NIRSpec R=1", "AIRS CH0 R=3", "AIRS CH1 R=1"], "Tier 1"
    
    elif tier.lower().replace(" ", "") in ['tier2', 'tierii', 'tiertwo']:
        return ["VISPhot", "FGS1", "FGS2", "NIRSpec R=10", "AIRS CH0 R=50", "AIRS CH1 R=10"], "Tier 2"
    
    elif tier.lower().replace(" ", "") in ['tier3', 'tieriii', 'tierthree']:
        return ["VISPhot", "FGS1", "FGS2", "NIRSpec R=20", "AIRS CH0 R=100", "AIRS CH1 R=30"], "Tier 3"
    
# @jit(parallel=True)
def __avgSNR(planet:str, tier:str, SNR_param:str, iterations:int):
    # getting instruments based on the tier
    instruments, _ = getTieredInstruments(tier)
    paramSNRs = []
    
    # iterating through the instruments
    # for instrument in instruments:
    for i in prange(len(instruments)):
        instrument = instruments[i]
        # average SNR only depends on NIRSpec, AIRS CH0, and AIRS CH1
        if SNR_param.lower() in ["esm", "tsm", "full phase curve snr"]:
            if instrument not in ['VISPhot', 'FGS1', 'FGS2']:
                instrument = checkInstrument(instrument)
                planetdf = getPlanet(instrument.getParam(SNR_param, iterations=iterations, names=True), planet) # get the planet data for one observation
                snr_mean = planetdf.mean(numeric_only=True).tolist() # finding the mean SNR
                paramSNRs.extend(snr_mean) # adding the mean SNR to the list
                
        else:
            if instrument in ['VISPhot', 'FGS1', 'FGS2']:
                instrument = checkInstrument(instrument)
                planetdf = getPlanet(instrument.getParam(SNR_param, iterations=iterations, names=True), planet) # get the planet data for one observation
                snr_mean = planetdf.mean(numeric_only=True).tolist() # finding the mean SNR
                paramSNRs.extend(snr_mean) # adding the mean SNR to the list
    
    return sum(paramSNRs)/len(paramSNRs) # returning the average SNR

def __avgFlux(planet:str, flux_param:str)->float:
    # getting instruments based on the tier
    instruments, _ = getTieredInstruments('tier 1')
    paramFluxes = []
    
    # iterating through the instruments
    # for instrument in instruments:
    for i in prange(len(instruments)):
        instrument = instruments[i]
        # average SNR only depends on NIRSpec, AIRS CH0, and AIRS CH1
        if flux_param in ["Eclipse Flux Ratio", "Transit Flux Ratio"]:
            if instrument not in ['VISPhot', 'FGS1', 'FGS2']:
                instrument = checkInstrument(instrument)
                planetdf = getPlanet(instrument.getParam(flux_param, names=True), planet)
                flux_mean = planetdf.mean(numeric_only=True).tolist()
                paramFluxes.extend(flux_mean)
        else:
            if instrument in ['VISPhot', 'FGS1', 'FGS2']:
                instrument = checkInstrument(instrument)
                planetdf = getPlanet(instrument.getParam(flux_param, names=True), planet)
                flux_mean = planetdf.mean(numeric_only=True).tolist()
                paramFluxes.extend(flux_mean)
        
    return sum(paramFluxes)/len(paramFluxes)
                

# @jit(parallel=True)
def findTierObservations(planet:str, tier:int, SNR_param:str, avg_SNR:float=7)->tuple[int, float]:
    if type(tier) in [int, float]:
        tier = f'tier {tier}'
            
    # finding the average SNR for the given tier for a single observation
    single_obs_SNR = __avgSNR(planet, tier, SNR_param, iterations=1)
    
    # finding the number of observations required to get SNR>=avg_SNR
    observations = np.ceil((avg_SNR / single_obs_SNR)**2)
    
    # finding the final SNR for the given number of observations
    finalSNR = __avgSNR(planet, tier, SNR_param, observations)
    
    # iterating until the final SNR is greater than or equal to the average SNR (if not already). Should NOT happen, only for safety.
    while finalSNR < avg_SNR:
        print(f"Not enough observations to achieve SNR>={avg_SNR} for {SNR_param}. Current SNR={finalSNR} for planet {planet}. Adding one more observation.")
        observations += 1
        finalSNR = __avgSNR(planet, tier, SNR_param, observations)
        
    return observations, finalSNR


def __avgTdayunc(planet:str, tier:str)->float:
    # getting instruments based on the tier
    instruments, _ = getTieredInstruments(tier)
    weights = []
    
    # iterating through the instruments
    # for instrument in instruments:
    for i in prange(len(instruments)):
        instrument = instruments[i]
        # average SNR only depends on NIRSpec, AIRS CH0, and AIRS CH1
        if instrument not in ['VISPhot', 'FGS1', 'FGS2']:
            instrument = checkInstrument(instrument)
            planetdf = getPlanet(instrument.getParam("Eclipse Dayside Temperature Uncertainty", names=True), planet) # get the planet data for one observation
            
            weights_df = planetdf.applymap(lambda x: 1/x**2 if isinstance(x, (int, float)) and pd.notnull(x) else 0)
            
            weighted_sum = weights_df.sum(axis=1)
            weights.append(weighted_sum)
            
    return np.sqrt(1/sum(weights)) if weights else None

def __avgAGunc(planet:str, tier:str)->float:
    # getting instruments based on the tier
    instruments, _ = getTieredInstruments(tier)
    weights = []
    
    # iterating through the instruments
    # for instrument in instruments:
    for i in prange(len(instruments)):
        instrument = instruments[i]
        # average SNR only depends on NIRSpec, AIRS CH0, and AIRS CH1
        if instrument in ['VISPhot', 'FGS1', 'FGS2']:
            instrument = checkInstrument(instrument)
            planetdf = getPlanet(instrument.getParam("Geometric Albedo Uncertainty", names=True), planet) # get the planet data for one observation
            
            weights_df = planetdf.applymap(lambda x: 1/x**2 if isinstance(x, (int, float)) and pd.notnull(x) else 0)
            
            weighted_sum = weights_df.sum(axis=1)
            weights.append(weighted_sum)
            
    return np.sqrt(1/sum(weights)) if weights else None

# def EWMean(planet:str, tier:str, SNR_param:str, flux_param:str, iterations:int):
#     instruments, _ = getTieredInstruments(tier)
    
#     for i in prange(len(instruments)):
#         inst = instruments[i]
#         if SNR_param.lower() in ["esm", "tsm", "full phase curve snr"]:
#             if inst not in ['VISPhot', 'FGS1', 'FGS2']:
#                 inst = checkInstrument(inst)
                
#                 SNRdf = inst.getParam(SNR_param, iterations=iterations, names=False)
#                 FLUXdf = inst.getParam(flux_param, names=False)
                
#                 precision_df = FLUXdf / SNRdf
                
#                 precision_df.applymap(lambda x: 1/x**2 if isinstance(x, (int, float)) and pd.notnull(x) else 0).sum(axis=1)
                
                
                
#                 planetdf = getPlanet(inst.getParam(SNR_param, iterations=iterations, names=True), planet)
#                 snr_mean = planetdf.mean(numeric_only=True).tolist()
    
#     # EWM precision
#     ewm_precision = np.sqrt(planetdf.applymap(lambda x: 1/x**2 if isinstance(x, (int, float)) and pd.notnull(x) else 0).sum(axis=1)

# def EclipsePrecisionEWM(tier:str):
#     instruments, _ = getTieredInstruments(tier)
#     precision = []
    
#     param_df = pd.DataFrame()
#     for i in prange(len(instruments)):
#         instrument = instruments[i]
#         if instrument not in ['VISPhot', 'FGS1', 'FGS2']:
#             instrument = checkInstrument(instrument)
#             param_df = pd.concat([param_df, instrument.getParam("Eclipse SNR", iterations=1, names=False)], axis=1)
            
#     precision = list((1/instrument.getParam("Eclipse SNR", iterations=1, names=False)**2).values)
            
#     for i in range(len(precision)):
#         precision[i] = np.sqrt(1/precision[i].sum())
    
#     return precision

# def EclipseMappingPrecisionEWM(tier:str):
#     instruments, _ = getTieredInstruments(tier)
#     precision = []
    
#     param_df = pd.DataFrame()
#     for i in prange(len(instruments)):
#         instrument = instruments[i]
#         if instrument not in ['VISPhot', 'FGS1', 'FGS2']:
#             instrument = checkInstrument(instrument)
#             param_df = pd.concat([param_df, instrument.getParam("Eclipse Mapping SNR", iterations=1, names=False)], axis=1)
            
#     precision = list((1/instrument.getParam("Eclipse Mapping SNR", iterations=1, names=False)**2).values)
                
#     for i in range(len(precision)):
#         precision[i] = np.sqrt(1/precision[i].sum())
    
#     return precision    

# constructing the observation table
# @animated_coffee
def constructObservationTable(target_list_title:str=None, show:bool=False):
    global target_list
    global target_list_name
    
    if target_list_title is not None:
        setTargetList(target_list_title)
    
    target_list_name, target_list = getTargetList()
    
    if show:
        start_time = time.time()
        
    
    def calculate_observations(row, tier, param, avg_SNR):
        return pd.Series(findTierObservations(row["Planet Name"], tier, param, avg_SNR))
    
    # def calculate_avg_td_unc(row, ):
    
    for param in ["ESM", "TSM", "RSM"]: # Eclipse flux = PC flux
        for i, row in target_list.iterrows():
            target_list.loc[i, f"{param} Flux"] = __avgFlux(row["Planet Name"], param)
        # target_list[f"{param} Flux"] = target_list.apply(
        #             lambda x: __avgFlux(x["Planet Name"], param)
        #         )
    
    target_list["Relative Dayside Temperature Uncertainty Average"] = __avgTdayunc(target_list["Planet Name"], 'tier 1')
    target_list["Relative Geometric Albedo Uncertainty Average"] = __avgAGunc(target_list["Planet Name"], 'tier 1')
    target_list["Relative Phase Function Uncertainty Average"] = target_list["Relative Geometric Albedo Uncertainty Average"]
    
    for i in range(1,4):
        
        if show:
            tier_time_start = time.time()
            print(f"starting tier {i}")
            
        # target_list[f"Tier {i} Eclipse EWM Precision"] = EclipsePrecisionEWM(i)
        # target_list[f"Tier {i} Eclipse Mapping EWM Precision"] = EclipseMappingPrecisionEWM(i)
        
        for param in ["ESM", "TSM", "RSM", "Full Phase Curve SNR"]:
            if param == "RSM" and i > 1:
                continue # Reflected light signal-to-noise ratio is not tier dependent
            
            if show:
                snr_time_start = time.time()
                print(f"---- starting {param}", end=" ")
                
            avg_SNR = 10 if param == "Full Phase Curve SNR" else 7
                
            if param != "RSM":
                target_list[[f"Tier {i} Observations {param}", f"Tier {i} {param}"]] = target_list.apply(
                    lambda row: calculate_observations(row, i, param, avg_SNR), axis=1
                )
            
            else: # if param == RSM
                target_list[[f"Observations RSM", f"RSM"]] = target_list.apply(
                                lambda row: calculate_observations(row, i, param, avg_SNR), axis=1
                            )
            
            if show:
                snr_time_end = time.time()
                print(f" -- {snr_time_end - snr_time_start:.2f} seconds --")
        
        if show:
            tier_time_end = time.time()
            print(f"     ---> tier {i} took {tier_time_end - tier_time_start:.2f} seconds", end="\n\n")
            
            
        if show:
            param_start_time = time.time()
            print(f"starting parameter uncertainty calculations, ")
        
        # finding uncertainties
        # target_list[f"Geometric Albedo Uncertainty"] = target_list.apply(
        #     lambda x: 1/x["RSM"], axis=1
        # )
        
        # target_list[f"Phase Function Uncertainty"] = target_list[f"Geometric Albedo Uncertainty"]
        
        # average eclipse dayside temperature uncertainty
        # target_list[f"Average Dayside Temperature Uncertainty * SNR"] = target_list.apply( 
        #     lambda x: Tdayunc(((1.1, 7.8)), x["Dayside Emitting Temperature [K]"], x["Star Temperature [K]"], x["Star Radius [Rs]"], 
        #                         x["Planet Radius [Rjup]"], x["ESM Flux"]), axis=1
        # )
        
        # target_list[f"Average Eclipse Dayside Temperature Uncertainty"] = target_list.apply( 
        #     lambda x: x["Average Dayside Temperature Uncertainty * SNR"] / x[f"Tier 1 ESM"], axis=1
        # )
        
        # target_list[f"Average Full Phase Curve Dayside Temperature Uncertainty"] = target_list.apply( 
        #     lambda x: x["Average Dayside Temperature Uncertainty * SNR"] / x[f"Tier 1 Full Phase Curve SNR"], axis=1
        # )
        
        # target_list[f"Tier {i} Average Full Phase Curve Dayside Temperature Uncertainty"] = target_list.apply( 
        #     lambda x: x["Average Dayside Temperature Uncertainty"] / x[f"Full Phase Curve SNR"], axis=1
        # )
            

        # target_list[f"Tier {i} Dayside Temperature Uncertainty * Dayside Temperature"] = target_list.apply(
        #     lambda x: , axis=1
        # )

    # saving target list
    ariel_observation_path = setPath(cur_dir + f'/Ariel Observations/{target_list_name}')
    target_list.to_parquet(f"{ariel_observation_path}_ObservationTable.parquet", index=False)
    
    if show:
        end_time = time.time()
        print(f"\n-> total time: {end_time - start_time:.2f} seconds", end="\n\n")
        
        
# get the observation table
def getObservationTable(target_list_name:str=target_list_name):
    ariel_observation_path =  f'{cur_dir}/Ariel Observations/{target_list_name}_ObservationTable.parquet'
    
    if not os.path.exists(ariel_observation_path):
        raise ValueError(f"Observation table for {target_list_name} does not exist. Construct the table first.")
    
    obs_table = pd.read_parquet(f"{ariel_observation_path}")
    try:
        obs_table = obs_table.loc[:, ~obs_table.columns.str.contains('^Unnamed')] # removing unnamed columns
    except:
        pass
    return obs_table



# plotting the parameter profile of the instrument(s) provided
def plotParamProfile(planet:str, instruments:list[str], param:str, wavelength:float=None, iterations=1, target_list_name=target_list_name, ax:plt.Axes=None, label:str=None, 
                     return_data:bool=False, ppm:bool=None, factor:float=1.0, **kwargs):
    """
    Plot the parameter profile for a given planet and parameter using multiple instruments.

    Parameters:
    planet (str): The name of the planet.
    instruments (list[str] or list[Telescope]): A list of instrument names or Telescope objects.
    param (str): The parameter to plot.
    wavelength (float, optional): The wavelength of the observation. Defaults to None.
    iterations (int, optional): The number of iterations. Defaults to 1.
    ax (matplotlib.axes.Axes, optional): The Axes object to plot on. If not provided, a new figure and Axes will be created. Defaults to None.
    label (str, optional): The label for the plot. If not provided, the parameter name will be used. Defaults to None.
    **kwargs: Additional keyword arguments for the plot function.

    Raises:
    ValueError: If instruments are not a list of strings or Telescope objects.

    Returns:
    None
    """

    # check if ax is provided
    if ax is None:
        _, ax = plt.subplots()
    
        
    wavelengths = np.array([])
    param_data = np.array([])
        
    # checl if tier is provided
    if type(instruments)==str:
        if 'tier' in instruments.lower().replace(" ", ""):
            instruments, _ = getTieredInstruments(instruments)
        else:
            instruments = [instruments]

    # check if instruments are strings or Telescope objects
    for i, instrument in enumerate(instruments):
        if type(instrument) == str:
            instrument = getInstrument(instrument, target_list_name)
        elif type(instrument) != Telescope:
            raise ValueError("instruments must be a list of strings or Telescope objects")
            
        # plot the parameter profile on Axes
        w, p = instrument.plotParam(planet, param, wavelength, iterations=iterations, plot=False, ppm=ppm, factor=factor)
        wavelengths = np.append(wavelengths, w)
        param_data = np.append(param_data, p)
        
        
    # check if label is provided
    if label is None:
        label = param
    
    # plotting
    plot = ax.plot(wavelengths, param_data, label=label, **kwargs)
    
    if return_data:
        return plot
    return None
    

def templateProfile(planet:str, instruments:list[str], params:list[str], colors:list[str], markers:list[str], linestyles:list[str], 
                    linewidths:list[float], alphas:list[float], main_title:str, iterations:int=1,
                    ax:plt.Axes=None, xscale='log', yscale='log', label_range_on_plot:bool=True, 
                    trim_plot:bool=True, trim_param:str="Noise Estimate", trim_amount:float=10):

    # check if ax is provided
    if ax is None:
        fig, ax = plt.subplots(figsize=(9,6))
        
    # setting scales
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    
    # check if instruments are strings or Telescope objects
    tier = None
    if type(instruments)==str:
        if 'tier' in instruments.lower().replace(" ", ""):
            instruments, tier = getTieredInstruments(instruments)
        else:
            instruments = [instruments]
        
    # setting title
    title = f"{planet} {main_title}"
    if tier is not None:
        title += f"\nat {tier} Spectral Resolution"
    # if iterations is not provided, set it to 1
    if iterations == 1:
        title += " with 1 Occultation"
    elif type(iterations) in [int, float] and iterations >= 1:
        iterations = int(iterations)
        title += " with " + str(iterations) + " Occultations"
    else:
        raise ValueError("Iterations must be an integer greater than or equal to 1")
    ax.set_title(title, fontsize=14)

    # Plotting the parameter profiles
    trim_data = None
    for param, color, marker, linestyle, linewidth, alpha in zip(params, colors, markers, linestyles, linewidths, alphas):
        if param == trim_param:
            trim_data = plotParamProfile(planet, instruments, param, iterations=iterations, ax=ax, color=color,
                                     linestyle=linestyle, linewidth=linewidth, marker=marker, alpha=alpha,
                                     return_data=True)
        else:
            plotParamProfile(planet, instruments, param, iterations=iterations, ax=ax, color=color,
                            linestyle=linestyle, linewidth=linewidth, marker=marker, alpha=alpha,
                            return_data=False)
    
    # trimming
    if trim_plot and trim_data is not None:
        minimum = trim_data[0].get_ydata().min()
        ax.set_ylim(minimum/trim_amount)
    
    # plotting ranges
    plotSensitivityRange(instruments, ax=ax, label_on_plot=label_range_on_plot)

    # setting x-tick label padding
    if label_range_on_plot:
        ax.tick_params(axis='x', pad=10)

    # setting labels
    ax.set_xlabel("Wavelength ($\mu m$)", fontsize=11)
        
    return ax, title
   

        
def plotPrecisionProfile(planet:str, instruments:list[str]='tier 1', iterations:int=1,
                         ax:plt.Axes=None, xscale='log', yscale='log',
                         params = ["Noise Estimate", "Eclipse Flux", "Transit Flux", "Reflected Light Flux"],
                         colors = ["blue", "red", "green", "orange"],
                         markers = ["x", '.', '.', '.'],
                         linestyles = ["--", ":", ":", ":"],
                         linewidths = [.5, .5, .5, .5],
                         alphas = [1, 1, 1, 1],
                         show_legend:bool=True, legend_loc:str='best', label_range_on_plot:bool=True, default_save=False, 
                         trim_plot:bool=True, trim_param:str="Noise Estimate", trim_amount:float=10):   
    
    return_ax = False
    if ax is None:
        return_ax = True
    
    ax, title = templateProfile(planet, instruments, params, colors, markers, linestyles, linewidths, alphas, "Signal & Noise for Ariel Instruments", 
                              iterations, ax, xscale, yscale, label_range_on_plot=label_range_on_plot, 
                              trim_plot=trim_plot, trim_param=trim_param, trim_amount=trim_amount)

    # showing legend
    if show_legend:
        ax.legend(loc=legend_loc)

    # setting y label
    ax.set_ylabel("Precision (ppm)", fontsize=11)

    # saving fig
    if default_save:
        path = setPath(work_dir + "/Precision plots")
        plt.savefig(path + '/' + title.replace("\n", " "), bbox_inches='tight', dpi=300)
        
    if return_ax:
        return ax
    
    


def plotSNRProfile(planet:str, instruments:list[str]='tier 1', iterations:int=1, 
                    params = ["ESM", "TSM", "RSM"],
                    colors = ["red", "green", "orange"],
                    markers = ['.', '.', '.'],
                    linestyles = [":", ":", ":"],
                    linewidths = [.5, .5, .5],
                    alphas = [1, 1, 1],
                    ax:plt.Axes=None, xscale='log', yscale='log', show_legend:bool=True, legend_loc:str='best', 
                    default_save=False, plotSNR7:bool=True, label_range_on_plot:bool=True, 
                    trim_plot:bool=True, trim_param:str="Noise Estimate", trim_amount:float=10):
    
    return_ax = False
    if ax is None:
        return_ax = True
        
    # plotting SNR profiles
    ax, title = templateProfile(planet, instruments, params, colors, markers, linestyles, linewidths, alphas, "SNR for Ariel Instruments",
                                iterations, ax, xscale, yscale, label_range_on_plot=label_range_on_plot,
                                trim_plot=trim_plot, trim_param=trim_param, trim_amount=trim_amount)
    
    # Plotting the parameter profiles
    if plotSNR7:
        ax.axhline(7, color='black', linestyle='--', label='S/N=7', linewidth=1, alpha=.5)

    # setting legend
    if show_legend:
        ax.legend(loc=legend_loc)

    # setting y label
    ax.set_ylabel("Signal-to-Noise Ratio (SNR)", fontsize=11)

    # saving fig
    if default_save:
        path = setPath(work_dir + "/SN curve plots")
        plt.savefig(path + "/" + title.replace("\n", " "), bbox_inches='tight', dpi=300)
    
    if return_ax:
        return ax
        
        
        
def plotTieredPrecisionProfile(planet:str, ax:plt.Axes=None, xscale:str='log', yscale:str='log', 
                               flux_instruments:list[str]=["VISPhot", "FGS1", "FGS2", "NIRSpec R=20", "AIRS CH0 R=100", "AIRS CH1 R=100"],
                               show_legend:bool=True, legend_loc:str='best', default_save:bool=False,
                               flux_marker:str='', flux_linestyle:str='-', flux_linewidth:float=1, 
                               eclipse_color:str='red', transit_color:str='green', reflected_color:str='orange',
                               tier1_color:str='black', tier2_color:str='blue', tier3_color:str='purple',
                               tier1_linestyle:str='--', tier2_linestyle:str='--', tier3_linestyle:str='--',
                               tier1_linewidth:float=.5, tier2_linewidth:float=.5, tier3_linewidth:float=.5,
                               tier1_marker:str='.', tier2_marker:str='.', tier3_marker:str='.',
                               tier1_markersize:float=5, tier2_markersize:float=5, tier3_markersize:float=5, 
                               trim_plot:bool=True, trim_amount:float=10, observations:int=1):
    
    # check if ax is provided
    return_ax = False
    if ax is None:
        return_ax = True
        fig, ax = plt.subplots(figsize=(9,6))
    
    # setting x and y scales
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)

    # Plotting fluxes (doesn't really change from tier to tier)
    plotParamProfile(planet, flux_instruments, "Eclipse Flux", linestyle=flux_linestyle, linewidth=flux_linewidth, marker=flux_marker, ax=ax, color=eclipse_color, label='Eclipse Flux')
    plotParamProfile(planet, flux_instruments, "Transit Flux", linestyle=flux_linestyle, linewidth=flux_linewidth, marker=flux_marker, ax=ax, color=transit_color, label='Transit Flux')
    plotParamProfile(planet, flux_instruments, "Reflected Light Flux", linestyle=flux_linestyle, linewidth=flux_linewidth, marker=flux_marker, ax=ax, color=reflected_color, label='Reflected Light Flux')


    # plotting noise (what actually changes from tier to tier)
    trim_data = plotParamProfile(planet, 'tier 1', "Noise Estimate", iterations=observations, linestyle=tier1_linestyle, linewidth=tier1_linewidth, marker=tier1_marker, markersize=tier1_markersize, ax=ax, color=tier1_color, label='Noise at Tier 1 Spectral Resolution', return_data=True)
    plotParamProfile(planet, 'tier 2', "Noise Estimate", iterations=observations, linestyle=tier2_linestyle, linewidth=tier2_linewidth, marker=tier2_marker, markersize=tier2_markersize, ax=ax, color=tier2_color, label='Noise at Tier 2 Spectral Resolution')
    plotParamProfile(planet, 'tier 3', "Noise Estimate", iterations=observations, linestyle=tier3_linestyle, linewidth=tier3_linewidth, marker=tier3_marker, markersize=tier3_markersize, ax=ax, color=tier3_color, label='Noise at Tier 3 Spectral Resolution')
    
    # trimming
    if trim_plot and trim_data is not None:
        minimum = trim_data[0].get_ydata().min()
        ax.set_ylim(minimum/trim_amount)
    
    # plotting the sensitivity ranges for all instruments
    plotSensitivityRange(ax=ax, label_on_plot=True)    
    
    # setting x-tick label padding
    ax.tick_params(axis='x', pad=10)

    # legend
    if show_legend:
        ax.legend(loc=legend_loc)

    # title
    if observations == 1:
        title = f"{planet} Noise and Flux for Ariel at Different Tier\nSpectral Resolutions (Single Occultation)"
    else:
        title = f"{planet} Noise and Flux for Ariel at Different Tier\nSpectral Resolutions ({observations} Occultations)"
        
    ax.set_title(title, fontsize=14)

    # labels
    ax.set_xlabel("Wavelength ($\mu m$)", fontsize=11)
    ax.set_ylabel("Precision (ppm)", fontsize=11)

    # setting x-tick label padding
    ax.tick_params(axis='x', pad=10)

    # saving fig
    if default_save:
        path = setPath(work_dir + "/Tiered Precision Plots")
        plt.savefig(path + "/" + title.replace("\n", " "), bbox_inches='tight', dpi=300)
    
    if return_ax:
        return ax