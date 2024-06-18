import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import glob
import os
from Functions import *

## Getting current directory
cur_dir = os.path.dirname(os.path.realpath(__file__))


def replaceNanWithMean(dataframe:pd.DataFrame, column_name:str):
    dataframe[column_name] = dataframe[column_name].fillna(dataframe[column_name].mean()) # replace each nan value with the mean value
    
    
def setPath(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return path


class Telescope:
    """
    Represents a telescope used for astronomical observations.

    Args:
        name (str): The name of the telescope.
        diameter (float): The diameter of the telescope's primary mirror or lens in meters.
        wavelength_range (tuple): The range of wavelengths that the telescope can observe, specified as a tuple of two floats representing the minimum and maximum wavelengths in micrometers.
        resolution (int): The resolution of the telescope, which determines the number of wavelength intervals within the specified wavelength range.
        throughput (float): The throughput of the telescope, which represents the fraction of incident light that is transmitted through the telescope system.
        target_list (pd.DataFrame, optional): The target list for observations, provided as a pandas DataFrame. Defaults to the target list loaded from a CSV file.
        table (pd.DataFrame, optional): The table used for calculations, provided as a pandas DataFrame. Defaults to None.
        float_precision (int, optional): The precision used for rounding floating-point numbers. Defaults to 7.

    Attributes:
        name (str): The name of the telescope.
        diameter (float): The diameter of the telescope's primary mirror or lens in meters.
        wavelength_range (tuple): The range of wavelengths that the telescope can observe.
        resolution (int): The resolution of the telescope.
        throughput (float): The throughput of the telescope.
        target_list (pd.DataFrame): The target list for observations.
        table (pd.DataFrame or str): The table used for calculations. If None, it indicates that the table has not been constructed yet.
        float_precision (int): The precision used for rounding floating-point numbers.

    Methods:
        constructRanges(): Constructs the wavelength ranges based on the resolution.
        getColumns(column_name): Returns a list of column names in the table that contain the specified substring.
        constructTable(): Constructs the table by performing calculations based on the target list and wavelength ranges.
        getParam(param, wavelength=None): Returns the specified parameter from the table. If a wavelength is specified, returns the parameter value at that wavelength.

    Examples:
        # Create a telescope object
        telescope = Telescope("Hubble", 2.4, (0.1, 2.5), 100, 0.8)

        # Construct the wavelength ranges
        ranges = telescope.constructRanges()
        print(ranges)
        # Output: [(0.1, 0.124), (0.124, 0.148), (0.148, 0.172), (0.172, 0.196), ...]

        # Get the column names containing "flux ratio"
        columns = telescope.getColumns("flux ratio")
        print(columns)
        # Output: ['Eclipse Flux Ratio 0.1-0.03um', 'Transit Flux Ratio 0.13-0.15um', ...]

        # Construct the table
        telescope.constructTable()

        # Get the "ESM" parameter from the table
        esm_param = telescope.getParam("ESM")
        print(esm_param)
        # Output: A pandas DataFrame containing the "ESM" parameter values for each target in the table.

        # Get the "Transit Flux Ratio" parameter at a specific wavelength
        transit_flux_ratio = telescope.getParam("Transit Flux Ratio", 0.15)
        print(transit_flux_ratio)
        # Output: A pandas DataFrame containing the "Transit Flux Ratio" values at the specified wavelength for each target in the table.
    """

    target_list = pd.read_csv(os.path.dirname(os.path.realpath(__file__)) + "/target_lists/Ariel_MCS_Known_2024-03-27.csv")
    
    def __init__(self, name, diameter, wavelength_range, resolution, throughput, target_list:pd.DataFrame=target_list, table:pd.DataFrame=None, float_precision=7):
        self.name = name
        self.diameter = diameter
        self.wavelength_range = wavelength_range
        self.resolution = resolution
        self.throughput = throughput
        self.target_list = target_list
        self.float_precision = float_precision
        
        if table is not None:
            self.table = table
        else:
            self.table = "Run 'constructTable' method to build table."

    def constructRanges(self):
        while round((self.wavelength_range[1] - self.wavelength_range[0]), self.float_precision) == 0:
            self.precision += 1 # ensuring that precision is such that w1 - w2 != 0
            
        sep = (self.wavelength_range[1] - self.wavelength_range[0]) / (2*self.resolution)
        arr = []
        wall = self.wavelength_range[0]
        for i in range(self.resolution):
            new_wall = wall+2*sep
            arr.append(tuple([round(wall, self.float_precision), round(wall+2*sep, self.float_precision)]))
            wall = new_wall
        return arr
    
    # helper function
    def getColumns(self, column_name:str):
        return [x for x in self.table if column_name.lower() in x.lower()]
    
    
    
    def constructTable(self):
        self.table = self.target_list.copy() # for calculations
        
        # calculating the Tday
        self.table["Dayside Emitting Temperature [K]"] = self.table.apply(lambda x: Tday(x["Star Temperature [K]"], 
                                                                                        x["Star Radius [Rs]"],
                                                                                        x["Planet Semi-major Axis [au]"],
                                                                                        x["Planet Albedo"],
                                                                                        x["Heat Redistribution Factor"]),
                                                                        axis=1)
        
       
        arr = self.constructRanges() # getting wavelength ranges based on resolution
        replaceNanWithMean(self.table, "Transit Duration [hrs]") # replacing all NaN transit duration values with the mean value of the column
        
        for w_range in arr:
            # calculating the eclipse flux ratio
            self.table[f"Eclipse Flux Ratio {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: eclipseFlux(x["Planet Radius [Rjup]"],
                                                                                                                x["Star Radius [Rs]"],
                                                                                                                w_range,
                                                                                                                x["Dayside Emitting Temperature [K]"],
                                                                                                                x["Star Temperature [K]"]),
                                                                                            axis=1)
            
            # calculating the transit flux ratio
            self.table[f"Transit Flux Ratio {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: transitFlux(x["Planet Radius [Rjup]"],
                                                                                                                   x["Star Radius [Rs]"],
                                                                                                                   x["Planet Mass [Mjup]"],
                                                                                                                   x["Dayside Emitting Temperature [K]"],
                                                                                                                   x["Mean Molecular Weight"]),
                                                                                             axis=1)
            
            # calculating the reflected light flux
            self.table[f"Reflected Light Flux Ratio {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: reflectionFlux(x["Planet Radius [Rjup]"],
                                                                                                                              x["Planet Semi-major Axis [au]"],
                                                                                                                              x["Planet Albedo"]),
                                                                                                     axis=1)
            
            # calculating the noise
            self.table[f"Noise Estimate {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: noiseEstimate(x["Star Temperature [K]"],
                                                                                                                *w_range,
                                                                                                                self.throughput, 
                                                                                                                3*x["Transit Duration [hrs]"]*3600, # x3 Transit duration
                                                                                                                x["Star Radius [Rs]"],
                                                                                                                self.diameter,
                                                                                                                x["Star Distance [pc]"]),
                                                                                            axis=1)
            
            # calculating the full phase curve noise
            self.table[f"Full Phase Curve Noise Estimate {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: noiseEstimate(x["Star Temperature [K]"],
                                                                                                                                 *w_range,
                                                                                                                                 self.throughput, 
                                                                                                                                 x["Planet Period [days]"]*24*3600 + 3*x["Transit Duration [hrs]"]*3600, # Full period + x3 transit duration
                                                                                                                                 x["Star Radius [Rs]"],
                                                                                                                                 self.diameter,
                                                                                                                                 x["Star Distance [pc]"]),
                                                                                                           axis=1)
                
            # calculating the ESM
            self.table[f"ESM Estimate {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: x[f"Eclipse Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Noise Estimate {w_range[0]}-{w_range[1]}um"],
                                                                                        axis=1)
            
            
            # calculating the TSM
            self.table[f"TSM Estimate {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: x[f"Transit Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Noise Estimate {w_range[0]}-{w_range[1]}um"],
                                                                                       axis=1)
            
            # calculating the RSM
            self.table[f"RSM Estimate {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: x[f"Reflected Light Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Noise Estimate {w_range[0]}-{w_range[1]}um"],
                                                                                       axis=1)
            
            # calculating the SNR for full phase curves
            self.table[f"Full Phase Curve SNR {w_range[0]}-{w_range[1]}um"] = self.table.apply(lambda x: x[f"Eclipse Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Full Phase Curve Noise Estimate {w_range[0]}-{w_range[1]}um"],
                                                                                               axis=1)
            
        
        noiseDF = self.getParam("Noise Estimate")
        eclipseFluxDF = self.getParam("Eclipse Flux Ratio")
        transitFluxDF = self.getParam("Transit Flux Ratio")
        reflectionFluxDF = self.getParam("Reflected Light Flux Ratio")
        phaseFluxDF = self.getParam("Full Phase Curve Noise Estimate")
        esmDF = self.getParam("ESM")
        tsmDF = self.getParam("TSM")
        rsmDF = self.getParam("RSM")
        phaseSNRDF = self.getParam("Full Phase Curve SNR")
        
        # getting the path of this file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        # setting the path for all telescope data
        telescope_path = setPath(dir_path + f"/Telescopes/{self.name} {self.wavelength_range[0]}-{self.wavelength_range[1]}um D={self.diameter} R={self.resolution} tau={self.throughput}")
        
        # saving telescope data
        self.target_list.to_csv(telescope_path + "/Target List.csv")
        noiseDF.to_csv(telescope_path + "/Noise.csv")
        eclipseFluxDF.to_csv(telescope_path + "/Eclipse Flux.csv")
        transitFluxDF.to_csv(telescope_path + "/Transit FLux.csv")
        reflectionFluxDF.to_csv(telescope_path + "/Reflected Light Flux.csv")
        phaseFluxDF.to_csv(telescope_path + "/Full Phase Curve Noise.csv")
        esmDF.to_csv(telescope_path + "/ESM.csv")
        tsmDF.to_csv(telescope_path + "/TSM.csv")
        rsmDF.to_csv(telescope_path + "/RSM.csv")
        phaseSNRDF.to_csv(telescope_path + "/Full Phase Curve SNR.csv")
            
            
    
     # helper functions for getParam
    def __getSubRange(self, column_name):
        arr = column_name.split()[-1].replace('um', '').split('-')
        return [float(x) for x in arr]
        
    def __getValueAtWavelength(self, column_names, wavelength):
        for column in column_names:
            w_range = self.__getSubRange(column)
            if w_range[0] <= wavelength <= w_range[1]:
                return self.table[["Planet Name", column]]
        return None
    
    def __isIterable(self, obj):
        try: 
            iter(obj)
            return True
        except TypeError:
            return False
        
        
    # getParam method
    def getParam(self, param:str, wavelength=None, iterations=1, names=True):
        # returning pull table if no value(s) is/are specified
        if wavelength is None:
            temp_table = self.table[[*self.getColumns(param)]]
            
            if 'noise' in param.lower():
                temp_table = temp_table.apply(lambda x: x*(iterations)**(-.5), axis=1)
            elif param.lower() in ['esm', 'tsm', 'rsm']:
                temp_table = temp_table.apply(lambda x: x*(iterations)**(.5), axis=1)
            
            if names:
                return pd.concat([self.table[["Planet Name"]], temp_table], axis=1)
            else:
                return pd.concat([temp_table], axis=1)
        
        # returning table with specified wavelength value
        if type(wavelength) in [int, float]:
            value =  self.__getValueAtWavelength(self.getColumns(param), wavelength)
            if value is None:
                raise ValueError(f"Provided wavelength not in range for this telescope system. Range is {self.wavelength_range[0]} to {self.wavelength_range[1]} microns.")
            return value

        # returning table with specified wavelength range
        if self.__isIterable(wavelength):
            wavelength = sorted(wavelength)# sorting wavelength range
            table_columns = [] # list of column names in range of sensitivity
            for column in self.getColumns(param):
                w_range = self.__getSubRange(column)
                
                # checking if the range of sensitivity is within the desired range
                if wavelength[0] <= w_range[0] <= w_range[1] <= wavelength[-1]:
                    table_columns.append(column)
                    
                # additional check for boundary condition
                if w_range[0] <= wavelength[0] <= w_range[1] or w_range[0] <= wavelength[-1] <= w_range[1]:
                    table_columns.append(column)
            
            # error check (if desired range is not in range of sensitivity)
            if len(table_columns) == 0:
                raise ValueError(f"No columns found in range of sensitivity {self.wavelength_range[0]}-{self.wavelength_range[1]} microns.")
            return self.table[["Planet Name", *table_columns]]
            
        # if the function gets to here, than the input value is not valid
        raise ValueError("Wavelength must be of type None, a float (or int) or list-like with two elements of type float (or int).")


    ## --- Specific param methods --- ##
    def getNoise(self, wavelength=None, iterations=1, names=True):
        return self.getParam("Noise Estimate", wavelength, iterations, names=names)

    def getEFlux(self, wavelength=None, names=True):
        return self.getParam("Eclipse Flux Ratio", wavelength, names=names)

    def getTFlux(self, wavelength=None, names=True):
        return self.getParam("Transit Flux Ratio", wavelength, names=names)

    def getRFlux(self, wavelength=None, names=True):
        return self.getParam("Reflected Light Flux Ratio", wavelength, names=names)

    def getESM(self, wavelength=None, iterations=1, names=True):
        return self.getParam("ESM", wavelength, iterations, names=names)
    
    def getTSM(self, wavelength=None, iterations=1, names=True):
        return self.getParam("TSM", wavelength, iterations, names=names)
    
    def getRSM(self, wavelength=None, iterations=1, names=True):
        return self.getParam("RSM", wavelength, iterations, names=names)
    
    
    # list of planets
    def listPlanets(self):
        return list(self.table["Planet Name"])

    
    # plotting parameter
    def plotParam(self, planet:str, param:str, wavelength:float=None, iterations:float=1, ax:plt.Axes=None, marker:str='o', 
                  color:str=None, linestyle:str=None, label:str=None, ppm:bool=None, plot:bool=True):
        # Preparing arrays
        wavelengths = np.array([])
        param_data = np.array([])
        param_columns = self.getColumns(param)
        
        # validating param_columns (changing the noise columns depending on if it is for phase curves or not)
        if "phase" in param.lower():
            param_columns = [x for x in param_columns if "phase" in x.lower()]
        else:
            param_columns = [x for x in param_columns if "phase" not in x.lower()]
        
        # input validation for parameter
        if param_columns == []:
            raise ValueError(f"No columns found for parameter {param}.")
        
        # checking if parameter values should be in ppm or not
        if ppm is not None:
            if ppm:
                factor = 1e6
            else:
                factor = 1
        else:
            if param.lower()  in ["esm", "tsm", "rsm"]:
                factor = 1
            else:
                factor = 1e6
        
        # Adding data to arrays
        for column in param_columns:
            w_range = column.split()[-1].replace('um', '').split('-')
            wavelengths = np.append(wavelengths, round((float(w_range[1]) + float(w_range[0])) / 2, 5))
            param_data = np.append(param_data, factor * getPlanet(self.getParam(param, wavelength, iterations=iterations, names=True), planet)[column])
        
        # input validation for planet
        if len(param_data) == 0:
            raise ValueError(f"No data found for planet {planet}. Available planets are: {self.listPlanets()}")
            
        # plotting to Axes
        if plot:
            # making figure and Axes if not provided
            if ax is None:
                _, ax = plt.subplots()
            ax.plot(wavelengths, param_data, marker=marker, color=color, linestyle=linestyle, label=label)
            
        # or returns two arrays of data
        else:
            return wavelengths, param_data
    
    
