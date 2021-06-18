import datetime as dt
import json
from dash_bootstrap_components._components.Card import Card
from dash_bootstrap_components._components.Row import Row
from numpy import source
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output
import warnings
from secret import mapbox_api_token
import datetime
import os
import io
from io import BytesIO
import requests
from ibm_botocore.client import Config
import ibm_boto3

app = dash.Dash(__name__, suppress_callback_exceptions=True, update_title='Hang tight seasurfer...', external_stylesheets=[dbc.themes.BOOTSTRAP])


##### COS FUNCTION start #####

#path ='C:/Users/NandiniGoyal/Desktop/UnfavourableData/'
COS_ENDPOINT = "https://s3.au-syd.cloud-object-storage.appdomain.cloud"
COS_API_KEY_ID = "NGKuasW1MkfjyEHLTaQCljOQJpQfuFwcomtvfQupI2-4"
COS_AUTH_ENDPOINT = "https://iam.cloud.ibm.com/identity/token"
COS_RESOURCE_CRN = "crn:v1:bluemix:public:cloud-object-storage:global:a/3c4240bac2774d79ae700f7e2f790508:283e8562-557f-4fac-82ce-62b9c112cf18:bucket:cognitivehackathon"
#COS_BUCKET_LOCATION = "au-syd-standard"

