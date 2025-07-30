'''
Suite of functions for performing analysis on data
output from many time slices.
'''

import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import itertools
from collections import defaultdict

# TODO init to make object from csv

# TODO read in lines avail
lines=["H1_6562.80A","O1_1304.86A","O1_6300.30A","O2_3728.80A","O2_3726.10A","O3_1660.81A",
       "O3_1666.15A","O3_4363.21A","O3_4958.91A","O3_5006.84A", "He2_1640.41A","C2_1335.66A",
       "C3_1906.68A","C3_1908.73A","C4_1549.00A","Mg2_2795.53A","Mg2_2802.71A","Ne3_3868.76A",
       "Ne3_3967.47A","N5_1238.82A","N5_1242.80A","N4_1486.50A","N3_1749.67A","S2_6716.44A","S2_6730.82A"]

def check_file_pattern(folder_path, pattern):
    '''Checks if a file matching the pattern exists in the folder.'''
    files = glob.glob(f"{folder_path}/{pattern}")
    return len(files) > 0

class SimulationPostAnalysis:
    '''
    Class containing post-processing functions for a simulation - multiple
    time slices.
    '''

    main_table = pd.DataFrame()

    def __init__(self, sim_titl:str, data_path:str):
        '''
        data_path: path to folder with information files
        sim_titl: str referring to simulation
        '''

        self.sim_titl = sim_titl
        self.data_path = data_path
        self.lines = lines

        self.make_dir()


    def make_dir(self):
        self.directory = f'{self.sim_titl}_post_analysis'

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)


    def get_files(self, pattern: str):
        """
        Returns an ordered list of files matching the given pattern.

        Parameters:
        -----------
        pattern (str): The glob-style pattern to match.

        Returns:
        --------
        A list of file paths, sorted alphabetically.
        """
        files = glob.glob(pattern)
        return sorted(files)
    

    def parse_file_to_dict(self, filepath):
        '''
        Parses a file with 'key: value' lines into a dictionary.
        '''

        data = {}
        float_pattern = r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"

        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if ':' not in line:
                    continue
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()

                # Try to match float or array of floats
                if re.fullmatch(float_pattern, value):
                    data[key] = float(value)
                elif re.match(r"\[.*\]", value):
                    # Try parsing arrays like [1 2 3]
                    try:
                        numbers = [
                            float(v) for v in re.findall(float_pattern, value)
                        ]
                        data[key] = numbers
                    except:
                        data[key] = value
                else:
                    # fallback: raw string
                    try:
                        data[key] = float(value)
                    except:
                        data[key] = value

        return data
    

    def populate_table(self):
        '''
        Populate main_table with simulation information at each time slice.

        
        '''

        data_rows = []

        float_pattern = r'[-+]?\d*\.\d+([eE][-+]?\d+)?'

        info_file_pattern = self.data_path + 'output_*_sim_info.txt'
        field_info_pattern = self.data_path + 'output_*_field_info.txt'
        lum_pattern = self.data_path + 'output_*_line_luminosity.txt'
        header_pattern = self.data_path + 'header_*.txt'

        print(info_file_pattern)

        sim_info_files = self.get_files(info_file_pattern)
        #field_info_files = self.get_files(info_file_pattern)
        #lum_files = self.get_files(info_file_pattern)
        #header_files = self.get_files(info_file_pattern)

        #file_lists = [sim_info_files, field_info_files, lum_files]

        #for file_list in file_lists:
        #    for file in file_list:
        #        with open(file, 'r') as file:
        #            file_content = file.read()

        print(len(sim_info_files))

        for sim_file in sim_info_files:
            match = re.match(r"output_(\d+)_sim_info\.txt",
                             os.path.basename(sim_file))
            if not match:
                continue
            output_id = match.group(1)
            print(output_id)

            row_data = {"output_id": int(output_id)}
            row_data.update(self.parse_file_to_dict(sim_file))

            lum_file = self.data_path + f"output_{output_id}_line_luminosity.txt"
            field_info_file = self.data_path + f"output_{output_id}_field_info.txt"

            print(lum_file)
            print(field_info_file)

            if os.path.exists(lum_file):
                row_data.update(self.parse_file_to_dict(lum_file))
            else:
                print('Warning: Missing luminosity file for output ' + \
                      output_id)

            if os.path.exists(field_info_file):
                row_data.update(self.parse_file_to_dict(field_info_file))
            else:
                print('Warning: Missing field info file for output' + \
                      output_id)

            data_rows.append(row_data)

        df = pd.DataFrame(data_rows)
        df.sort_values("output_id", inplace=True)
        df.reset_index(drop=True, inplace=True)

        self.df = df

        df.to_csv(os.path.join(self.directory, 'analysis_data.csv'),
                  index=True)

        return df



        temp_min_pattern = fr'{field}_min: [-+]?\d*\.\d+([eE][-+]?\d+)?'
        temp_min = float(re.search(temp_min_pattern, file_content).group(1))


    def lvz(self, df, lines, group_species=True):
        '''
        TODO
        '''

        column_list = []

        for line in lines:
            field = ('gas', f'luminosity_{line}')
            column = str(field) + '_agg'
            column_list.append(column)

        # Group lines by element (e.g., 'O3', 'H1', etc.)
        groups = defaultdict(list)
        for line in lines:
            prefix = line.split('_')[0]
            groups[prefix].append(line)
            print(groups)

        # Set up color and linestyle cycler
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
        linestyles = ['-', '--', '-.', ':']
        style_cycler = itertools.cycle(itertools.product(colors, linestyles))

        plt.figure(figsize=(10, 6))

        if group_species:
            for group, group_lines in groups.items():
                color, linestyle = next(style_cycler)
                for i, line in enumerate(group_lines):
                    column = f"('gas', 'luminosity_{line}')_agg"
                    if column in df.columns:
                        y_vals = df[column].replace(0, np.nan)
                        # Only label the first line of the group
                        label = group if i == 0 else None
                        plt.plot(df['current_redshift'], np.log10(y_vals),
                                 color=color, linestyle=linestyle,
                                 label=label)
            # Show unique element legend to the right
            plt.legend(title='Element', bbox_to_anchor=(1.05, 1),
                       loc='upper left', borderaxespad=0.)
        else:
            for i, column in enumerate(column_list):
                if column in df.columns:
                    y_vals = df[column].replace(0, np.nan)
                    color, linestyle = next(style_cycler)
                    plt.plot(df['current_redshift'], np.log10(y_vals),
                             linestyle=linestyle,
                             color=color, label=lines[i])
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', 
                       borderaxespad=0.)

        plt.xlabel('Redshift')
        plt.ylabel(r'Luminosity [erg s$^{-1}$]')
        plt.grid(True)
        ax = plt.gca()
        ax.invert_xaxis()
        plt.tight_layout()

        #plt.show()
        if group_species:
            plt.savefig(os.path.join(self.directory, 'lvz_group_species.png'))
        else:
            plt.savefig(os.path.join(self.directory, 'lvz.png'))

    
    





    #def lvz(self):
    #    '''
    #    Luminosity vs. Redshift
    #    '''


'''
post = Simulation_Post_Analysis('CC_Fiducial',
                                '/Users/bnowicki/Documents/Research/Ricotti/CC_Fiducial_analysis/movie_dir/')

df = post.gather_all_data()
print(df.head())
# save to CSV
df.to_csv("combined_simulation_data.csv", index=False)

# === Configuration ===
csv_file = "combined_simulation_data.csv"
x_field = "current_redshift"
y_field = "H1_6562.80A Luminosity"
title = f"{y_field} vs {x_field}"

# === Load data ===
df = pd.read_csv(csv_file)

# Check if fields exist
if x_field not in df.columns or y_field not in df.columns:
    raise ValueError(f"Fields not found in CSV: {x_field}, {y_field}")

# === Plot ===
plt.figure(figsize=(8, 6))
plt.plot(df[x_field], df[y_field], marker='o', linestyle='-', color='blue')
plt.xlabel(x_field)
plt.ylabel(y_field)
plt.title(title)
plt.grid(True)
plt.tight_layout()
plt.savefig("plot.png")
plt.show()

'''

    

