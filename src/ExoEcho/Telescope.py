import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
from scipy import integrate
import os
# from .Functions import *
# from .ConversionUI import create_window
from Functions import *
from ConversionUI import create_window

# import tkinter as tk
# from tkinter import ttk, messagebox, font, filedialog
# from thefuzz import process




## Getting current directory
cur_dir = os.path.dirname(os.path.realpath(__file__))
telescopes = cur_dir + "/Telescopes/"
target_lists = cur_dir + "/target_lists/"

# Default target list
default_target_list_name = "Ariel_MCS_Known_2024-03-27"
target_list_name = default_target_list_name
target_list_changed = False

default_target_list = pd.read_csv(cur_dir + f"/target_lists/{default_target_list_name}.csv")
target_list = pd.read_csv(cur_dir + f"/target_lists/{target_list_name}.csv")


def setTargetList(targets_name:str=default_target_list_name):
    global target_list_name
    global target_list
    global target_list_changed
    
    if targets_name is None:
        targets_name = default_target_list_name
    
    target_list_name = targets_name
    target_list = pd.read_csv(cur_dir + f"/target_lists/{target_list_name}.csv")
    
    # updating current target file
    targetfile = pd.read_csv(cur_dir + f"/CurrentTargetList.csv")
    targetfile["current"] = target_list_name
    targetfile.to_csv(cur_dir + f"/CurrentTargetList.csv", index=False)
    
    updateTargetList()
    
    target_list_changed = True
    
def updateTargetList(target_df_name=None, target_df=None):
    global target_list_name
    global target_list
    global target_list_changed
    
    if target_df is not None and target_df_name is not None:
        target_list_name = target_df_name
        target_list = target_df
        target_list_changed = True
    
    df = pd.read_csv(cur_dir + f"/CurrentTargetList.csv")
    current = df["current"][0]
    
    if current is None or current == "None" or pd.isnull(current):
        df["current"] = df["default"]
    
    if current != target_list_name:
        target_list_name = current
        target_list = pd.read_csv(cur_dir + f"/target_lists/{target_list_name}.csv")
        target_list_changed = True
    
    
def getTargetList():
    if __name__ == '__main__':
        updateTargetList()
    df = pd.read_csv(cur_dir + f"/CurrentTargetList.csv")
    lst = df["current"][0]
    return lst, pd.read_csv(cur_dir + f"/target_lists/{lst}.csv")



def replaceNanWithMean(dataframe:pd.DataFrame, column_name:str):
    dataframe[column_name] = dataframe[column_name].fillna(dataframe[column_name].mean()) # replace each nan value with the mean value
    
    
def setPath(path:str):
    """Returns the input path. Creates it if it does not exist.

    Args:
        path (str): path

    Returns:
        str: path (created if it does not exist)
    """
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def openInstruments(telescope:str=None, target_list:str=None, show:bool=False):
    full_dict = {}
    
    # if show:
    #     print("________________________________________________________________\n"+
    #           "Opening all instruments into dictionary object 'instruments'...\n")
    
    for tel in sorted(os.listdir(telescopes), key=str.lower):
        if telescope is None or telescope == tel:
        
            if show:
                print(tel)
                
            target_list_path = telescopes + tel + "/"
            telescope_dict = {}
            for targets in sorted(os.listdir(target_list_path), key=str.lower):
                if target_list is None or target_list == targets:
                    
                    if show:
                        print(f"  |--> {targets}")
                        
                    instrument_path = target_list_path + targets + "/"
                    target_list_dict = {}
                    for instrument in sorted(os.listdir(instrument_path), key=str.lower):
                        if show:
                            print(f"             |--> {instrument}")
                        target_list_dict[instrument] = getTelescope(instrument, targets)
                    telescope_dict[targets] = target_list_dict
                
                
            full_dict[tel] = telescope_dict
        
    if show:
        print("________________________________________________________________\n")
        
    return full_dict



# class TelescopeList():
#     def __init__(self, name:str, key:str, values:list):
#         self.name = name
#         self.key = key
#         self.values = values
        
#     def nestedTelescopeList(self):
#         for 
        
    