# Create client 
client = ibm_boto3.client("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

# Create resource
cos = ibm_boto3.resource("s3",
    ibm_api_key_id=COS_API_KEY_ID,
    ibm_service_instance_id=COS_RESOURCE_CRN,
    config=Config(signature_version="oauth"),
    endpoint_url=COS_ENDPOINT
)

def data_import(df_chunk):
    """Helper function does the data import as a chunk"""
    chunk_list = []
    for chunk in df_chunk:
        chunk_list.append(chunk)
    df_concat = pd.concat(chunk_list)
    return df_concat

def cloud_connection(cos,bucket_name,key):
    obj = cos.Object(bucket_name, key).get()
    obj_bytes = obj['Body'].read() # .read() returns a byte string
    obj_bytes_stream = io.BytesIO(obj_bytes) # that we convert to a stream
    data = pd.read_csv(obj_bytes_stream,chunksize=10000,encoding='unicode_escape')
    return data


##### cos function end #####


#### city graphs start #####

# erosion = pd.read_csv("land_data/Soil Erosion.csv")
# texture = pd.read_csv("land_data/Soil Texture.csv")
# productivity = pd.read_csv("land_data/Soil Productivity.csv")

data = cloud_connection(cos, 'cognitivehackathon', 'Soil Erosion.csv') 
erosion = data_import(data)
erosion = erosion.astype(str)
erosion['% Land Area Covered'] = erosion['% Land Area Covered'].astype(float)

data = cloud_connection(cos, 'cognitivehackathon', 'Soil Texture.csv') 
texture = data_import(data)
texture = texture.astype(str)
texture['% Land Area Covered'] = texture['% Land Area Covered'].astype(float)

data = cloud_connection(cos, 'cognitivehackathon', 'Soil Productivity.csv') 
productivity = data_import(data)
productivity = productivity.astype(str)
productivity['% Land Area Covered'] = productivity['% Land Area Covered'].astype(float)

# waste_data = pd.read_csv('waste_data/Waste.csv')
# ground_water = pd.read_csv("ground_water_data/Ground Water.csv")

data = cloud_connection(cos, 'cognitivehackathon', 'Waste.csv') 
waste_data = data_import(data)
waste_data = waste_data.astype(str)
waste_data['Population'] = waste_data['Population'].astype(float)
waste_data['Per capita waste generation (kg/day)'] = waste_data['Per capita waste generation (kg/day)'].astype(float)

data = cloud_connection(cos, 'cognitivehackathon', 'Ground Water.csv') 
ground_water = data_import(data)
ground_water = ground_water.astype(str)
ground_water['Current Level (m bgl)'] = ground_water['Current Level (m bgl)'].astype(float)

air_quality = pd.read_csv("air_quality/aq.csv")

air_quality = air_quality.dropna()

def aq_color(row):
    return 1 if row['AQI']>100 else 0

air_quality['color_coding'] = air_quality.apply(lambda row: aq_color(row), axis=1)

air_quality['Date'] = pd.to_datetime(air_quality['Date'], format="%d-%m-%Y")

air_quality = air_quality.sort_values('Date')

#### city graphs end #####


#city dropdown options

options = [
    {'label': 'Delhi', 'value': 'Delhi'},
    {'label': 'Mumbai', 'value': 'Mumbai'},
    {'label': 'Bengaluru', 'value': 'Bengaluru'},
    {'label': 'Kolkata', 'value': 'Kolkata'},
    {'label': 'Jaipur', 'value': 'Jaipur'}
]

# url = "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=b4dc986918e043939e4111312211606 &q=Bangalore&num_of_days=1&tp=24&format=json&aqi=yes&alerts=yes"
# payload="<file contents here>"
# headers = {
#   'Content-Type': 'text/plain'
# }
# response = requests.request("GET", url, headers=headers, data=payload)
# print(response.text)

api_token = 'pk.eyJ1Ijoic2h1YmhhbTd5YWRhdiIsImEiOiJja3AxbjBvM2QxY3Z0MzBxdXhuZXh2NGJuIn0.clGLe_gtAyFkk2G9yZ9YXg'


###### rivers part ########

river_options = [
    {'label':'Ganga', 'value': 'Ganga'},
    {'label': 'Yamuna', 'value': 'Yamuna'},
    {'label': 'Cauvery', 'value': 'Cauvery'}
]

selected_points_ganga = [2725, 1061, 1062, 2490, 1146, 1147, 1046, 2485, 1073, 2551, 3114, 1079,1815, 1819, 1080, 1472, 1471, 1469]

data = cloud_connection(cos, 'cognitivehackathon', 'ganga_selected_points.csv') 
location_coordinates_df = data_import(data)
location_coordinates_df = location_coordinates_df.astype(str)

data = cloud_connection(cos, 'cognitivehackathon', 'ganga_2019.csv') 
ganga_2019 = data_import(data)
ganga_2019 = ganga_2019.astype(str)

data = cloud_connection(cos, 'cognitivehackathon', 'ganga_2018.csv') 
ganga_2018 = data_import(data)
ganga_2018 = ganga_2018.astype(str)

data = cloud_connection(cos, 'cognitivehackathon', 'ganga_2017.csv') 
ganga_2017 = data_import(data)
ganga_2017 = ganga_2017.astype(str)

data = cloud_connection(cos, 'cognitivehackathon', 'ganga_2016.csv') 
ganga_2016 = data_import(data)
ganga_2016 = ganga_2016.astype(str)

data = cloud_connection(cos, 'cognitivehackathon', 'ganga_2015.csv') 
ganga_2015 = data_import(data)
ganga_2016 = ganga_2016.astype(str)


# ganga_2019 = pd.read_csv('rivers/ganga_preprocessed/ganga_2019.csv')
# ganga_2018 = pd.read_csv('rivers/ganga_preprocessed/ganga_2018.csv')
# ganga_2017 = pd.read_csv('rivers/ganga_preprocessed/ganga_2017.csv')
# ganga_2016 = pd.read_csv('rivers/ganga_preprocessed/ganga_2016.csv')
# ganga_2015 = pd.read_csv('rivers/ganga_preprocessed/ganga_2015.csv')

location_coordinates_df['location_id'] = location_coordinates_df['location_id'].astype(int)
location_coordinates_df['latitude'] = location_coordinates_df['latitude'].astype(float)
location_coordinates_df['longitude'] = location_coordinates_df['longitude'].astype(float)

ganga_2018['STATION CODE'] = ganga_2018['STATION CODE'].astype(int)
ganga_2018['wqi'] = ganga_2018['wqi'].astype(float)
ganga_2018['PH'] = ganga_2018['PH'].astype(float)
ganga_2018['DO'] = ganga_2018['DO'].astype(float)
ganga_2018['BOD'] = ganga_2018['BOD'].astype(float)
ganga_2018['CONDUCTIVITY'] = ganga_2018['CONDUCTIVITY'].astype(float)

ganga_2019.index = ganga_2019['STATION CODE']
ganga_2018.index = ganga_2018['STATION CODE']
ganga_2017.index = ganga_2017['STATION CODE']
ganga_2016.index = ganga_2016['STATION CODE']
ganga_2015.index = ganga_2015['STATION CODE']


fig_rivers = go.Figure(go.Scattermapbox(
    mode = "markers+lines+text",
    lon = location_coordinates_df["longitude"],
    lat=location_coordinates_df["latitude"],
    marker=go.scattermapbox.Marker(
            size=13,
            color=ganga_2018.loc[location_coordinates_df['location_id'].values]['wqi'],
            opacity=0.7,
            colorscale=[(0.00, "red"),   (0.25, "red"),
                                          (0.25, "orange"), (0.75, "orange"),
                                          (0.75, "green"),  (1.0, "green")],
            showscale=True
        ),
    text = list(ganga_2018.loc[location_coordinates_df['location_id'].values]['STATION NAME'] + '   :   ' + ganga_2018.loc[location_coordinates_df['location_id'].values]['wqi'].astype(str)),
    textposition='top right',
    textfont=dict(size=12, color='black'),
    )
)

fig_rivers.update_layout(
    margin ={'l':10,'t':10,'b':10,'r':10},
    font_size=16,  title={'xanchor': 'center','yanchor': 'top', 'y':0.9, 'x':0.5,}, 
    title_font_size = 24,
    mapbox=dict(
        accesstoken=api_token, 
        style = "mapbox://styles/shubham7yadav/ckpy4asr5034u17mblroogx7v",
        center=dict(
            lat=24.607490,
            lon=78.289735,
        ),
        zoom=4.0
    ),
    height = 1000, width = 1000,
    showlegend=False
)

###### rivers part end ####

###### sustainability status start ####

sustainability_status = {
    "Bengaluru": "Medium",
    "Delhi": "High",
    "Jaipur": "Medium",
    "Mumbai": "Medium",
    "Kolkata": "High-Medium"
}


###### sustainability status end #####




# layout
tab_1 = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Select City'),   
                dbc.CardBody([
                    dcc.Dropdown(
                        id='city',
                        options=options,
                        clearable=False,
                        value='Bengaluru'
                    ),
                    html.Div(children=[
                        
                    ], id='city-sustainability-status', style={'textAlign': 'center'})
                ]),
            ], style={'margin': '5px'}, className='w-100', color='rgba(66, 235, 192, 0.35)'),
            dbc.Card([
                dbc.CardHeader(id='real-time-city-details', children=['City Details']),   
                dbc.CardBody([
                    html.Div([
                        dcc.Graph(id="city-temp"),
                        dcc.Graph(id="city-aq"),
                        dcc.Graph(id="city-humidity"),
                        dcc.Graph(id="city-uv"),
                        dcc.Graph(id="city-precipitation")
                    ])
                ]),
            ], style={'margin': '5px'}, className='w-100', color='rgba(66, 235, 192, 0.35)')
        ], width=3),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.H3("Temperature", style={"font-size": "18px"}),
                    dcc.Graph(id="city-temp-historical")
                ], width=6),
                dbc.Col([
                    html.H3("Rainfall", style={"font-size": "18px"}),
                    dcc.Graph(id="city-rainfall-historical")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("Air Quality", style={"font-size": "18px"}),
                    dcc.Graph(id="city-aq-historical")
                ], width=6),
                dbc.Col([
                    html.H3("Ground Water Quality", style={"font-size": "18px"}),
                    dcc.Graph(id="city-groundwater-historical")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("Waste", style={"font-size": "18px"}),
                    dcc.Graph(id="city-waste-historical")
                ], width=6),
                dbc.Col([
                    html.H3("Soil Erosion", style={"font-size": "18px"}),
                    dcc.Graph(id="city-land-erosion-historical")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.H3("Land Coverage", style={"font-size": "18px"}),
                    dcc.Graph(id="city-land-covered-historical")
                ], width=6),
                dbc.Col([
                    html.H3("Soil Texture", style={"font-size": "18px"}),
                    dcc.Graph(id="city-land-texture-historical")
                ], width=6)
            ])
        ], width=9)
    ]),
    dbc.Row([
        
    ])
], style={'margin-top': '5px', 'margin-right': '2px'})


