import copy

# import dash
from dash import Dash, html, dash_table, ctx
import pandas as pd
import numpy as np
# import json
# from dash import dcc
from dash.dependencies import Input, Output, State
# from datetime import datetime as dt
# from plotly import graph_objs as go
# from plotly.graph_objs import *
# import plotly.express as px
import dash_leaflet as dl
# import pickle
# from tqdm import tqdm
from dash.exceptions import PreventUpdate
from datetime import datetime
# import dash_mantine_components as dmc
from get_layout import get_layout, LABELS, LABELLED_DATA

UNSELECTED_COLOR = "#3EEDE7"
PICKED_COLOR = "#00E500"
MARKER_RADIUS = 3
MARKER_COLOR = "#000000"
PICKED_MARKER_RADIUS = 6
PICKED_MARKER_COLOR = "#00E500"

SELECTED_COLOR = "#003371"
LABELLED_COLOR = "#FF461F"

DATA_PATH = './pd_database.pkl'

# def ts2dt(ts):
#     m = datetime.fromtimestamp(ts)
#     res = m.strftime('%Y-%m-%d %H:%M:%S')
#     return res


# def trajectory_gen(databse_file):
#     df = pd.read_hdf(databse_file)
#     ppdata = df['ppdata']
#     all_traj_list = []
#     all_time_list = []
#     for i in tqdm(range(len(ppdata))):
#         x = ppdata.loc[i]
#         latlng = x[:, :2]
#         time = x[:, 5]
#         single_time_list = []
#         single_track_list = []
#
#         for i in range(len(latlng)):
#             y = latlng[i]
#             single_track_list.append(y)
#
#         for t in range(len(time)):
#             ts = ts2dt(time[t])
#             single_time_list.append(ts)
#         all_traj_list.append(single_track_list)
#         all_time_list.append(single_time_list)
#
#     return all_traj_list, all_time_list


# load toy data
# traj_list, time_list = trajectory_gen('./pd_database.h5')
data = pd.read_pickle(DATA_PATH)
default_location = []
for i, row in data.iterrows():
    default_location.append(np.mean(row['ppdata'], axis=0))
default_location = np.mean(default_location, axis=0)

# The traj_list for the database
# for i in tqdm(range(len(traj_list))):
#     data.loc[i] = {'ppdata': np.array(traj_list[i]), 'date': time_list[i]}

# data.loc[0] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])}
# data.loc[1] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])+0.01}
# data.loc[2] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])-0.05}
# data.loc[3] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])+0.03}
# data.loc[4] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])-0.005}

# data.loc[0] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]]),
#                'date': ['2022-08-23 16:58:05', '2022-12-23 16:59:05', '2023-08-20 16:59:35']}
# data.loc[1] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])+0.01,
#                'date': ['2022-08-24 16:58:05', '2022-12-24 16:59:05', '2023-08-21 16:59:35']}
# data.loc[2] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])-0.05,
#                'date': ['2022-08-25 16:58:05', '2022-12-25 16:59:05', '2023-08-22 16:59:35']}
# data.loc[3] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])+0.03,
#                'date': ['2022-08-26 16:58:05', '2022-12-26 16:59:05', '2023-08-23 16:59:35']}
# data.loc[4] = {'ppdata': np.array([[57, 10], [57, 11], [56, 11]])-0.005,
#                'date': ['2022-08-27 16:58:05', '2022-12-27 16:59:05', '2023-08-24 16:59:35']}

# # generate polylines
# polylines_children = []
# for i, row in data.iterrows():
#     polylines_children.append(
#         dl.Polyline(positions=row['ppdata'], color=UNSELECTED_COLOR, weight=3)
#     )

# this is the basic app, but it doesn not allow you to have different callbacks poiting to same output
app = Dash(__name__)
app.layout = get_layout(default_location=default_location)
app.title = 'Vessel Track Annotation'
server = app.server