# @jitclass
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
    
    def __init__(self, name, diameter, wavelength_range, resolution, throughput, target_list:pd.DataFrame=None, 
                 target_list_name:str=None, table:pd.DataFrame=None, float_precision=7):
        
        self.name = name
        self.diameter = diameter
        self.wavelength_range = wavelength_range
        self.resolution = resolution
        self.throughput = throughput
        self.target_list = target_list
        self.float_precision = float_precision
        
        self.target_list_dir = os.path.dirname(os.path.realpath(__file__)) + "/target_lists/"
        self.target_list_name = target_list_name
        self.target_list = target_list
        
        if self.target_list_name is None:
            self.target_list_name = default_target_list_name
            print(f"No target list name provided. Loading default target list: {self.target_list_name}. Use 'setTargetList' method to change target list.")
        # running setTargetList method to load target list
        self.setTargetList() 
        
        if table is not None:
            self.table = table
        else:
            self.table = "Run 'constructTable' method to build table."
            
            
        self.__vCalculateParams__ = np.vectorize(self.__calculateParams__, signature='(n)->()') # vectorizing the calculateParams method for faster calculations
            
    
    def setTargetList(self):
        # loading target list
        if self.target_list is None:
            try:
                self.target_list = pd.read_csv(f"{self.target_list_dir}{self.target_list_name}.csv")
                self.target_list = self.target_list.loc[:, ~self.target_list.columns.str.contains('^Unnamed')] # removing unnamed columns
            except FileNotFoundError:
                raise FileNotFoundError(f"Target list {target_list_name}.csv not found in the target_lists directory. Please choose an available target list or add a custom one directly as a target_list argument (should be a pd.DataFrame object).")
            except:
                raise ValueError("An error occurred while trying to load the target list. Please ensure that the target list is in the correct format and that the file exists.")
        
        elif self.target_list_name is not None: # if target list is provided, check if it is in the target_lists directory
            custom_counter = 0
            for filename in os.listdir(self.target_list_dir):
                if filename.endswith(".csv"):
                    if filename == f"{self.target_list_name}.csv":
                        self.target_list_name = filename.split(".csv")[0]
                    if "Custom Target List" in filename:
                        custom_counter += 1
                    break
                if self.target_list_name is None:
                    self.target_list_name = f"Custom Target List {custom_counter}".replace(' 0', '')
                    self.target_list.to_csv(self.target_list_dir + self.target_list_name + ".csv")
                    
                self.target_list = target_list
    
    
    def __str__(self):
        return self.info()
            
    def info(self):
        return f"Telescope: {self.name}\nDiameter: {self.diameter} m\nWavelength Range: {self.wavelength_range[0]} - {self.wavelength_range[1]} microns\nResolution: {self.resolution}\nThroughput: {self.throughput}\nTarget List: {self.target_list_name}"

    def constructRanges(self):
        while round((self.wavelength_range[1] - self.wavelength_range[0]), self.float_precision) == 0:
            self.precision += 1 # ensuring that precision is such that w1 - w2 != 0
            
        sep = (self.wavelength_range[1] - self.wavelength_range[0]) / (2*self.resolution)
        arr = []
        wall = self.wavelength_range[0]
        for i in range(self.resolution):
            new_wall = wall+2*sep
            arr.append(np.array([round(wall, self.float_precision), round(wall+2*sep, self.float_precision)]))
            wall = new_wall
        return arr
    
    # helper function
    def getColumns(self, column_name:str):
        if 'phase curve' not in column_name.lower():
            return [x for x in self.table if column_name.lower() in x.lower() and 'phase curve' not in x.lower()]
        
        # if 'noise' == column_name.lower().split()[0]:
        #     return [x for x in self.table if column_name.lower().split()[0] == x.lower().split()[0]]
        return [x for x in self.table if column_name.lower() in x.lower()]
            
        
    
    def __calculateParams__(self, w_range): #pass in the array containing all w_ranges to the vectorized function.
        w_range = pd.Series(self.table.shape[0] * [w_range])
        w_range_name = f"{w_range[0][0]}-{w_range[0][1]}um"
        # calculating the eclipse flux ratio
        self.table[f"Eclipse Flux Ratio {w_range_name}"] = v_eclipseFlux(self.table["Planet Radius [Rjup]"],
                            self.table["Star Radius [Rs]"],
                            w_range,
                            self.table["Dayside Emitting Temperature [K]"],
                            self.table["Star Temperature [K]"])
        
        # calculating the transit flux ratio
        self.table[f"Transit Flux Ratio {w_range_name}"] = v_transitFlux(self.table["Planet Radius [Rjup]"],
                                                self.table["Star Radius [Rs]"],
                                                self.table["Planet Mass [Mjup]"],
                                                self.table["Dayside Emitting Temperature [K]"],
                                                self.table["Mean Molecular Weight"])
        
        # calculating the reflected light flux
        self.table[f"Reflected Light Flux Ratio {w_range_name}"] = v_reflectionFlux(self.table["Planet Radius [Rjup]"],
                                                        self.table["Planet Semi-major Axis [au]"],
                                                        self.table["Planet Albedo"])
        
        # calculating the noise
        self.table[f"Noise Estimate {w_range_name}"] = v_noiseEstimate(self.table["Star Temperature [K]"],
                                                w_range,
                                                self.throughput, 
                                                3*self.table["Transit Duration [hrs]"]*3600, # x3 Transit duration
                                                self.table["Star Radius [Rs]"],
                                                self.diameter,
                                                self.table["Star Distance [pc]"])
        
        # calculating the full phase curve noise
        self.table[f"Full Phase Curve Noise Estimate {w_range_name}"] = v_noiseEstimate(self.table["Star Temperature [K]"],
                                                    w_range,
                                                    self.throughput, 
                                                    self.table["Planet Period [days]"]*24*3600 + 3*self.table["Transit Duration [hrs]"]*3600, # Full period + x3 transit duration
                                                    self.table["Star Radius [Rs]"],
                                                    self.diameter,
                                                    self.table["Star Distance [pc]"])
        
        # try:
        #     self.table[f"T12_Noise {w_range_name}"] = v_noiseEstimate(self.table["Star Temperature [K]"],
        #                                                                 w_range,
        #                                                                 self.throughput,
        #                                                                 self.table["Transit Duration T12 [s]"],
        #                                                                 self.table["Star Radius [Rs]"],
        #                                                                 self.diameter,
        #                                                                 self.table["Star Distance [pc]"]
        #     )
        # except:
        #     self.table[f"T12_Noise {w_range_name}"] = 0
            
        # calculating the ESM
        self.table[f"ESM Estimate {w_range_name}"] = self.table[f"Eclipse Flux Ratio {w_range_name}"] / self.table[f"Noise Estimate {w_range_name}"]
        
        # try:
        #     self.table[f"Eclipse Mapping SNR {w_range_name}"] = self.table[f"Eclipse Flux Ratio {w_range_name}"] / self.table[f"T12_Noise {w_range_name}"]
        # except:
        #     self.table[f"Eclipse Mapping SNR {w_range_name}"] = 0
            
        # calculating the TSM
        self.table[f"TSM Estimate {w_range_name}"] = self.table[f"Transit Flux Ratio {w_range_name}"] / self.table[f"Noise Estimate {w_range_name}"]
        
        # calculating the RSM
        self.table[f"RSM Estimate {w_range_name}"] = self.table[f"Reflected Light Flux Ratio {w_range_name}"] / self.table[f"Noise Estimate {w_range_name}"]
        
        # calculating the SNR for full phase curves
        self.table[f"Full Phase Curve SNR {w_range_name}"] = self.table[f"Eclipse Flux Ratio {w_range_name}"] / self.table[f"Full Phase Curve Noise Estimate {w_range_name}"]

        # geometric albedo uncertainty
        self.table[f"Geometric Albedo Uncertainty {w_range_name}"] = 1 / self.table[f"RSM Estimate {w_range_name}"]
        
        # phase function uncertainty
        self.table[f"Phase Function Uncertainty {w_range_name}"] = self.table[f"Geometric Albedo Uncertainty {w_range_name}"]
        
        # dayside temperature uncertainties
        self.table[f"Dayside Temperature Uncertainty x SNR {w_range_name}"]  = v_Tdayunc(w_range, 
                                                                                           self.table["Dayside Emitting Temperature [K]"],
                                                                                           self.table["Star Temperature [K]"],
                                                                                           self.table["Star Radius [Rs]"],
                                                                                           self.table["Planet Radius [Rjup]"],
                                                                                           self.table[f"Eclipse Flux Ratio {w_range_name}"])
        
        self.table[f"Eclipse Dayside Temperature Uncertainty {w_range_name}"]  = self.table[f"Dayside Temperature Uncertainty x SNR {w_range_name}"] / self.table[f"ESM Estimate {w_range_name}"]
        self.table[f"Full Phase Curve Dayside Temperature Uncertainty {w_range_name}"] = self.table[f"Dayside Temperature Uncertainty x SNR {w_range_name}"] / self.table[f"Full Phase Curve SNR {w_range_name}"]
        

    def constructTable(self):
        self.table = self.target_list.copy() # for calculations
        
        # calculating the Tday
        self.table["Dayside Emitting Temperature [K]"] = Tday(self.table["Star Temperature [K]"], 
                                                                self.table["Star Radius [Rs]"],
                                                                self.table["Planet Semi-major Axis [au]"],
                                                                self.table["Planet Albedo"],
                                                                self.table["Heat Redistribution Factor"])
        
        self.target_list["Dayside Emitting Temperature [K]"] = self.table["Dayside Emitting Temperature [K]"]
        self.target_list.to_csv(self.target_list_dir + self.target_list_name + ".csv")
        
       
        arr = self.constructRanges() # getting wavelength ranges based on resolution
        
        # fixing Transit Duration
        self.table.rename(columns={"Transit Duration [hr]": "Transit Duration [hrs]"}, inplace=True)
        replaceNanWithMean(self.table, "Transit Duration [hrs]") # replacing all NaN transit duration values with the mean value of the column
        
        self.__vCalculateParams__(arr)  
        
        
        eclipse_flux_col = self.table.filter(like="Eclipse Flux Ratio")
        self.table["Average Eclipse Flux Ratio"] = eclipse_flux_col.mean(axis=1)
        
        ESM_col = self.table.filter(like="ESM Estimate")
        self.table["Average ESM Estimate"] = ESM_col.mean(axis=1)
        
        FPC_snr_col = self.table.filter(like="Full Phase Curve SNR")
        self.table["Average Full Phase Curve SNR"] = FPC_snr_col.mean(axis=1)
        
        
        tdayDF = self.getParam("Dayside Emitting Temperature [K]")
        noiseDF = self.getParam("Noise Estimate")
        # t12noiseDF = self.getParam("T12_Noise")
        eclipseFluxDF = self.getParam("Eclipse Flux Ratio")
        transitFluxDF = self.getParam("Transit Flux Ratio")
        reflectionFluxDF = self.getParam("Reflected Light Flux Ratio")
        phaseFluxDF = self.getParam("Full Phase Curve Noise Estimate")
        esmDF = self.getParam("ESM")
        # t12esmDF = self.getParam("T12_ESM")
        tsmDF = self.getParam("TSM")
        rsmDF = self.getParam("RSM")
        phaseSNRDF = self.getParam("Full Phase Curve SNR")
        
        geoAlbedoUnc = self.getParam("Geometric Albedo Uncertainty")
        phaseFuncUnc = self.getParam("Phase Function Uncertainty")
        ESMtdunc = self.getParam("Eclipse Dayside Temperature Uncertainty")
        FPCtdunc = self.getParam("Full Phase Curve Dayside Temperature Uncertainty")
        
        # getting the path of this file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        
        # setting the path for all telescope data
        telescope_path = setPath(dir_path + f"/Telescopes/{self.name.split()[0]}/{self.target_list_name}/{self.name} {self.wavelength_range[0]}-{self.wavelength_range[1]}um D={self.diameter} R={self.resolution} tau={self.throughput}")
            
        # saving telescope data
        # self.target_list.to_parquet(telescope_path + "/Target List.parquet")
        tdayDF.to_parquet(telescope_path + "/Dayside Emitting Temperature [K].parquet")
        noiseDF.to_parquet(telescope_path + "/Noise.parquet")
        # t12noiseDF.to_parquet(telescope_path + "/T12_Noise.parquet")
        eclipseFluxDF.to_parquet(telescope_path + "/Eclipse Flux.parquet")
        transitFluxDF.to_parquet(telescope_path + "/Transit FLux.parquet")
        reflectionFluxDF.to_parquet(telescope_path + "/Reflected Light Flux.parquet")
        phaseFluxDF.to_parquet(telescope_path + "/Full Phase Curve Noise.parquet")
        esmDF.to_parquet(telescope_path + "/ESM.parquet")
        # t12esmDF.to_parquet(telescope_path + "/T12_ESM.parquet")
        tsmDF.to_parquet(telescope_path + "/TSM.parquet")
        rsmDF.to_parquet(telescope_path + "/RSM.parquet")
        phaseSNRDF.to_parquet(telescope_path + "/Full Phase Curve SNR.parquet")
        
        geoAlbedoUnc.to_parquet(telescope_path + "/Geometric Albedo Uncertainty.parquet")
        phaseFuncUnc.to_parquet(telescope_path + "/Phase Function Uncertainty.parquet")
        ESMtdunc.to_parquet(telescope_path + "/Eclipse Dayside Temperature Uncertainty.parquet")
        FPCtdunc.to_parquet(telescope_path + "/Full Phase Curve Dayside Temperature Uncertainty.parquet")
            
    
     # helper functions for getParam
    def __getSubRange(self, column_name):
        arr = column_name.split()[-1].replace('um', '').split('-')
        return [float(x) for x in arr]
        
    def __getValueAtWavelength(self, column_names, wavelength, planet_names=True):
        for column in column_names:
            w_range = self.__getSubRange(column)
            if w_range[0] <= wavelength <= w_range[1]:
                if planet_names:
                    return self.table[["Planet Name", column]]
                return self.table[[column]]
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
            
            if 'noise' in param.lower() or "uncertainty" in param.lower():
                temp_table *= (iterations ** (-0.5))
            elif param.lower() in ['esm', 'tsm', 'rsm', 'full phase curve snr']:
                temp_table *= (iterations ** 0.5)
            if names:
                return pd.concat([self.table[["Planet Name"]], temp_table], axis=1)
            else:
                return pd.concat([temp_table], axis=1)
        
        # returning table with specified wavelength value
        if type(wavelength) in [int, float]:
            value =  self.__getValueAtWavelength(self.getColumns(param), wavelength, planet_names=names)  
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
            
            if names:
                return self.table[["Planet Name", *table_columns]]
            return self.table[[*table_columns]]
            
        # if the function gets to here, than the input value is not valid
        raise ValueError("Wavelength must be of type None, a float (or int) or list-like with two elements of type float (or int).")


    ## --- Specific param methods --- ##
    def getNoise(self, wavelength=None, iterations=1, names=True):
        return self.getParam("Noise", wavelength, iterations, names=names)
    
    def getFPCNoise(self, wavelength=None, iterations=1, names=True):
        return self.getParam("Full Phase Curve Noise", wavelength, iterations, names=names)

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
    
    def getFPCSM(self, wavelength=None, iterations=1, names=True):
        return self.getParam("Full Phase Curve SNR", wavelength, iterations, names=names)
    
    
    # list of planets
    def listPlanets(self):
        return list(self.table["Planet Name"])

    
    # plotting parameter
    def plotParam(self, planet:str, param:str, wavelength:float=None, iterations:float=1, ax:plt.Axes=None, marker:str='o', 
                  color:str=None, linestyle:str=None, label:str=None, ppm:bool=None, factor:float=1.0, plot:bool=True):
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
                factor *= 1e6
            else:
                factor *= 1
        else:
            if param.lower()  in ["esm", "tsm", "rsm"]:
                factor *= 1
            else:
                factor *= 1e6
        
        # Adding data to arrays
        for column in param_columns:
            w_range = column.split()[-1].replace('um', '').split('-')
            if "um" not in column:
                if "average" in column.lower():
                    continue
                raise ValueError(f"Column {column} does not contain wavelength information.")
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
def normalize_name(name):
        return sorted(name.lower().replace(".csv", "").replace("-", " ").split())
    
    