tab_2 = html.Div([
    dbc.Row([
        html.Img(src="assets/covid_banner.png", style={"width":"100%"}),
        html.Br(),
        html.Div([
            dcc.Link("Navigate to Earthquale Data", href="https://www.volcanodiscovery.com/earthquakes/india.html", target="_blank" ),
            html.Img(src="assets/earthquake.png", style={"width":"50%"}),            
        ], style={"width":"100%", 'textAlign': 'center', "margin-top": "50px"}),
        html.Div([
            dcc.Link("Navigate to Cyclone Data", href="https://mausam.imd.gov.in/imd_latest/contents/cyclone.php", target="_blank" ),
            html.Img(src="assets/cyclone.png", style={"width":"50%"}),
        ], style={"width":"100%", 'textAlign': 'center', "margin-top": "50px"})
    ])
])


tab_3 = html.Div([dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader('Select River'),   
                dbc.CardBody([
                    dcc.Dropdown(
                        id='river',
                        options=river_options,
                        clearable=False,
                        value='Ganga'
                    ),
                ]),
            ], style={'margin': '5px'}, className='w-100', color='rgba(168, 215, 255, 0.35)'),
            html.Div(id='river-states'),
            html.Div(id='river-state-details')
        ], width=4),
        dbc.Col([
            dbc.Row([
                dcc.Graph(figure=fig_rivers)
            ])
        ], width=8)
    ]),
    dbc.Row([
        
    ])
],style = {"overflow-y":"auto", })        