def convert_datetime(start_date, end_date):
    if 'T' in start_date:
        start_date = start_date[:start_date.find('T')]
    if 'T' in end_date:
        end_date = end_date[:end_date.find('T')]
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    return start_date, end_date


# The date selection callback related to the overall map display
@app.callback(Output('geomap_data', 'children'),
              [Input('date_range_picker', 'start_date'),
               Input('date_range_picker', 'end_date')],
              prevent_initial_callbacks=True)
def date_selection(start_date, end_date):
    # if start_date and end_date:
    picked_children = []
    POLYLINE_PICKED = []
    start_date, end_date = convert_datetime(start_date, end_date)
    for i, row in data.iterrows():
        # we assume data rows do not span over multiple days
        if row['date'][0] >= start_date and row['date'][-1] <= end_date:
            polyline = dl.Polyline(positions=row['ppdata'].tolist(),
                                   color=PICKED_COLOR,
                                   weight=4,
                                   opacity=0.3)
            marker = dl.CircleMarker(center=row['ppdata'][-1, :],
                                     radius=MARKER_RADIUS,
                                     color=MARKER_COLOR)
            picked_children.append(polyline)
            picked_children.append(marker)
            POLYLINE_PICKED.append((row['ppdata'], row['date']))

        global PICKED_TRACK
        PICKED_TRACK = POLYLINE_PICKED

    global SELECTED_TRACK, SELECTED_POS
    SELECTED_TRACK = None
    SELECTED_POS = None

    return picked_children

# This callback allows the user to click on a polyline and change its color.
@app.callback([Output('geomap_selected_data', 'children'),
               Output('selected_time_range', 'disabled'),
               Output('selected_time_range', 'min'),
               Output('selected_time_range', 'max'),
               Output('selected_time_range', 'value'),
               Output('selected_time_range', 'step')],
              [Input('map', 'clickData'),
               Input('selected_time_range', 'value'),
               Input('labelled_data_table', 'selected_row_ids')],
              prevent_initial_callbacks=True)
def display_click_data(clickData, time_range, selected_row_id):
    button_clicked = ctx.triggered_id
    if button_clicked == 'map' or button_clicked == 'selected_time_range':

        dist = ()
        for track in PICKED_TRACK:
            marker_position = track[0][-1, :]
            dist = dist + (np.linalg.norm(marker_position - np.array([clickData['latlng']['lat'], clickData['latlng']['lng']])),)
        pos = np.argmin(dist)

        MIN = 0

        # MAX = data.loc[pos, 'ppdata'].shape[0] - 1
        MAX = PICKED_TRACK[pos][0].shape[0] - 1

        # step = data.loc[pos, 'ppdata'].shape[0] / 20
        step = PICKED_TRACK[pos][0].shape[0] / 20

        if step < 1:
            STEP = 1
        else:
            STEP = int(step)

        if len(time_range) == 0:  # useful at the beginning
            SELECTED_TIME = range(PICKED_TRACK[pos][0].shape[0])
            VALUE = [MIN, MAX+1]

        if button_clicked == 'selected_time_range':  # useful when the user clicks on the range slider
            SELECTED_TIME = range(time_range[0], time_range[1]+1)
            VALUE = time_range

        if button_clicked == 'map':
            SELECTED_TIME = range(MAX+1)
            VALUE = [MIN, MAX+1]

        if SELECTED_TIME != range(MIN, MAX+1) and button_clicked != 'selected_time_range':
            SELECTED_TIME = range(MIN, MAX+1)

        selected_children = [dl.Polyline(positions=PICKED_TRACK[pos][0][SELECTED_TIME, :],
                                         color=SELECTED_COLOR, weight=3),
                             dl.CircleMarker(center=PICKED_TRACK[pos][0][SELECTED_TIME, :][-1, :],
                                             radius=PICKED_MARKER_RADIUS,
                                             color=PICKED_MARKER_COLOR)]

        global SELECTED_TRACK, SELECTED_POS
        SELECTED_TRACK = (PICKED_TRACK[pos][0][SELECTED_TIME, :],
                          PICKED_TRACK[pos][1][SELECTED_TIME])
        SELECTED_POS = pos

        return selected_children, False, MIN, MAX, VALUE, STEP

    elif button_clicked == 'labelled_data_table':
        if selected_row_id is not None:
            if len(selected_row_id) == 1:
                global TO_REMOVE_ID
                TO_REMOVE_ID = selected_row_id
                selected_children = [dl.CircleMarker(center=LABELLED_DATA.loc[selected_row_id[0], 'ppdata'][-1, :],
                                                     radius=PICKED_MARKER_RADIUS+8)]

                return selected_children, True, 0, 1, [], 1

    raise PreventUpdate