def getTelescope(instrument_name:str, target_list_name:str=target_list_name, current_directory:str=cur_dir):
    
    # ensuring target_list_name is in the correct format
    target_list_name = target_list_name.replace(".csv", "")
    
    # Target list
    string = os.path.join(current_directory, "target_lists", f"{target_list_name}.csv")
    target_list = pd.read_csv(string)
    try:
        target_list = target_list.loc[:, ~target_list.columns.str.contains('^Unnamed')] # removing unnamed columns
    except:
        pass
    
    # getting the telescope
    try:
        telescope_dir = current_directory + f"/Telescopes/{instrument_name.split()[0]}/"
    except FileNotFoundError:
        raise FileNotFoundError(f"Telescope {instrument_name.split()[0]} not found in the Telescopes directory. Please choose an available telescope or add a custom one directly. Ensure that the first word for instrument name is the telescope name and is spaced from the rest of the words.\n"
                                + "Example: 'Ariel [instrument name]', or 'Hubble [instrument name]'. NOT -> '[instrument name] Ariel', or even 'Ariel[instrument name]."
                                + "\nAvailable telescopes are: " + str(os.listdir(current_directory + "/Telescopes")))
    except:
        raise ValueError("An error occurred while trying to load the telescope. Please ensure that the telescope is in the correct format and that the file exists.")
    
    # getting the target list for the telescope
    try:
        telescope_dir += f"{target_list_name}/"
    except FileNotFoundError:
        raise FileNotFoundError(f"Target list {target_list_name} not found in the Telescopes directory. Please choose an available target list or add a custom one directly."
                                + "/nAvailable target lists are: {os.listdir(current_directory + '/Telescopes')}")
    except:
        raise ValueError("An error occurred while trying to load the target list. Please ensure that the target list is in the correct format and that the file exists.")
    
    # getting telescope directory list
    dir_list = os.listdir(telescope_dir)
    
    normalized_instrument_name = normalize_name(instrument_name)

    desired_telescope = ''
    for telescope in dir_list:
        normalized_telescope_name = normalize_name(telescope)

        is_in = all(word in normalized_telescope_name for word in normalized_instrument_name)
        # is_in = check_all(normalized_telescope_name, normalized_instrument_name)
                
        if is_in:
            if desired_telescope != '':
                raise ValueError(f"Cannot find desired instrument. Note that this error is raised if the name is degenerate, in which case consider being more specific. The available instruments are in the following sorted list.\n\n {sorted(dir_list, key=str.lower)}")
            desired_telescope = telescope
            
    if desired_telescope == '':
        raise ValueError(f"No matching instrument found with '{instrument_name}'. Check spelling and the following sorted list of included instruments.\n\n {sorted(dir_list, key=str.lower)}")
    
    
    # getting all necessary parameters ready for making the telescope object
    diameter = float(desired_telescope.split("D=")[-1].split()[0]) # Diameter
    resolution = int(desired_telescope.split('R=')[-1].split()[0]) # Resolution
    throughput = float(desired_telescope.split('tau=')[-1].split()[0]) # Throughput
    
    wavelength_range_str = desired_telescope.split('um')[0].split()[-1].split('-')
    wavelength_range = (float(wavelength_range_str[0]), float(wavelength_range_str[-1])) # Wavelength
    
    name = " ".join(desired_telescope.split('um')[0].split()[:-1])
    
    # Fetching the directory of the desired telescope
    sub_dir = os.path.join(telescope_dir, desired_telescope)
    
    # Fetching all parquet files in the directory
    # pattern = os.path.join(sub_dir, "**/*.parquet")
    # files = glob.glob(pattern, recursive=True)
    files = os.listdir(sub_dir)
    # Combining parquet files into a single dataframe
    
    dfs = []
    dfs.append(target_list)
    for file in files:
        # print(file)
        if file.endswith(".parquet"):
            df = pd.read_parquet(f"{sub_dir}/{file}")
        dfs.append(df)
        
    if dfs == []:
        raise ValueError("No parquet files found in the directory. Please ensure that the directory contains the necessary files. Files in the directory are: " + str(os.listdir(sub_dir)))
        
    # Table
    table = pd.concat(dfs, axis=1)
    table = table.iloc[:,~table.columns.duplicated()]
    try:
        table = table.loc[:, ~table.columns.str.contains('^Unnamed')] # removing unnamed columns
    except:
        pass
 
    
    # adding SNRs to table
    # w_ranges = [x.split()[-1].replace("um", "").split('-') for x in table.columns if 'eclipse flux' in x.lower()]
    # for w_range in w_ranges:
    #     table[f"ESM Estimate {w_range[0]}-{w_range[1]}um"] = table.apply(lambda x: x[f"Eclipse Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Noise Estimate {w_range[0]}-{w_range[1]}um"],
    #                                                                             axis=1)
    #     table[f"TSM Estimate {w_range[0]}-{w_range[1]}um"] = table.apply(lambda x: x[f"Transit Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Noise Estimate {w_range[0]}-{w_range[1]}um"],
    #                                                                                 axis=1)
    #     table[f"RSM Estimate {w_range[0]}-{w_range[1]}um"] = table.apply(lambda x: x[f"Reflected Light Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Noise Estimate {w_range[0]}-{w_range[1]}um"],
    #                                                                                 axis=1)
    #     table[f"Full Phase Curve SNR {w_range[0]}-{w_range[1]}um"] = table.apply(lambda x: x[f"Eclipse Flux Ratio {w_range[0]}-{w_range[1]}um"] / x[f"Full Phase Curve Noise Estimate {w_range[0]}-{w_range[1]}um"],
    #                                                                                     axis=1)

    
    # Making the telescope object
    telescope = Telescope(name=name, diameter=diameter, wavelength_range=wavelength_range, resolution=resolution, 
                          throughput=throughput, target_list=target_list, target_list_name=target_list_name, table=table)
    
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
    
    
    
    
def saveTargetList(target_list:pd.DataFrame, target_list_name:str=target_list_name):
    target_list_dir = target_lists + target_list_name + ".csv"
    target_list.to_csv(target_list_dir)
    print(f"Target list '{target_list_name}' saved successfully at the following directory:\n{target_list_dir}")
    
    
    