tab_height = '5vh'


app.layout = dbc.Container([
    html.Div([
        dbc.Row([
            dbc.Col([
                html.Img(src="/assets/evs_logo.gif", style={'height':'15vh', 'width':'auto'})
            ], width=3),
            dbc.Col([], width=6),
            dbc.Col([
                html.Img(src="/assets/ibm_logo.png", style={'height':'15vh', 'width':'auto', 'text-align': 'right'})
            ], width=3)
        ])
    ], style={'margin-top': '6px', 'margin-bottom': '6px', 'margin-left': '7vh'}),
    dcc.Tabs([
        dcc.Tab(label='Elements Analysis', value='tab-1', children=[tab_1], style={'padding': '0', 'line-height': tab_height, 'font-size': '20px'}, selected_style={'font-size': '20px','padding': '0','line-height': tab_height}),
        dcc.Tab(label='Alert', value='tab-2', children=[tab_2],style={'padding': '0', 'line-height': tab_height, 'font-size': '20px'}, selected_style={'font-size': '20px','padding': '0','line-height': tab_height}),
        dcc.Tab(label='River Analysis', value='tab-3',children=[tab_3], style={'padding': '0', 'line-height': tab_height, 'font-size': '20px'}, selected_style={'font-size': '20px','padding': '0','line-height': tab_height})
    ], colors={
        "border":  "rgb(26,92,75,0.75)",
        "primary":  "rgb(26,92,75,0.75)",
        "background":  "rgb(26,92,75,0.75)"
    }, style={
        # 'width': '50%',
        # 'font-size': '200%',
        'color': '#fff',
        'height': tab_height}),
], fluid=True) 






@app.callback(Output('river-states', 'children'),
                [Input(component_id='river', component_property='value')])
def create_states_selector(river):
    river_states = ganga_2018['STATE'].unique()
    river_states_options = list()
    for state in river_states:
        river_states_options.append({'label': state, 'value': state})

    states_card = dbc.Card([
        dbc.CardHeader('Select City'),   
        dbc.CardBody([
            dcc.Dropdown(
                id='river-state-option',
                options=river_states_options,
                clearable=False,
                value=river_states[0]
            ),
        ]),
    ], style={'margin': '5px'}, className='w-100', color='rgba(168, 215, 255, 0.35)')

    return states_card


@app.callback(Output('river-state-details', 'children'),
                [Input(component_id='river-state-option', component_property='value')])
