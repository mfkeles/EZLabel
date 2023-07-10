<img src="https://github.com/mfkeles/EZLabel/assets/22876046/9e785534-2176-4a25-b4a8-5c8be4636eff" width="500">   

# EZLabel: Interactive Data Labeling Tool

Welcome to EZLabel, an interactive tool built with Python, Dash, and Plotly, to simplify the process of manual data labeling. It allows you to manually select and label data points in a time series, and save the labels to use them for further analysis or Machine Learning purposes.

## Features
- Drag and drop functionality to load your dataset.
- Navigate through different columns of your dataset to label data.
- Click on a data point to annotate and store the label.
- Load and save annotations for reusability.

## Code Overview

The script consists of a `Dash` application with an interactive layout that allows users to upload a CSV file, navigate through its columns, and label the data points by clicking on them. 

The layout includes an upload component, several button controls to navigate through the columns and save/load annotations, dropdown menu to select columns, and a graph that plots the selected column's data.

The data uploaded by the user is stored in the Dash Store component, allowing for efficient sharing of data between callbacks while keeping the application stateless (this optimizes scalability and speed).

All the interaction logic of the application is controlled via several Dash callbacks that react to user's actions (like file upload, button clicks, or graph clicks) and update the application's state accordingly.

## Usage

1. **Upload your CSV File**: Drag and drop your CSV file into the upload box or click 'Select Files' to open the file dialog.
2. **Navigate through Columns**: Use the 'Previous Column' and 'Next Column' buttons to navigate through the columns of your dataset.
3. **Label Data Points**: Click on a data point in the plot to label it. The selected points will be highlighted.
4. **Save Annotations**: After labeling data points, click 'Save Annotations' button to store your labels in a `.pkl` file in the same directory as the loaded file. The filename will be the same as the loaded CSV file, but with a `.pkl` extension.
5. **Load Annotations**: If you have previously saved labels for the currently loaded CSV file, you can load them back into the application by clicking 'Load Annotations' button.

## Installation

To use EZLabel, you need to have Python installed along with several packages. The required packages include:

- `dash`
- `plotly`
- `pandas`
- `pickle`
- `os`
- `base64`
- `io`

Install these packages using pip:
```
pip install dash plotly pandas
```

Then, clone the EZLabel repository to your local machine and run the script.

## License

EZLabel is open-sourced under the MIT license.

## Contributions

Contributions are always welcome! Please read the contribution guidelines first.