def cleanTargetList(target_list, separate_errors=True):
    
    def getColumn(df, lst):
        if type(lst) == str:
            lst = lst.split()
            
        returnlst = []
        for x in df.columns:
            isIn = True
            for s in lst:
                if s not in x:
                    isIn = False
                    break
                    
            if isIn:
                returnlst.append(x)
        
        return returnlst
    
    def remove(string, chars):
        if type(string) == list:
            strings = []
            for s in string:
                strings.append(remove(s, chars))
            return strings
                
        for c in chars:
            string = string.replace(c, "")
        return string

    def getUnc(x):
        x = remove(str(x), ["\ast", "\\ast", "<", "\n"])
        
        if "−" in x:
            x = x.replace("−", "-")
        
        if x == "nan":
            return 0., 0., 0.
        
        elif "^" in x:
            xsplit = x.split("^")
            
            val = float(xsplit[0])
            uncs = remove(xsplit[1].split("_"), ["{", "}", "+", "-"])
            uncs = [float(uncs[0]), float(uncs[1])]
            
        elif "±" in x:
            xsplit = x.split("±")
            
            val = float(xsplit[0])
            uncs = [float(xsplit[1]), float(xsplit[1])]
            
        elif "+" in x and "-" in x:
            xsplit = x.split("+")
            
            val = float(xsplit[0])
            uncs = [float(xsplit[1].split("-")[0]), float(xsplit[1].split("-")[1])]
            
            # uncs = [float(x.split("+")[1]), float(x.split("-")[1])]
        
        else:
            val = float(x)
            uncs = [0., 0.]
            
        return val, *uncs
    
    
    cleandf = target_list.copy()

    if separate_errors:
        # separating columns with uncertainties
        for column in target_list.columns:
            if column not in ["Name", "Planet Name", "Star Name", "Reference", "Notes"]:
                cleandf.drop(column, axis=1, inplace=True)
                
                column_split = column.split(" ")
                if "[" in column_split[-1] or "(" in column_split[-1]:
                    column_name, column_units = " ".join(column_split[:-1]), column_split[-1]
                    upper_name = column_name + " Error Upper " + column_units
                    lower_name = column_name + " Error Lower " + column_units
                    cleandf[column], cleandf[upper_name], cleandf[lower_name], = 0., 0., 0.
                    
                else:
                    upper_name = column + " Error Upper"
                    lower_name = column + " Error Lower"
                    cleandf[column], cleandf[upper_name], cleandf[lower_name] = 0., 0., 0.
                
                value_i = 0
                first_value = str(target_list[column].values[value_i])
                while first_value == "nan" and value_i < len(target_list[column].values) - 1:
                    value_i += 1
                    first_value = str(target_list[column].values[value_i])

                
                if not first_value[0].isalpha():
                    for i, value in target_list[column].items():
                        if str(value) == "-":
                            value = "nan"
                        try:
                            cleandf.loc[i, column], cleandf.loc[i, upper_name], cleandf.loc[i, lower_name] = getUnc(value)
                        except:
                            continue
                        # clean_BD_df[column][i], clean_BD_df[column + " upper unc"][i], clean_BD_df[column + " lower unc"][i] = getUnc(value)
                
                # removing columns with no uncertainties
                if (cleandf[upper_name] == 0).all():
                    cleandf.drop(upper_name, axis=1, inplace=True)
                if (cleandf[lower_name] == 0).all():
                    cleandf.drop(lower_name, axis=1, inplace=True)
                
    return create_window(cleandf)
    
    
    # # printing column names
    # print("__________________\nCurrent Column names: \n")
    # for x in cleandf.columns:
    #     print(x)
    # print("__________________\n")
    
    
    # # fixing planet names
    # passed = False
    # while passed is False:
    #     passed = True
    #     name_column = input("What is the name of the column that contains the planet names? Press ENTER if it is already 'Planet Name' (warning: case sensitive!).")
    #     if name_column != "" and name_column != "Planet Name":
    #         try:
    #             cleandf.rename(columns={name_column: "Planet Name"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
        
    # # fixing transit durations
    # passed = False
    # while passed is False:
    #     passed = True
    #     transit_duration_column = input("What is the name of the column that contains the transit duration? Press ENTER if it is already 'Transit Duration [hrs]' (warning: case sensitive!).")
    #     if transit_duration_column != "" and transit_duration_column != "Transit Duration [hrs]":
    #         transit_duration_units = input("What are the units for the transit duration? Enter 'd' for day or 'm' for minutes. Press ENTER if it is already in hours.")
            
    #         try:
    #             cleandf.rename(columns={transit_duration_column: "Transit Duration [hrs]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
                
    #         if transit_duration_units == "":
    #             continue
    #         elif transit_duration_units.lower() == "d":
    #             cleandf[getColumn(cleandf, "Transit Duration [hrs]")] *= 24
    #         elif transit_duration_units.lower() == "m":
    #             cleandf[getColumn(cleandf, "Transit Duration [hrs]")] /= 60
    #         else:
    #             passed = False
    #             print("Invalid input. Please enter 'd' for day or 'm' for minutes or ENTER if already in hours.")
            
    # # fixing eclipse duration
    # passed = False
    # while passed is False:
    #     passed = True
    #     eclipse_duration_column = input("What is the name of the column that contains the eclipse duration? Press ENTER if it is already 'Eclipse Duration [hrs]' (warning: case sensitive!). Enter 'na' if no such column exists. ")
        
    #     if eclipse_duration_column != "" and eclipse_duration_column!="Eclipse Duration [hrs]" and eclipse_duration_column != "na":
    #         eclipse_duration_units = input("What are the units for the eclipse duration? Enter 'd' for day or 'm' for minutes. Press ENTER if it is already in hours.")
    
    #         try:
    #             cleandf.rename(columns={eclipse_duration_column: "Eclipse Duration [hrs]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
            
    #         if eclipse_duration_units == "":
    #             continue
    #         elif eclipse_duration_units.lower() == "d":
    #             cleandf[getColumn(cleandf, "Eclipse Duration [hrs]")] *= 24
    #         elif eclipse_duration_units.lower() == "m":
    #             cleandf[getColumn(cleandf, "Eclipse Duration [hrs]")] /= 60
    #         else:
    #             passed = False
    #             print("Invalid input. Please enter 'd' for day or 'm' for minutes or ENTER if already in hours.")
        
    #     elif eclipse_duration_column == "na":
    #         cleandf["Eclipse Duration [hrs]"] = cleandf["Transit Duration [hrs]"]
            
    # for index, row in cleandf.iterrows():
    #     eclipse_dur = row["Eclipse Duration [hrs]"]
    #     # err_up = row["Eclipse Duration Error Upper [hrs]"]
    #     # err_low = row["Eclipse Duration Error Lower [hrs]"]
        
    #     if eclipse_dur == 0:
    #         cleandf.at[index, "Eclipse Duration [hrs]"] = row["Transit Duration [hrs]"]
    #         # cleandf.at[index, "Eclipse Duration Error Upper [hrs]"] = row["Transit Duration Error Upper [hrs]"]
    #         # cleandf.at[index, "Eclipse Duration Error Lower [hrs]"] = row["Transit Duration Error Lower [hrs]"]
    
    # # fixing star distances
    # passed = False
    # while passed is False:
    #     passed = True
    #     distance__column = input("What is the name of the column that contains the star distances? Press ENTER if it is already 'Star Distance [pc]' (warning: case sensitive!). Enter 'na' if no such column exists.")
    #     if distance__column != "" and distance__column != "Star Distance [pc]" and distance__column != "na":
    #         distance_units = input("What are the units for the star distance? Enter 'ly' for light years. Press ENTER if it is already in parsecs.")
            
    #         try:
    #             cleandf.rename(columns={distance__column: "Star Distance [pc]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")

    #         if distance_units == "":
    #             continue
    #         elif distance_units.lower() == "ly":
    #             cleandf[getColumn(cleandf, "Star Distance [pc]")] *= 3.262
    #         else:
    #             passed = False
    #             print("Invalid input. Please enter 'ly' for light years or press ENTER if already in parsecs.")
    
    #     elif distance__column == "na":
    #         cleandf["Star Distance [pc]"] = 20
    
    # for index, row in cleandf.iterrows():
    #     eclipse_dur = row["Star Distance [pc]"]
    #     if eclipse_dur == 0:
    #         cleandf.at[index, "Star Distance [pc]"] = 20
            
            
    # # fixing star radii
    # passed = False
    # while passed is False:
    #     passed = True
    #     radius_column = input("What is the name of the column that contains the star radii? Press ENTER if it is already 'Star Radius [Rs]' (warning: case sensitive!).")

    #     if radius_column != "" and radius_column != "Star Radius [Rs]":
    #         radius_units = input("What are the units for the star radius? Enter 'm' for meters or 'km' for kilometers. Press ENTER if it is already in solar radii.")
            
    #         try:
    #             cleandf.rename(columns={radius_column: "Star Radius [Rs]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
            
    #         if radius_units == "":
    #             continue    
    #         elif radius_units.lower() == "m":
    #             cleandf[getColumn(cleandf, "Star Radius [Rs]")] /= 6.957e8
    #         else:
    #             passed = False
    #             print("Invalid input. Please enter 'm' for meters or press ENTER if already in stellar radii.")
    
    # # fixing star temperatures
    # passed = False
    # while passed is False:
    #     passed = True
    #     temp_column = input("What is the name of the column that contains the star temperatures? Press ENTER if it is already 'Star Temperature [K]' (warning: case sensitive!).")
    #     if temp_column != "" and temp_column != "Star Temperature [K]":
    #         try:
    #             cleandf.rename(columns={temp_column: "Star Temperature [K]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
                
    # # fixing semi-major axes
    # passed = False
    # while passed is False:
    #     passed = True
    #     sma_column = input("What is the name of the column that contains the planet semi-major axes? Press ENTER if it is already 'Planet Semi-major Axis [au]' (warning: case sensitive!).")
    #     if sma_column != "" and sma_column != "Planet Semi-major Axis [au]":
    #         sma_units = input("What are the units for the planet semi-major axes? Enter 'm' for meters or 'km' for kilometers. Press ENTER if it is already in astronomical units.")

    #         try:
    #             cleandf.rename(columns={sma_column: "Planet Semi-major Axis [au]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
                
    #         if sma_units == "":
    #             continue
    #         elif sma_units.lower() == "m":
    #             cleandf[getColumn(cleandf, "Planet Semi-major Axis [au]")] /= 1.496e11
    #         elif sma_units.lower() == "km":
    #             cleandf[getColumn(cleandf, "Planet Semi-major Axis [au]")] /= 1.496e8
    #         else:
    #             passed = False
    #             print("Invalid input. Please enter 'm' for meters or press ENTER if already in astronomical units.")
            
    # # fixing planet radii
    # passed = False
    # while passed is False:
    #     passed = True
    #     radius_column = input("What is the name of the column that contains the planet radii? Press ENTER if it is already 'Planet Radius [Rjup]' (warning: case sensitive!).")
    #     if radius_column != "" and radius_column != "Planet Radius [Rjup]":
    #         radius_units = input("What are the units for the planet radii? Enter 'm' for meters, 'km' for kilometers, or 'Re' for Earth radii. Press ENTER if it is already in Jupiter radii.")

    #         try:
    #             cleandf.rename(columns={radius_column: "Planet Radius [Rjup]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
            
    #         if radius_units == "":
    #             continue    
    #         elif radius_units.lower() == "m":
    #             cleandf[getColumn(cleandf, "Planet Radius [Rjup]")] /= 69911e3
    #         elif radius_units.lower() == "km":
    #             cleandf[getColumn(cleandf, "Planet Radius [Rjup]")] /= 69911
    #         elif radius_units.lower() == "re":
    #             cleandf[getColumn(cleandf, "Planet Radius [Rjup]")] /= 11.2
    #         else:
    #             passed = False
    #             print("Invalid input. Please enter 'm' for meters, 'km' for kilometers, 'Re' for Earth radii, or press ENTER if already in Jupiter radii.")
            
    # # fixing planet masses
    # passed = False
    # while passed is False:
    #     passed = True
    #     mass_column = input("What is the name of the column that contains the planet masses? Press ENTER if it is already 'Planet Mass [Mjup]' (warning: case sensitive!).")
    #     if mass_column != "" and mass_column != "Planet Mass [Mjup]":
    #         mass_units = input("What are the units for the planet masses? Enter 'kg' for kilograms or 'Me' for Earth masses. Press ENTER if it is already in Jupiter masses.")
            
    #         try:
    #             cleandf.rename(columns={mass_column: "Planet Mass [Mjup]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
            
    #         if mass_units == "":
    #             continue
    #         elif mass_units.lower == "kg":
    #             cleandf[getColumn(cleandf, "Planet Mass [Mjup]")] /= 1.898e27
    #         elif mass_units.lower() == "me":
    #             cleandf[getColumn(cleandf, "Planet Mass [Mjup]")] /= 317.8
    #         else:
    #             passed = False
    #             print("Invalid input. Please enter 'kg' for kilograms, 'Me' for Earth masses, or press ENTER if already in Jupiter masses. ")
    
    # # fixing Mean Molecular Weights
    # passed = False
    # while passed is False:
    #     passed = True
    #     mmw_column = input("What is the name of the column that contains the mean molecular weights? Press ENTER if it is already 'Mean Molecular Weight' (warning: case sensitive!). Enter 'na' if there is no mean molecular weight column.")
    #     if mmw_column != "" and mmw_column != "na" and mmw_column != "Mean Molecular Weight":
    #         try:
    #             cleandf.rename(columns={mmw_column: "Mean Molecular Weight"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
    #     elif mmw_column == "na":
    #         cleandf["Mean Molecular Weight"] = 2.3
    #     else:
    #         passed = False
    #         print("Invalid column name. Please enter a valid column name.")
        
    # # fixing planet albedos
    # passed = False
    # while passed is False:
    #     passed = True
    #     alb_column = input("What is the name of the column that contains the planet albedos? Press ENTER if it is already 'Planet Albedo' (warning: case sensitive!). Enter 'na' if there is no planet albedo column.")
    #     if alb_column != "" and alb_column != "Planet Albedo" and alb_column != "na":
    #         try:
    #             cleandf.rename(columns={alb_column: "Planet Albedo"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
                
    #     elif alb_column == "na":
    #         cleandf["Planet Albedo"] = 0.2  
    #     else:
    #         passed = False
    #         print("Invalid column name. Please enter a valid column name.")
                
    # # fixing planet gemotric albedos
    # passed = False
    # while passed is False:
    #     passed = True
    #     alb_geo_column = input("What is the name of the column that contains the planet geometric albedos? Press ENTER if it is already 'Planet Geometric Albedo' (warning: case sensitive!). Enter 'na' if there is no planet geometric albedo column.")
    #     if alb_geo_column != "" and alb_geo_column != "Planet Geometric Albedo" and alb_geo_column != "na":
    #         try:
    #             cleandf.rename(columns={alb_geo_column: "Planet Geometric Albedo"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
    #     elif alb_geo_column == "na":
    #         cleandf["Planet Geometric Albedo"] = 0.25
    #     else:
    #         passed = False
    #         print("Invalid column name. Please enter a valid column name.")
    
    # # fixing heat redistribution factors
    # passed = False
    # while passed is False:
    #     passed = True
    #     hrf_column = input("What is the name of the column that contains the heat redistribution factors? Press ENTER if it is already 'Heat Redistribution Factor' (warning: case sensitive!). Enter 'na' if there is no heat redistribution factor column.")
    #     if hrf_column != "" and hrf_column != "Heat Redistribution Factor" and hrf_column != "na":
    #         try:
    #             cleandf.rename(columns={hrf_column: "Heat Redistribution Factor"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
    #     elif hrf_column == "na":
    #         cleandf["Heat Redistribution Factor"] = 0.8
    #     else:
    #         passed = False
    #         print("Invalid column name. Please enter a valid column name.")
    
    # # fixing planet periods
    # passed = False
    # while passed is False:
    #     passed = True
    #     period_column = input("What is the name of the column that contains the planet periods? Press ENTER if it is already 'Planet Period [days]' (warning: case sensitive!).")
    #     period_units = input("What are the units for the planet periods? Enter 'h' for hours. Press ENTER if it is already in days")
    #     if period_column != "" and period_column != "Planet Period [days]":
    #         try:
    #             cleandf.rename(columns={period_column: "Planet Period [days]"}, inplace=True)
    #         except KeyError:
    #             passed = False
    #             print("Invalid column name. Please enter a valid column name.")
    #     if period_units.lower() in ["h", "hr", "hrs"]:
    #         cleandf[getColumn(cleandf, "Planet Period [days]")] /= 24
    #     elif period_units.lower() in ["d", "day", "days"] or period_units == "":
    #         continue
    #     else:
    #         passed = False
    #         print("Invalid input. Please enter 'hrs' for hours or press ENTER if already in days.")
            
    # return cleandf