## --- Retrieving telescope --- ##
def getTelescope(instrument_name:str, directory:str=cur_dir):
    def normalize_name(name):
        return sorted(name.lower().replace(".csv", "").replace("-", " ").split())
    
    telescope_dir = cur_dir + "/Telescopes"
    dir_list = os.listdir(telescope_dir)
    
    normalized_instrument_name = normalize_name(instrument_name)

    desired_telescope = ''
    for telescope in dir_list:
        normalized_telescope_name = normalize_name(telescope)

        is_in = all(word in normalized_telescope_name for word in normalized_instrument_name)
                
        if is_in:
            if desired_telescope != '':
                raise ValueError(f"Cannot find desired instrument. Note that this error is raised if the name is degenerate, in which case consider being more specific. The available instruments are in the following sorted list.\n\n {sorted(dir_list, key=str.lower)}")
            desired_telescope = telescope
            
    if desired_telescope == '':
        raise ValueError(f"No matching instrument found with '{instrument_name}'. Check spelling and the following sorted list of included instruments.\n\n {sorted(dir_list, key=str.lower)}")
    
    
    # getting all necessary parameters ready for making the telescope object
    diameter = float(desired_telescope.split("D=")[-1].split()[0]) # Diameter
    resolution = float(desired_telescope.split('R=')[-1].split()[0]) # Resolution
    throughput = float(desired_telescope.split('tau=')[-1].split()[0]) # Throughput
    
    wavelength_range_str = desired_telescope.split('um')[0].split()[-1].split('-')
    wavelength_range = (float(wavelength_range_str[0]), float(wavelength_range_str[-1])) # Wavelength
    
    name = " ".join(desired_telescope.split('um')[0].split()[:-1])
    
    # Fetching the directory of the desired telescope
    sub_dir = os.path.join(telescope_dir, desired_telescope)
    
    # Fetching all CSV files in the directory
    csv_files = glob.glob(os.path.join(sub_dir, "*.csv"))
    # Combining CSV files into a single dataframe
    dfs = []
    for file in csv_files:
        df = pd.read_csv(file)
        dfs.append(df)
        
    # Table
    table = pd.concat(dfs, axis=1)
    table = table.iloc[:,~table.columns.duplicated()]
    try:
        table = table.loc[:, ~table.columns.str.contains('^Unnamed')] # removing unnamed columns
    except:
        pass
    
    # Target list
    target_list = pd.read_csv(os.path.join(sub_dir, "Target List.csv"))
    try:
        target_list = target_list.loc[:, ~target_list.columns.str.contains('^Unnamed')] # removing unnamed columns
    except:
        pass
    
    # Making the telescope object
    telescope = Telescope(name, diameter, wavelength_range, resolution, throughput, target_list, table)
    
    return telescope


