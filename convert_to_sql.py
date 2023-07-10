import os
import pandas as pd

def save_column_as_csv(data, column_name, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for key, df in data.items():
        output_path = os.path.join(output_folder, f"{key}.csv")
        if column_name in df.columns:
            time_series = df[column_name].apply(pd.Series)
            max_length = time_series.apply(len).max()

            # Create time index with spacing of 1/30 seconds
            time_index = pd.Index(range(max_length)) / 30

            # Create a new dataframe with each column corresponding to a row and index as time
            new_df = pd.DataFrame(index=time_index)
            for i, series in enumerate(time_series):
                new_df[i] = pd.Series(series)

            new_df.to_csv(output_path)
        else:
            print(f"Column '{column_name}' does not exist in dataframe for key '{key}'")

# Example usage
data = pd.read_pickle(r'Z:\mfk\basty-projects\bouts_dict.pkl')
column_name = "distance.origin-prob"
output_folder = os.path.dirname(r"Z:\mfk\basty-projects\bouts_to_csv")

save_column_as_csv(data, column_name, output_folder)
