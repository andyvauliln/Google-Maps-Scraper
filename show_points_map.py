import math
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from geopy.distance import geodesic
import os
from geopy.distance import distance

from dash_extensions import EventListener


selected_indices = []

csv_file = "measure_points_4.csv"

if os.path.exists(csv_file):
    try:
        measure_points = pd.read_csv(csv_file, index_col=False)
        if measure_points.empty:
            default_lat, default_lon = -8.3405, 115.0920
            measure_points = pd.DataFrame({"lat": [default_lat], "lon": [default_lon], "type": [
                "measure point"], "title": ["measure point"]})
    except Exception as e:
        print(f"Error while reading the CSV file: {e}")
        measure_points = pd.DataFrame(columns=["lat", "lon", "type", "title"])
else:
    print("CSV file not found. Creating a new DataFrame with a default point.")
    default_lat, default_lon = -8.3405, 115.0920
    measure_points = pd.DataFrame({"lat": [default_lat], "lon": [default_lon], "type": [
                                  "measure point"], "title": ["measure point"]})
    measure_points.to_csv(csv_file, index=False)

measure_points['type'] = 'measure point'
measure_points['title'] = 'measure point'


def set_places(points):
    points['size'] = 1000
    points['color'] = 1

    global fig
    fig = px.scatter_mapbox(points,
                            lat="lat",
                            lon="lon",
                            hover_name="title",
                            hover_data=["title", "size"],
                            color='type',
                            size="size",
                            zoom=10,
                            height=800,
                            width=1200)

    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update_layout(clickmode='event+select')
    fig.update_traces(
        marker=dict(size=10),
        unselected=dict(marker=dict(opacity=0.3))
    )
    global measure_points
    measure_points = points
    return fig


fig = set_places(measure_points)
app = dash.Dash(__name__)


def save_updated_measure_points():
    print("***********SAVED*********")
    global measure_points
    print(len(measure_points))
    global fig
    measure_points.to_csv("generatedPoints/measure_points.csv", index=False)
    return fig


@app.callback(
    Output("map", "figure"),
    [
        Input("delete_button", "n_clicks"),
        Input("save_button", "n_clicks"),
        Input("add_points_button", "n_clicks"),
    ],
    [
        State("map", "selectedData"),
    ],
    prevent_initial_call=True,
)
def update_map(delete_clicks, save_clicks, add_clicks, selected_data):
    global selected_indices
    if selected_data is None:
        selected_indices = []
    else:
        selected_indices = [point["pointIndex"]
                            for point in selected_data["points"]]

    ctx = dash.callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if input_id == "delete_button":
        return delete_points(selected_data)
    elif input_id == "save_button":
        return save_updated_measure_points()
    elif input_id == "add_points_button":
        return add_points(selected_data)
    return dash.no_update


def delete_points(selected_data):
    global measure_points
    if selected_data is not None:
        indices_to_remove = [point["pointIndex"]
                             for point in selected_data["points"]]
        measure_points.drop(indices_to_remove, inplace=True, errors='ignore')
        measure_points.reset_index(drop=True, inplace=True)
        updated_fig = set_places(measure_points)
        return updated_fig

    return dash.no_update


def generate_points_in_area(min_lat, max_lat, min_lon, max_lon, distance_km):
    points = []

    lat_distance = geodesic((min_lat, min_lon), (max_lat, min_lon)).km
    lon_distance = geodesic((min_lat, min_lon), (min_lat, max_lon)).km

    num_points_lat = int(lat_distance // distance_km) + 1
    num_points_lon = int(lon_distance // distance_km) + 1

    try:
        lat_step = (max_lat - min_lat) / (num_points_lat - 1)
    except ZeroDivisionError:
        lat_step = 0
    try:
        lon_step = (max_lon - min_lon) / (num_points_lon - 1)
    except ZeroDivisionError:
        lon_step = 0

    points = []
    for i in range(num_points_lat):
        for j in range(num_points_lon):
            lat = min_lat + i * lat_step
            lon = min_lon + j * lon_step
            points.append(
                {"lat": lat, "lon": lon, "type": "measure point", "title": "measure point"})

    return points


def add_points(selected_data):
    if (selected_data is not None):
        if "lassoPoints" in selected_data and selected_data["lassoPoints"] is not None:
            lasso_points = selected_data["lassoPoints"]["mapbox"]
            min_lat, max_lat = min([point[1] for point in lasso_points]), max(
                [point[1] for point in lasso_points])
            min_lon, max_lon = min([point[0] for point in lasso_points]), max(
                [point[0] for point in lasso_points])
        if "range" in selected_data and selected_data["range"] is not None:
            rangepoints = selected_data["range"]["mapbox"]
            min_lat, max_lat = min([point[1] for point in rangepoints]), max(
                [point[1] for point in rangepoints])
            min_lon, max_lon = min([point[0] for point in rangepoints]), max(
                [point[0] for point in rangepoints])

        points = generate_points_in_area(
            min_lat, max_lat, min_lon, max_lon, 0.15)

        # Add new point to measure_points DataFrame
        global measure_points
        measure_points = measure_points.append(points, ignore_index=True)

        # Update the map
        set_places(measure_points)
        global fig
        return fig
    return dash.no_update


@app.callback(
    Output('num_points', 'children'),
    Input('map', 'figure')
)
def update_num_points(_):
    return f'Number of points: {len(measure_points)}'


# Layout
app.layout = html.Div([
    html.H1("Google  Map Points"),
    html.P(id='num_points'),
    html.Button("Add Points to Selected Area",
                id="add_points_button"),
    html.Button("Delete Selected Points", id="delete_button"),
    html.Button("Save Selected Points", id="save_button"),
    dcc.Graph(id="map", figure=fig),
    EventListener("keydown", id="keydown_listener")
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
