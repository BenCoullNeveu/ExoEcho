import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from thefuzz import process
import os


FONTSIZE = 12

# Function to update the dataframe based on user selections
def update_dataframe(dataframe, column_dict, unit_dict)->pd.DataFrame:
    
    df = dataframe.copy()
    
    # getting the order of the columns
    orderlist = ['Planet Name',
                    'Transit Duration',
                    'Eclipse Duration',
                    'Star Distance', 
                    'Star Radius', 
                    'Star Temperature', 
                    'Planet Semi-major Axis', 
                    'Planet Radius', 
                    'Planet Mass', 
                    'Mean Molecular Weight', 
                    'Planet Albedo', 
                    'Planet Geometric Albedo', 
                    'Heat Redistribution Factor', 
                    'Planet Period']
    

    for i, (key, val) in enumerate(column_dict.items()):
        
        if "Planet Name" == orderlist[i]:
            if column_dict[key] != "" and column_dict[key] != 'Planet Name':
                try:
                    df.rename(columns={column_dict[key]: "Planet Name"}, inplace=True)
                except KeyError as keyerror:
                    messagebox.showerror("KeyError for Planet Name", f"No column named {keyerror} found in DataFrame. Please try again.")
        
        
        if "Transit Duration" == orderlist[i]:
            if column_dict[key] != "" and column_dict[key] != 'Transit Duration [hrs]':
                try:
                    df.rename(columns={column_dict[key]: "Transit Duration [hrs]"}, inplace=True)
                except KeyError as keyerror:
                    messagebox.showerror("KeyError for Transit Duration", f"No column named {keyerror} found in DataFrame. Please try again.")
                
                if unit_dict[key] == 'yrs':
                    df["Transit Duration [hrs]"] *= 8760
                elif unit_dict[key] == 'd':
                    df["Transit Duration [hrs]"] *= 24
                elif unit_dict[key] == 'm':
                    df["Transit Duration [hrs]"] /= 60
                elif unit_dict[key] == 's':
                    df["Transit Duration [hrs]"] /= 3600
                    
        
        if "Eclipse Duration" == orderlist[i]:
            if column_dict[key] != "" and column_dict[key] != "na" and column_dict[key] != 'Eclipse Duration [hrs]':
                try:
                    df.rename(columns={column_dict[key]: "Eclipse Duration [hrs]"}, inplace=True)
                except KeyError as keyerror:
                    messagebox.showerror("KeyError for Eclipse Duration", f"No column named {keyerror} found in DataFrame. Please try again.")
                
                if unit_dict[key] == 'yrs':
                    df["Eclipse Duration [hrs]"] *= 8760
                elif unit_dict[key] == 'd':
                    df["Eclipse Duration [hrs]"] *= 24
                elif unit_dict[key] == 'm':
                    df["Eclipse Duration [hrs]"] /= 60
                elif unit_dict[key] == 's':
                    df["Eclipse Duration [hrs]"] /= 3600
                    
            elif column_dict[key] == "" or column_dict[key] == "na":
                df["Eclipse Duration [hrs]"] = df["Transit Duration [hrs]"]
                
            for index, row in df.iterrows():
                eclipse_dur = row["Eclipse Duration [hrs]"]
            
            if eclipse_dur == 0:
                df.at[index, "Eclipse Duration [hrs]"] = row["Transit Duration [hrs]"]
        
        
        
        if "Star Distance" == orderlist[i]:
            if column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Star Distance [pc]"}, inplace=True)
                if unit_dict[key] == 'ly':
                    df["Star Distance [pc]"] *= 3.262
            else:
                df["Star Distance [pc]"] = 20


        if "Star Radius" == orderlist[i]:
            if column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Star Radius [Rs]"}, inplace=True)
                if unit_dict[key] == 'm':
                    df["Star Radius [Rs]"] /= 6.957e8


        if "Star Temperature" == orderlist[i]:
            if column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Star Temperature [K]"}, inplace=True)


        if "Planet Semi-major Axis" == orderlist[i]:
            if column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Planet Semi-major Axis [au]"}, inplace=True)
                if unit_dict[key] == 'm':
                    df["Planet Semi-major Axis [au]"] /= 1.496e11
                elif unit_dict[key] == 'km':
                    df["Planet Semi-major Axis [au]"] /= 1.496e8


        if "Planet Radius" == orderlist[i]:
            if column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Planet Radius [Rjup]"}, inplace=True)
                if unit_dict[key] == 'm':
                    df["Planet Radius [Rjup]"] /= 69911e3
                elif unit_dict[key] == 'km':
                    df["Planet Radius [Rjup]"] /= 69911
                elif unit_dict[key] == 'Earth Radii':
                    df["Planet Radius [Rjup]"] /= 11.2


        if "Planet Mass" == orderlist[i]:
            if column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Planet Mass [Mjup]"}, inplace=True)
                if unit_dict[key] == 'kg':
                    df["Planet Mass [Mjup]"] /= 1.898e27
                elif unit_dict[key] == 'Earth Masses':
                    df["Planet Mass [Mjup]"] /= 317.8


        if "Mean Molecular Weight" == orderlist[i]:
            if column_dict[key] != "" and column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Mean Molecular Weight"}, inplace=True)
            else:
                df["Mean Molecular Weight"] = 2.3

        # Update columns for planet albedos
        if "Planet Albedo" == orderlist[i]:
            if column_dict[key] != "" and column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Planet Albedo"}, inplace=True)
            else:
                df["Planet Albedo"] = 0.2

        # Update columns for planet geometric albedos
        if "Planet Geometric Albedo" == orderlist[i]:
            if column_dict[key] != "" and column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Planet Geometric Albedo"}, inplace=True)
            else:
                df["Planet Geometric Albedo"] = 0.25

        # Update columns for heat redistribution factors
        if "Heat Redistribution Factor" == orderlist[i]:
            if column_dict[key] != "" and column_dict[key] != 'na':
                df.rename(columns={column_dict[key]: "Heat Redistribution Factor"}, inplace=True)
            else:
                df["Heat Redistribution Factor"] = 0.8

        # Update columns for planet periods
        if "Planet Period [days]" == orderlist[i]:
            if column_dict[key] != 'na' and column_dict[key] != "":
                df.rename(columns={column_dict[key]: "Planet Period [days]"}, inplace=True)
                if unit_dict[key] == 'yrs':
                    df["Planet Period [days]"] *= 365.25
                elif unit_dict[key] == 'd':
                    df["Planet Period [days]"] *= 1
                elif unit_dict[key] == 'h':
                    df["Planet Period [days]"] /= 24
                elif unit_dict[key] == 's':
                    df["Planet Period [days]"] /= 86400
            else:
                messagebox.showerror("Error", "Please select a column for Planet Period.")


    messagebox.showinfo("Success", "DataFrame updated successfully!")
    
    return df
    