## Get Planet from dataframe ##
def getPlanet(df:pd.DataFrame, planet:str, use_indexing:bool=False):
    try:
        if not use_indexing:
            planetdf = df[df["Planet Name"] == planet]
        
        else:
            # Ensure "Planet Name" is the index for faster lookups
            if df.index.name != "Planet Name":
                df = df.set_index("Planet Name")

            # Efficiently filter by planet name
            planetdf = pd.DataFrame(df.loc[planet])



    except KeyError:
        raise KeyError("Provided dataframe does not contain a column named 'Planet Name'. Be sure to set the getParam (or getNoise, getESM, getEFlux, etc) method's argument 'names' to True.")
    
    if planetdf.empty:
        raise ValueError(f"Planet '{planet}' not found in dataframe. Available planets are: {list(df['Planet Name'])}")
    else:
        return planetdf


# def plotNoise(df, system_name=None, fill_between=False, ax=None, savepath=None):
#     if system_name is None:
#         raise ValueError("Please include a system_name for title.")
    
#     if ax is None:
#         fig, ax = plt.subplots()
        
#     wavelengths = np.array([])
#     stds = np.array([])
#     means = np.array([])
#     noise_columns = getNoiseColumns(df)
#     for column in noise_columns:
#         w_range = column.split()[-1].replace('um', '').split('-')
        
