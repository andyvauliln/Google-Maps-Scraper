import re
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json
import numpy as np
import dash_bootstrap_components as dbc

fig = None

with open('data/top_places_by_type.json') as f:
    data = json.load(f)


df = pd.DataFrame(data)
df['lat'] = df['location'].apply(lambda x: x['lat'])
df['lng'] = df['location'].apply(lambda x: x['lng'])
df['link'] = 'https://www.google.com/maps/place/?hl=en&q=place_id:' + df['place_id']

types = df['types'].apply(lambda x: pd.Series(
    [1]*len(x), index=x)).fillna(0, downcast='infer')
df = df.join(types)

colors = ['blue', 'green', 'orange', 'yellow', 'purple']
buttons = [dict(args=[{"visible": [color == c for c in colors]}],
                label=color, method="update") for color in colors]
buttons.append(
    dict(args=[{"visible": [True for c in colors]}], label="All", method="update"))

updatemenus = list([dict(active=-1, buttons=list(buttons))])

color_explanation = {
    "blue": '0',
    "green": '< 10',
    # 'red': "closed",
    "orange": '10-50',
    "yellow": '50-200',
    "purple": '> 200',
}


def set_places(points):

    df_copy = points.copy()
    df_copy['size'] = 5
    df_copy.loc[df_copy['user_ratings_total'] < 10, 'size'] = 10
    df_copy.loc[(df_copy['user_ratings_total'] >= 10) & (
        df_copy['user_ratings_total'] < 50), 'size'] = 20
    df_copy.loc[(df_copy['user_ratings_total'] >= 50) & (
        df_copy['user_ratings_total'] < 200), 'size'] = 30
    df_copy.loc[df_copy['user_ratings_total'] >= 200, 'size'] = 40
    df_copy['color'] = 'blue'
    df_copy.loc[df_copy['user_ratings_total'] < 10, 'color'] = 'green'
    df_copy.loc[(df_copy['user_ratings_total'] >= 10) & (
        df_copy['user_ratings_total'] < 50), 'color'] = 'yellow'
    df_copy.loc[(df_copy['user_ratings_total'] >= 50) & (
        df_copy['user_ratings_total'] < 200), 'color'] = 'orange'
    df_copy.loc[df_copy['user_ratings_total'] >= 200, 'color'] = 'purple'
    # df_copy.loc[df_copy['business_status'] ==
    #             'CLOSED_TEMPORARILY', 'color'] = 'red'

    fig = px.scatter_mapbox(df_copy, lat="lat", lon="lng", hover_name="name",
                            hover_data=["name", "place_id", "link", "business_status",
                                        "types", "vicinity", "rating", "user_ratings_total", "compound_code"],
                            color_discrete_map='identity', color='color', size='size', zoom=10, height=800, width=1200)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return df_copy, fig


df, fig = set_places(df)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


@app.callback(
    Output('display-info', 'children'),
    [Input('map', 'clickData')]
)
def display_click_data(clickData):
    if clickData is None:
        return 'Click on a point to see more information.'
    else:
        point_info = clickData.get('points')
        if point_info is not None:
            point_info = point_info[0]
            place_id = point_info.get('customdata')
            if place_id is not None:
                place_id = place_id[1]
                return [html.Div([
                    html.P([html.Label('Place Info:', style={
                        'fontWeight': 'bold'})]),
                    html.A(f"Google Maps Link: {point_info['customdata'][0]}",
                           href=point_info['customdata'][2], target="_blank"),
                    html.P(f"Name: {point_info['hovertext']}"),
                    html.P(f"Place ID: {place_id}"),
                    html.P(f"Status: {point_info['customdata'][3]}"),
                    html.P(f"Types: {point_info['customdata'][4]}"),
                    html.P(f"Vicinity: {point_info['customdata'][5]}"),
                    html.P(f"Rating: {point_info['customdata'][6]}"),
                    html.P(f"Reviews: {point_info['customdata'][7]}"),
                    html.P(f"Compound Code: {point_info['customdata'][8]}")
                ])]
        return 'Click on a point to see more information.'


@app.callback(
    Output('display-count', 'children'),
    Input('map', 'figure')
)
def update_display_count(figure):
    total_count = 0
    for trace in figure['data']:
        total_count += len(trace['lon'])
    return f"Number of places shown: {total_count}"


@app.callback(
    Output('map', 'figure'),
    Input('category_selector', 'value'),
    Input('search_name', 'value'),
    Input('type_selector', 'value')
)
def update_map(categories, name, types):
    global fig
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    filtered_df = df.copy()

    if trigger_id in ['category_selector', 'search_name', 'type_selector']:
        if categories:
            filtered_df = filtered_df[filtered_df['color'].isin(categories)]
        if name:
            filtered_df = filtered_df[filtered_df['name'].str.contains(
                re.escape(name), case=False)]
        if types:
            filtered_df = filtered_df[filtered_df[types].any(axis=1)]
        _, fig = set_places(filtered_df)
    return fig


app.layout = html.Div([
    dbc.Row([
        dbc.Col(
            dcc.Graph(id='map', figure=fig),
            width=8
        ),
        dbc.Col([
            html.Div(f"Total places: {len(df)}", id='total-count',
                     style={'marginBottom': 5, 'marginTop': 5, 'fontWeight': 'bold'}),
            html.Div(id='display-count',
                     style={'marginBottom': 5, 'marginTop': 5, 'fontWeight': 'bold'}),

            dbc.Row([
                html.Div([
                    html.Label('Search by name:', style={
                               'fontWeight': 'bold'}),
                    dcc.Input(id='search_name', type='text', value='',
                              style={'width': '100%', 'marginBottom': 25})
                ])
            ]),
            html.Div([
                html.Label('Category Selector', style={'fontWeight': 'bold'}),
                dcc.Checklist(
                    id='category_selector',
                    options=[
                        {'label': f" {i} ({color_explanation.get(i, 'No explanation')})", 'value': i}
                        for i in df['color'].unique()
                    ],
                    style={
                        'border': '1px solid #ccc',
                        'padding': '10px',
                        'border-radius': '5px',
                        'background-color': '#f9f9f9',
                        'margin-bottom': '10px'
                    },
                    value=df['color'].unique()
                )
            ]),
            dbc.Row([
                html.Div([
                    html.Label('Type Selector:', style={'fontWeight': 'bold'}),
                    dcc.Dropdown(
                        id='type_selector',
                        options=[{'label': i, 'value': i}
                                 for i in types.columns],
                        multi=True,
                        style={'width': '100%', 'marginBottom': 15}
                    )
                ])
            ]),
            dbc.Row([
                html.Div(id='display-info',
                         style={'marginBottom': 50, 'marginTop': 15})
            ]),
        ], width=4)
    ])
])


if __name__ == '__main__':
    print(len(data), "length")
    app.run_server(debug=True, port=8051)
