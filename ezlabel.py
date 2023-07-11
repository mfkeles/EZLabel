import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import pandas as pd
import os
import base64
import io
import pickle

app = dash.Dash(__name__)

N = 30  # Number of points to mark before and after the clicked point

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    dcc.Store(id='intermediate-data'),
    dcc.Store(id='column-index', data=0),
    dcc.Store(id='prev-clicks-store', data=0),
    dcc.Store(id='next-clicks-store', data=0),
    dcc.Store(id='annotations', data=[]),  # Store for annotations
    dcc.Graph(id='figure'),
    html.Div(id='clickdata', children="No click registered yet."),
    html.Div(id='output-data-upload'),
    html.Div(id='save-confirm'),
    dcc.Dropdown(id='column-dropdown'),
    html.Button('Previous Column', id='prev-button'),
    html.Button('Next Column', id='next-button'),
    html.Button('Save Annotations', id='save-button'),
    html.Button('Load Annotations', id='load-button'),
    html.Div(id='annotations-list')

])


@app.callback(
    Output('intermediate-data', 'data'),
    Output('column-dropdown', 'options'),
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename')])
def update_data(contents, filename):
    if contents is None:
        raise dash.exceptions.PreventUpdate

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            data = {
                'df': df.to_json(orient='split', index=False),
                'columns': [col for col in df.columns if col not in ['start_index', 'stop_index', 'region']],
                'filename': filename.split('.')[0]  # add filename to data
            }
    except Exception as e:
        return dash.no_update

    column_options = [{'label': column, 'value': column} for column in data['columns']]

    return data, column_options, f'Successfully loaded {filename}'  # return only three values here




@app.callback(
    Output('clickdata', 'children'),
    [Input('figure', 'clickData')],
    [State('column-dropdown', 'value'),
     State('annotations', 'data'),
     State('intermediate-data', 'data')])
def display_click_data(clickData, selected_column, annotations, data):
    if clickData is None:
        return "No click registered yet."
    else:
        clicked_x = clickData['points'][0]['x']
        clicked_y = clickData['points'][0]['y']

        # Add the clicked point to the annotations
        new_annotation = {
            'column': selected_column,
            'index': clicked_x,
            'value': clicked_y
        }
        annotations.append(new_annotation)

        # Update the stored annotations
        filename = data["filename"]  # Use the filename of the uploaded CSV file
        with open(f'{filename}.pkl', 'wb') as f:
            pickle.dump(annotations, f)

        return f"Clicked point: x={clicked_x}, y={clicked_y}"


@app.callback(
    Output('figure', 'figure'),
    Output('column-index', 'data'),
    Output('prev-clicks-store', 'data'),
    Output('next-clicks-store', 'data'),
    Output('column-dropdown', 'value'),
    [Input('prev-button', 'n_clicks'),
     Input('next-button', 'n_clicks'),
     Input('column-dropdown', 'value'),
     Input('intermediate-data', 'data'),
     Input('annotations', 'data')],
    [State('column-index', 'data'),
     State('prev-clicks-store', 'data'),
     State('next-clicks-store', 'data')]
)
def update_figure(prev_clicks, next_clicks, selected_column, data, annotations, column_index, prev_clicks_store,
                  next_clicks_store):
    ctx = dash.callback_context
    if not ctx.triggered or 'intermediate-data.data' in [x['prop_id'] for x in ctx.triggered]:
        # if the callback was not triggered or if it was triggered by data upload
        # select the first column to plot
        if data is None:
            raise dash.exceptions.PreventUpdate

        df = pd.read_json(data['df'], orient='split')
        columns = data['columns']
        selected_column = columns[0]
        column_index = 0
        prev_clicks = 0
        next_clicks = 0
    else:
        df = pd.read_json(data['df'], orient='split')
        columns = data['columns']

        prev_clicks = prev_clicks or 0
        next_clicks = next_clicks or 0

        if ctx.triggered[0]['prop_id'] == 'column-dropdown.value':
            column_index = columns.index(selected_column)
        else:
            prev_diff = prev_clicks - prev_clicks_store
            next_diff = next_clicks - next_clicks_store
            next_column_index = (column_index + next_diff - prev_diff) % len(columns)
            selected_column = str(columns[next_column_index])
            column_index = next_column_index

    y_data = df[int(selected_column)]  # Change this line
    y_data = y_data.dropna()

    x_data = list(range(len(y_data)))
    # Create the figure
    figure = go.Figure()

    # Original data without the highlighted section
    original_trace = go.Scatter(x=x_data, y=y_data, mode='lines+markers',showlegend=False)

    # Add the original trace
    figure.add_trace(original_trace)

    for annotation in annotations:
        if annotation['column'] == selected_column:  # change 'col_name' to 'column'
            idx = annotation['index']
            lower_bound = max(0, idx - N)
            upper_bound = min(len(y_data), idx + N)

            # Highlighted section of the data
            highlighted_trace = go.Scatter(
                x=list(range(lower_bound, upper_bound)),
                y=y_data[lower_bound: upper_bound],
                mode='lines+markers',
                marker=dict(color='red'),  # Use marker to specify color for points
                showlegend=False
            )

            # Add the highlighted trace
            figure.add_trace(highlighted_trace)

    return figure, column_index, prev_clicks, next_clicks, selected_column

@app.callback(
    Output('annotations', 'data'),
    [Input('figure', 'clickData'),
     Input('load-button', 'n_clicks'),
     Input('upload-data', 'contents')],
    [State('annotations', 'data'),
     State('column-dropdown', 'value'),
     State('intermediate-data', 'data')])
def update_annotations(clickData, load_n_clicks, contents, annotations, selected_column, data):
    ctx = dash.callback_context

    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    # if the callback was triggered by 'upload-data', clear annotations
    if 'upload-data.contents' in [x['prop_id'] for x in ctx.triggered]:
        return []

    # if the callback was triggered by 'load-button', load annotations
    elif 'load-button.n_clicks' in [x['prop_id'] for x in ctx.triggered]:
        if load_n_clicks is None or data is None:
            raise dash.exceptions.PreventUpdate

        # Load annotations
        filename = data["filename"]
        try:
            with open(f'{filename}.pkl', 'rb') as f:
                annotations = pickle.load(f)
        except FileNotFoundError:
            annotations = []

    # else, the callback was triggered by 'figure.clickData', add the new annotation
    else:
        if clickData is None or selected_column is None:
            raise dash.exceptions.PreventUpdate

        clicked_x = clickData['points'][0]['x']
        clicked_y = clickData['points'][0]['y']

        new_annotation = {
            'index': clicked_x,  # change 'x' to 'index'
            'value': clicked_y,  # change 'y' to 'value'
            'column': selected_column  # change 'col_name' to 'column'
        }

        if new_annotation not in annotations:
            annotations.append(new_annotation)

    return annotations


@app.callback(
    Output('save-confirm', 'children'),
    Input('save-button', 'n_clicks'),
    State('annotations', 'data'),
    State('intermediate-data', 'data'))   # Use intermediate-data to get filename
def save_annotations(n_clicks, annotations, data):
    if n_clicks is None or data is None:
        raise dash.exceptions.PreventUpdate

    # extract filename from data
    filename = data['filename']
    with open(f'{filename}.pkl', 'wb') as f:
        pickle.dump(annotations, f)

    return f'Successfully saved annotations for {filename}'



if __name__ == '__main__':
    app.run_server(debug=True)