# This callback allows the user to assign a label to selected track
@app.callback([Output('label_summary', 'children'),
               Output('geomap_labelled_data', 'children'),
               Output('labelled_data_table', 'data')],
              [Input('assign_label_button', 'n_clicks'),
               Input('remove_label_button', 'n_clicks'),
               Input('date_range_picker', 'start_date'),
               Input('date_range_picker', 'end_date')],
              [State(component_id='labels', component_property='value')],
              prevent_initial_callbacks=True)
def assign_label(click_to_assign, click_to_remove, start_date, end_date, label):
    button_clicked = ctx.triggered_id
    if button_clicked:
        global SELECTED_TRACK, SELECTED_POS, LABELLED_DATA
        if button_clicked == 'assign_label_button':
            if isinstance(SELECTED_TRACK[0], np.ndarray):
                if isinstance(label, str):
                    dist_row = {'ppdata': SELECTED_TRACK[0],
                                'date': SELECTED_TRACK[1],
                                'label': label,
                                'parent_id': SELECTED_POS,
                                'source_dataset': DATA_PATH,
                                'hash': hash(SELECTED_TRACK[0].tostring())
                                }
                    LABELLED_DATA = LABELLED_DATA.append(dist_row, ignore_index=True)

                    # remove duplicated labels
                    LABELLED_DATA = LABELLED_DATA.drop_duplicates(subset=['hash'], keep='last')

        elif button_clicked == 'remove_label_button':
            global TO_REMOVE_ID
            LABELLED_DATA = LABELLED_DATA.drop(index=TO_REMOVE_ID)

    # update map with labelled data
    start_date, end_date = convert_datetime(start_date, end_date)
    polylines_children = []
    for i, row in LABELLED_DATA.iterrows():
        if row['date'][0] >= start_date and row['date'][-1] <= end_date:
            polylines_children.append(
                dl.Polyline(positions=row['ppdata'],
                            color=LABELLED_COLOR,
                            weight=16, opacity=0.2)
            )

    # refine what to display in table
    TABLE_CONTENT = copy.deepcopy(LABELLED_DATA)
    TABLE_CONTENT = TABLE_CONTENT.reset_index()
    TABLE_CONTENT = TABLE_CONTENT.rename(columns={'index': 'id'})
    TABLE_CONTENT['ppdata'] = '...'
    for i, row in TABLE_CONTENT.iterrows():
        TABLE_CONTENT.at[i, 'date'] = f'{row["date"][0]} to {row["date"][-1]}'
    TABLE_CONTENT = TABLE_CONTENT.to_dict('records')

    return [f'Number of labels = {len(LABELLED_DATA)}'], polylines_children, TABLE_CONTENT


# this callback is to save labelled data to disk
@app.callback(Output('save_feedback', 'children'),
              Input('save_button', 'n_clicks'),
              prevent_initial_callbacks=True)
def save_session(click):
    if click:
        now = datetime.now()
        name = now.strftime("%Y-%m-%d-%H-%M-%S")
        filename = f'labelled_data_{name}.pkl'
        LABELLED_DATA.to_pickle(filename, protocol=-1)
        # TODO: labelled data should also contain fields! Correct ones!
        return f'Saved to {filename}'
    raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=False, port=8051)