#         wavelengths = np.append(wavelengths, round((float(w_range[1]) + float(w_range[0])) / 2, 3))
#         stds = np.append(stds, df[column].std())
#         means = np.append(means, df[column].mean())
        
#     if fill_between:
#         ax.fill_between(wavelengths, means-stds, means+stds, alpha=.3, zorder=3)
#         ax.scatter(wavelengths, means, marker='.', color='blue', zorder=3)
#     else:
#         ax.errorbar(wavelengths, means, yerr=stds, fmt='o', c='black', capsize=3, zorder=3)
        
#     ax.set_ylabel("Noise Estimate")
#     ax.set_xlabel("Wavelength [microns]")
    
#     ax.grid(which="major", alpha=.4, zorder=0)
#     ax.grid(which="minor", alpha=.1, linestyle="-.", zorder=0)
#     ax.minorticks_on()
    
#     senstivity_range = getRange(df)
#     title=f"Noise Estimates at Various Wavelengths\n{system_name}, {senstivity_range[0]}-{senstivity_range[1]} $\mu m$, R={len(noise_columns)})"
#     ax.set_title(title)
    
#     if savepath is not None:
#         plt.savefig(savepath + "/" + title.replace("\n", " ").replace("$\mu m$", "microns") + ".png", bbox_inches='tight', dpi=300)
        