def create_states_selector(state):
    ganga_2018_selected = ganga_2018[ganga_2018['STATION CODE'].isin(location_coordinates_df['location_id'])]


    ## air quality details

    table_header = [
        html.Thead(html.Tr([html.Th("Location"), html.Th("WQI"), html.Th("pH"), html.Th("BOD"), html.Th("Nitrate")]))
    ]

    rows = list()

    for i,row in ganga_2018_selected[ganga_2018_selected['STATE']==state].iterrows():
        rows.append(html.Tr([html.Td(row['STATION NAME']),  html.Td("{0:.2f}".format(row['wqi'])), html.Td(row['PH MIN']), html.Td(row['BIO-CHEMICAL OXYGEN DEMAND MIN']), html.Td(row['NITRATE + NITRITE MIN'])]))

    table_body = [html.Tbody(rows)]

    table = dbc.Table(table_header + table_body, bordered=True)

    state_description_card = dbc.Card([
        dbc.CardHeader('State Locations Air Quality Details'),   
        dbc.CardBody(table),
    ], style={'margin': '5px'}, className='w-100', color='rgba(168, 215, 255, 0.35)')


    ## usuability details

    table_header = [
        html.Thead(html.Tr([html.Th("Location"), html.Th("Irrigation"), html.Th("Drinking"), html.Th("Bathing")]))
    ]

    rows = list()

    for i,row in ganga_2018_selected[ganga_2018_selected['STATE']==state].iterrows():
        irrigation_status = None
        irrigation_color = None
        drinking_status = None
        drinking_color = None
        bathing_status = None
        bathing_color = None
        
        if (row['PH']>=6) & (row['PH']<=8.5) & (row['CONDUCTIVITY']<2000):
            irrigation_status = 'Fit'
            irrigation_color = 'green'
        else:
            irrigation_status = 'Not Fit'
            irrigation_color = 'red'

        if (row['BOD']<=3) & (row['DO']>=4) & (row['PH']>=6) & (row['PH']<=9):
            drinking_status = 'Fit'
            drinking_color = 'green'
        else:
            drinking_status = 'Not Fit'
            drinking_color = 'red'

        if (row['BOD']<=3) & (row['DO']>=5) & (row['PH']>=6.5) & (row['PH']<=8.5):
            bathing_status = 'Fit'
            bathing_color = 'green'
        else:
            bathing_status = 'Not Fit'
            bathing_color = 'red'

        rows.append(html.Tr([html.Td(row['STATION NAME']), html.Td(irrigation_status, style={"color": irrigation_color}), html.Td(drinking_status, style={"color": drinking_color}), html.Td(bathing_status, style={"color": bathing_color})]))

    table_body = [html.Tbody(rows)]

    table = dbc.Table(table_header + table_body, bordered=True)

    water_usability_card =dbc.Card([
        dbc.CardHeader('State Locations Water Usability Details'),   
        dbc.CardBody(table),
    ], style={'margin': '5px'}, className='w-100', color='rgba(168, 215, 255, 0.35)')


    return state_description_card,water_usability_card



# dcc.Graph(id="city-temp", figure=bullet_fig),
#                         dcc.Graph(id="city-aq", figure=bullet_fig),
#                         dcc.Graph(id="city-humidity", figure=bullet_fig),
#                         dcc.Graph(id="city-uv", figure=bullet_fig),
#                         dcc.Graph(id="city-precipitation", figure=bullet_fig)

@app.callback(Output('real-time-city-details', 'children'),
              Output('city-temp', 'figure'),
              Output('city-aq', 'figure'),
              Output('city-humidity', 'figure'),
              Output('city-uv', 'figure'),
              Output('city-precipitation', 'figure'),
              Output('city-sustainability-status', 'children'),
              Output('city-temp-historical', 'figure'),
              Output('city-rainfall-historical', 'figure'),
              Output('city-aq-historical', 'figure'),
              Output('city-land-erosion-historical', 'figure'),
              Output('city-land-covered-historical', 'figure'),
              Output('city-land-texture-historical', 'figure'),
              Output('city-groundwater-historical', 'figure'),
              Output('city-waste-historical', 'figure'),
                [Input(component_id='city', component_property='value')])
