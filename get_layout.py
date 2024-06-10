from dash import Dash, html, dash_table, ctx
from dash import dcc
from datetime import datetime as dt
import dash_leaflet as dl
import dash_mantine_components as dmc
import pandas as pd


LABELS = ['towards the sea/normal', 'looping in the port', 'looping at river mouth',
          'out from the port', 'out from the river', 'revolve on the sea',
          'stop outside the port', 'stop/tiny movement', 'large movement',
          'turn back movement', 'stop/return in the port']

LABELLED_DATA = pd.DataFrame(columns=['ppdata', 'date', 'label',
                                      'parent_id', 'hash', 'source_dataset'])

def convert_labels_to_radioitems(labels):
    list_of_items = []
    for lab in labels:
        list_of_items.append({'label': lab, 'value': lab})
    return list_of_items


def get_layout(default_location):
    header_component = html.Div([
        html.Div([], id='dummy_output', hidden=True),  # to be used as dummy output for the remove label button
        dcc.DatePickerRange(id='date_range_picker',
                            min_date_allowed=dt(2017, 1, 1),
                            max_date_allowed=dt(2024, 12, 31),
                            start_date=dt(2022, 4, 1),
                            end_date=dt(2022, 4, 7),
                            calendar_orientation='vertical',
                            ),
    ])
    map_component = html.Div([
        dl.Map([
            dl.TileLayer(),
            dl.LayerGroup(id='geomap_labelled_data', children=[]),
            dl.LayerGroup(id='geomap_data', children=[]),
            dl.LayerGroup(id='geomap_selected_data', children=[]),
        ], id='map', center=default_location, zoom=10, style={'height': '80vh'}),
        html.Div([dcc.RangeSlider(0, 1, 1,
                                  value=[],
                                  id='selected_time_range',
                                  disabled=True)]),
    ])
    labelling_component = html.Div([
        html.Div([
            html.Button('Assign label', id='assign_label_button', n_clicks=0),
            html.Div(id='label_summary', children=['No labelled data yet']),
            dcc.RadioItems(
                id='labels',
                options=convert_labels_to_radioitems(LABELS),
                value=False,
            )], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ])
    table_component = html.Div([
        dash_table.DataTable(data=LABELLED_DATA.to_dict('records'),
                             columns=[{"name": i, "id": i} for i in LABELLED_DATA.columns],
                             id='labelled_data_table',
                             row_selectable='single'),
    ])
    remove_component = html.Div([
        html.Button('Remove Label', id='remove_label_button', n_clicks=0),
        html.Button('Save', id='save_button', n_clicks=0),
        html.Div(id='save_feedback', children=[''])
    ])

    layout = dmc.Grid([
        dmc.Col(children=[header_component], span=10),
        dmc.Col(children=[], span=2),
        dmc.Col(children=[map_component], span=10),
        dmc.Col(children=[labelling_component], span=2),
        dmc.Col(children=[table_component], span=10),
        dmc.Col(children=[remove_component], span=2),
    ])

    return layout