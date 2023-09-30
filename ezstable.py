# Following script combines the annotation data with the time series data


path = r'C:\Users\Grover\Documents\GitHub\EZLabel'
dict_path = r'Z:\mfk\basty-projects\bouts_dict.pkl'

import pandas as pd
import os
import glob


def process_row(row, dictionary, N):
    df_dict = dictionary[row['name']]
    df_dict_filtered = df_dict.drop(['start_index', 'stop_index', 'region'], axis=1)

    trial_id = int(row['trial_id'])
    peak_index = row['peak_index']

    # New dictionary to store sliced data with column names
    sliced_data_dict = {}

    for col in df_dict_filtered.columns:
        if peak_index-N >= 0:
            start = max(0, peak_index - N)
            end = min(len(df_dict_filtered.loc[trial_id, col]), peak_index + N)
            sliced_data_dict[col] = df_dict_filtered.loc[trial_id, col][start:end]

    return sliced_data_dict


pkl_files = glob.glob(os.path.join(path, '*.pkl'))
ts_dict = pd.read_pickle(dict_path)

df_list = []  # A list to store each DataFrame

for file in pkl_files:
    data = pd.read_pickle(file)
    df = pd.DataFrame(data)
    df['name'] = os.path.splitext(os.path.basename(file))[0]
    df_list.append(df)  # Append the DataFrame to the list

# Concatenate all the DataFrames in the list into a single DataFrame
annotations = pd.concat(df_list, ignore_index=True)

# Rename the columns to make it more intuitive
annotations.rename(columns = {'index':'peak_index','column':'trial_id'},inplace=True)

# Create an empty DataFrame to store all the processed rows
processed_data_df = pd.DataFrame()

# Loop through each row in annotations
for i, row in annotations.iterrows():
    processed_row = process_row(row, ts_dict, 45)

    # Create a DataFrame for this row and append it to processed_data_df
    row_df = pd.DataFrame(processed_row)
    row_df['name'] = row['name']
    row_df.set_index('name', append=True, inplace=True)
    processed_data_df = pd.concat([processed_data_df, row_df])

# Rearrange the index levels
processed_data_df = processed_data_df.swaplevel('name')

# Reset index names
processed_data_df.index.names = ['name', 'time']