def on_city_change(city):

    # url = "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=b4dc986918e043939e4111312211606 &q=Bangalore&num_of_days=1&tp=24&format=json&aqi=yes&alerts=yes"
    # payload="<file contents here>"
    # headers = {
    #   'Content-Type': 'text/plain'
    # }
    # response = requests.request("GET", url, headers=headers, data=payload)
    # y = json.loads(response.text)
    # current_dict = y["data"]["current_condition"][0]
    # required_keys = ["temp_C", "air_quality", "humidity", "uvIndex", "windspeedKmph", "precipMM"]
    # final_dict = {}
    # for item in required_keys:
    #     if item == "air_quality":
    #         final_dict[item] = current_dict[item]["us-epa-index"]
    #     else:
    #         final_dict[item] = current_dict[item]
    final_dict = {'temp_C': '23', 'air_quality': '1', 'humidity': '83', 'uvIndex': '7', 'windspeedKmph': '15', 'precipMM': '0.0'}

    ### read historical data start #####

    temp_data = pd.read_csv('temperature_data/'+city+'_temp_hist_forecast.csv')
    # rain_data = pd.read_csv('rainfall_data/'+city+'.csv')

    data = cloud_connection(cos, 'cognitivehackathon', city+'_rainfall.csv') 
    rain_data = data_import(data)
    rain_data = rain_data.astype(str)
    rain_data['RF Actual Level (mm)'] = rain_data['RF Actual Level (mm)'].astype(float)
    rain_data.columns = ['Dates','RF Actual Level (mm)','Last 10 Year Average (m bgl)', 'Last Year  (m bgl)', 'Current Level (m bgl)']

    ### read historical data end #####

    ##temperature
    bullet_fig_temp = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = float(final_dict['temp_C']),
        gauge = {
            'shape': "bullet",
            'axis' : {"range":[None, 100]},
            'steps': [
                {'range': [0, 10], 'color': "red"},
                {'range': [10,30], 'color': "orange"},
                {'range': [30,70], 'color': "green"},
                {'range': [70,90], 'color': "orange"},
                {'range': [90,100], 'color': "red"}
            ],
            'bar': {'color': "darkblue"}
        },
        domain = {'x': [0.35, 1], 'y': [0.3, 0.7]},
        title = {'text': "Temperature  ", "font": {"size":14}}
    ))

    bullet_fig_temp.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        height=70,
        width=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    ##air quality
    bullet_fig_aq = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = float(final_dict['air_quality']),
        gauge = {
            'shape': "bullet",
            'axis' : {"range":[None, 100]},
            'steps': [
                {'range': [0, 10], 'color': "red"},
                {'range': [10,30], 'color': "orange"},
                {'range': [30,70], 'color': "green"},
                {'range': [70,90], 'color': "orange"},
                {'range': [90,100], 'color': "red"}
            ],
            'bar': {'color': "darkblue"}
        },
        domain = {'x': [0.35, 1], 'y': [0.3, 0.7]},
        title = {'text': "Air Quality  ", "font": {"size":14}}
    ))

    bullet_fig_aq.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        height=70,
        width=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    ##humidity
    bullet_fig_humidity = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = float(final_dict['humidity']),
        gauge = {
            'shape': "bullet",
            'axis' : {"range":[None, 100]},
            'steps': [
                {'range': [0, 10], 'color': "red"},
                {'range': [10,30], 'color': "orange"},
                {'range': [30,70], 'color': "green"},
                {'range': [70,90], 'color': "orange"},
                {'range': [90,100], 'color': "red"}
            ],
            'bar': {'color': "darkblue"}
        },
        domain = {'x': [0.35, 1], 'y': [0.3, 0.7]},
        title = {'text': "Humidity  ", "font": {"size":14}}
    ))

    bullet_fig_humidity.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        height=70,
        width=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    ##uv
    bullet_fig_uv = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = float(final_dict['uvIndex']),
        gauge = {
            'shape': "bullet",
            'axis' : {"range":[None, 100]},
            'steps': [
                {'range': [0, 10], 'color': "red"},
                {'range': [10,30], 'color': "orange"},
                {'range': [30,70], 'color': "green"},
                {'range': [70,90], 'color': "orange"},
                {'range': [90,100], 'color': "red"}
            ],
            'bar': {'color': "darkblue"}
        },
        domain = {'x': [0.35, 1], 'y': [0.3, 0.7]},
        title = {'text': "UV Index  ", "font": {"size":14}}
    ))

    bullet_fig_uv.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        height=70,
        width=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    ##precipitation
    bullet_fig_precipitation = go.Figure(go.Indicator(
        mode = "number+gauge",
        value = float(final_dict['precipMM']),
        gauge = {
            'shape': "bullet",
            'axis' : {"range":[None, 100]},
            'steps': [
                {'range': [0, 10], 'color': "red"},
                {'range': [10,30], 'color': "orange"},
                {'range': [30,70], 'color': "green"},
                {'range': [70,90], 'color': "orange"},
                {'range': [90,100], 'color': "red"}
            ],
            'bar': {'color': "darkblue"}
        },
        domain = {'x': [0.35, 1], 'y': [0.3, 0.7]},
        title = {'text': "Precipitation ", "font": {"size":14}}
    ))

    bullet_fig_precipitation.update_layout(
        margin ={'l':0,'t':0,'b':0,'r':0},
        height=70,
        width=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    sustainable = None
    if (sustainability_status[city]=="Medium"):
        sustainable = (html.P(children=[
            html.Strong('City Sustainability Status: '),
            html.Span(sustainability_status[city])
        ], style={'margin-top': '20px'}),
        html.Img(src="/assets/smiling_earth.png", style={'height': '50%','width': '50%'}))
    elif (sustainability_status[city]=="High-Medium") | (sustainability_status[city]=="High"):
        sustainable = (html.P(children=[
            html.Strong('City Sustainability Status: '),
            html.Span(sustainability_status[city])
        ], style={'margin-top': '20px'}),
        html.Img(src="/assets/sad_earth.png", style={'height': '50%','width': '50%'}))

    #### city historical data plot start ######

    # fig_temperature = px.line(temp_data, x="date_time", y="maxtempC",
    #     labels={
    #         "date_time": "Date",
    #         "maxtempC": "Max. Temperature",
    #     },
    #         title='Temperature Data')

    fig_temperature = go.Figure()
    fig_temperature.add_trace(go.Scatter(x=temp_data[temp_data['TempC'].notna()]['date'], y=temp_data[temp_data['TempC'].notna()]['TempC'],
                        mode='lines',
                        name='Historical Data'))
    fig_temperature.add_trace(go.Scatter(x=temp_data[temp_data['TempC'].isna()]['date'], y=temp_data[temp_data['TempC'].isna()]['Forecast(TempC)'],
                        mode='lines',
                        name='Forecast Data',
                        line=dict(
                        color='orange'
                    )))

    fig_rainfall = px.line(rain_data, x="Dates", y="RF Actual Level (mm)",)

    temp_gd_water = ground_water[ground_water["District"] == city]
    fig_groundwater = go.Figure(go.Scatter(x=temp_gd_water['Dates'], y=temp_gd_water["Current Level (m bgl)"]))


    temp_waste_data = waste_data[waste_data["District"] == city]
    fig_waste = go.Figure()
    fig_waste = make_subplots(specs=[[{"secondary_y": True}]])
    fig_waste.add_trace(go.Bar(x=temp_waste_data['Year'], y=temp_waste_data['Population'],
                        name='Population',
                        marker_color = 'green',
                        opacity=0.4,
                        marker_line_color='rgb(8,48,107)',
                        marker_line_width=2))
    # add first scatter trace at row = 1, col = 1
    fig_waste.add_trace(go.Scatter(x=temp_waste_data['Year'], y=temp_waste_data['Per capita waste generation (kg/day)'], line=dict(color='red'), name='Per capita waste generation (kg/day)'),
                    secondary_y=True,)



    # colors = ['red' if val > 100 else 'green' for val in air_quality[air_quality['City']==city]['AQI']]

    fig_aq = px.line(air_quality[air_quality['City']==city], x="Date", y="AQI")


    temp_data = erosion[erosion["City"] == city]
    fig_erosion = go.Figure([go.Pie(labels=temp_data["Soil Erosion"], values=temp_data["% Land Area Covered"])])

    temp_data = texture[texture["City"] == city]
    fig_texture = go.Figure([go.Pie(labels=temp_data["Soil Texture"], values=temp_data["% Land Area Covered"])])

    temp_data = productivity[productivity["City"] == city]
    fig_covered = go.Figure([go.Pie(labels=temp_data["Soil Productivity"], values=temp_data["% Land Area Covered"])])
    #### city historical data plot start ######

    return (city+" Real time"), bullet_fig_temp, bullet_fig_aq, bullet_fig_humidity, bullet_fig_uv, bullet_fig_precipitation, sustainable, fig_temperature, fig_rainfall,fig_aq, fig_erosion, fig_covered, fig_texture,fig_groundwater,fig_waste


if __name__ == '__main__': 
    app.run_server(port = int(os.getenv('PORT', 8080)), host='0.0.0.0', debug=True)