# Function to create the tkinter window
def create_window(dataframes=None)->pd.DataFrame:
    """Returns the updated DataFrame based on user selections. This function creates a tkinter window that 
    allows the user to select columns from a DataFrame and update them based on a predefined list of terms and units.
    If no dataframes are provided, the function will search for all DataFrames in memory and use them as options.

    Args:
        dataframes (pd.DataFrame, optional): the DataFrames that can be updated

    Returns:
        pd.DataFrame: the updated DataFrame
    """
    
    updated_df = None
    
    if dataframes is None:
        df_names = [obj for obj in globals() if isinstance(eval(obj), pd.DataFrame) and obj[0] != "_"]
        dataframes = dict([(df_n, eval(df_n)) for df_n in df_names])
    
    elif isinstance(dataframes, pd.DataFrame):
        dataframes = {"DataFrame": dataframes}
    
    window = tk.Tk()
    window.title("DataFrame Column Selector")
    
    def filter_options(event, term, menu):
        # Get the user's current input in the combobox
        typed_value = menu.get()
        
        # Get the list of all possible columns from the current dataframe
        columns = ['na'] + list(dataframes[df_var.get()].columns)
        
        # Filter the columns based on what the user has typed
        if typed_value == '':
            filtered_values = columns
        else:
            filtered_values = [col for col in columns if typed_value.lower() in col.lower()]

        # Update the combobox dropdown with the filtered options
        menu['values'] = filtered_values

        # Keep the current input in the combobox
        menu.set(typed_value)
    
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?\nAny unsaved changes will be lost."):
            window.destroy()
    
    window.protocol("WM_DELETE_WINDOW", on_closing)
    
    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family="Helvetica", size=FONTSIZE)
    
    titlefont = font.Font(family='Helvetica', size=FONTSIZE+1, weight='bold')
    boxfont = font.Font(family='Helvetica', size=12)

    # Frame for column selections
    frame_columns = tk.Frame(window)
    frame_columns.grid(row=1, column=0, padx=10, pady=10)

    # Add titles to the columns
    # title_label = tk.Label(frame_columns, text="Term", anchor="w")
    # title_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

    column_label = tk.Label(frame_columns, text="Current Column Name", anchor="center", font=titlefont)
    column_label.grid(row=0, column=1, padx=20, sticky=tk.N)

    unit_label = tk.Label(frame_columns, text="Current Units (if applicable)", anchor="center", font=titlefont)
    unit_label.grid(row=0, column=2, padx=20, sticky=tk.N)

    updated_column_label = tk.Label(frame_columns, text="Updated Column Name", anchor="center", font=titlefont)
    updated_column_label.grid(row=0, column=4, padx=20, pady=5, sticky=tk.N)
    


    # Create dictionary to store user selections and labels for updated columns
    column_dict = {}
    unit_dict = {}

    # Define the terms to match. -> Value pattern is (unit, label)
    terms = {
        'Planet Name': ([], "Planet Name"),
        'Transit Duration': (['hrs', 'd', 'm', 's'], "Transit Duration [hrs]"),
        'Eclipse Duration': (['hrs', 'd', 'm', 's'], "Eclipse Duration [hrs]"),
        'Star Distance': (['pc', 'ly'], "Star Distance [pc]"),
        'Star Radius': (['Solar radii', 'm'], "Star Radius [Rs]"),
        'Star Temperature': (['K'], "Star Temperature [K]"),
        'Semi-major Axis': (['au', 'm', 'km'], "Planet Semi-major Axis [au]"),
        'Planet Radius': (['Jupiter Radii', 'Earth Radii', 'm', 'km'], "Planet Radius [Rjup]"),
        'Planet Mass': (['Jupiter Masses', 'Earth Masses', 'kg'], "Planet Mass [Mjup]"),
        'Mean Molecular Weight': ([], "Mean Molecular Weight"),
        'Planet Albedo': ([], "Planet Albedo"),
        'Planet Geometric Albedo': ([], "Planet Geometric Albedo"),
        'Heat Redistribution Factor': ([], "Heat Redistribution Factor"),
        'Planet Period': (['yrs', 'd', 'h', 's'], "Planet Period [days]")
    }
    
    # adding vertical line that spans all rows
    ttk.Separator(frame_columns, orient="vertical").grid(column=3, row=0, rowspan=len(terms)+1, sticky=tk.NS, padx=5)

    # Create UI elements for each term
    for idx, (term, (units, colname)) in enumerate(terms.items()):
        idx += 1 # idx + 1 to account for the title row
        label = tk.Label(frame_columns, text=f"Select column for {term}:")
        label.grid(row=idx, column=0, sticky=tk.W) 

        column_var = tk.StringVar(window)
        column_var.set('na')
        column_menu = ttk.Combobox(frame_columns, textvariable=column_var, values=['na'], font=boxfont, state='normal')
        column_menu.grid(row=idx, column=1, sticky=tk.N)
        column_dict[term] = column_menu

        if units:
            unit_var = tk.StringVar(window)
            unit_var.set(units[0])
            unit_menu = ttk.Combobox(frame_columns, textvariable=unit_var, values=units, font=boxfont, state='readonly')
            unit_menu.grid(row=idx, column=2, sticky=tk.N)
            unit_dict[term] = unit_var
        else:
            unit_dict[term] = None

        colname_label = tk.Label(frame_columns, text=colname)
        colname_label.grid(row=idx, column=4, padx=20, sticky=tk.W)
        
    # Bind the filter_options function to each combobox for dynamic filtering
    for term, menu in column_dict.items():
        menu.bind('<KeyRelease>', lambda event, term=term, menu=menu: filter_options(event, term, menu))

        

    # Frame for DataFrame selection
    frame_df = tk.Frame(window)
    frame_df.grid(row=0, column=0, padx=10, pady=10)

    df_label = tk.Label(frame_df, text="Select DataFrame:")
    df_label.pack(side=tk.LEFT)

    df_var = tk.StringVar(window)
    df_var.set(list(dataframes.keys())[0])
    df_menu = ttk.Combobox(frame_df, textvariable=df_var, values=list(dataframes.keys()), font=boxfont, state='readonly')
    df_menu.pack(side=tk.LEFT)
    
    # Define the possible columns
    def update_columns(*args):
        columns = ['na'] + list(dataframes[df_var.get()].columns)
        for term, menu in column_dict.items():
            best_match = process.extractOne(term, columns, score_cutoff=80)
            menu['values'] = columns
            if best_match:
                menu.set(best_match[0])

    df_var.trace_add("write", update_columns)
    update_columns()
        
        


    def submit():
        nonlocal updated_df
        selected_df = dataframes[df_var.get()]
        col_dict = {key: var.get() for key, var in column_dict.items()}
        unit_dict_final = {key: (var.get() if var else None) for key, var in unit_dict.items()}
        
        cropped_df = selected_df.copy()
        if keep_columns_var.get():
            columns_to_keep = [col_dict[key] for key in col_dict if col_dict[key] != 'na' and col_dict[key] != ""]
            cropped_df = selected_df[columns_to_keep]
            
        updated_df = update_dataframe(cropped_df, col_dict, unit_dict_final)
        
        save_choice = messagebox.askyesno("Save DataFrame", "Do you want to save the updated DataFrame?")
        while True:
            if not save_choice:
                break
            
            file_path = filedialog.asksaveasfilename(
                initialdir=os.getcwd(),
                title="Save DataFrame",
                defaultextension=".csv",
                filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
            )
            
            if file_path:
                updated_df.to_csv(file_path, index=False)
                messagebox.showinfo("Saved", f"DataFrame saved successfully at {file_path}")
                break
            else:
                retry_save = messagebox.askretrycancel("Save Canceled", "Save operation was canceled. Do you want to try saving again?")
                if not retry_save:
                    break
    
    keep_columns_var = tk.BooleanVar(value=False)
    keep_columns_checkbox = tk.Checkbutton(window, text="Keep only these columns", variable=keep_columns_var)
    keep_columns_checkbox.grid(row=2, column=0, padx=10, pady=15)
    
    submit_button = tk.Button(window, text="Update DataFrame", command=submit)
    submit_button.grid(row=3, column=0, padx=10, pady=25)

    messagebox.showinfo("DataFrames", f"DataFrames found: {list(dataframes.keys())}.\nPlease select the DataFrame you would like to update from the dropdown menu.")
    
    window.mainloop()
    
    return updated_df