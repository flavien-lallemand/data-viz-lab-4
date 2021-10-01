from numpy.random.mtrand import f
import streamlit as st
# importing numpy and pandas for to work with sample data.
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import datetime
import pydeck as pdk

import logging
import time
import streamlit.components.v1 as components
import base64

from functools import wraps

############ CONFIG ############
logger = logging.getLogger(__name__)


# Misc logger setup so a debug log statement gets printed on stdout.
logger.setLevel("INFO")
handler = logging.FileHandler(filename="log.txt", mode="a")
log_format = "%(asctime)s %(levelname)s -- %(message)s"
formatter = logging.Formatter(log_format)
handler.setFormatter(formatter)
logger.addHandler(handler)

logging.info('\nNew Execution at :', time.time(), "\n")

############ END CONFIG ############

############ FUNCTIONS ############
def timed(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.info("{} ran in {}s".format(func.__name__, round(end - start, 2)))
        return result

    return wrapper

@timed
@st.cache(suppress_st_warning=True, allow_output_mutation=True, persist=True)
def load_data_raw(url, delimiter):
    data=pd.read_csv(url, delimiter)

    data["Date/Time"] = pd.to_datetime(data["Date/Time"])

    data['day'] = data['Date/Time'].map(get_dom)

    data['weekday'] = data['Date/Time'].map(get_weekday)

    data['hour'] = data['Date/Time'].map(get_hour)

    data['minute'] = data['Date/Time'].map(get_minute)

    return data

@timed
@st.cache(suppress_st_warning=True, allow_output_mutation=True, persist=True)
def load_data_ny(url, delimiter):

    data = pd.read_csv(url, delimiter)

    data['tpep_pickup_datetime'] = data['tpep_pickup_datetime'].map(pd.to_datetime)
    data['tpep_dropoff_datetime'] = data['tpep_dropoff_datetime'].map(pd.to_datetime)

    #Pickup datetime transformation and insertion in new column using get_... functions
    data['day_pickup'] = data['tpep_pickup_datetime'].map(get_dom)

    data['weekday_pickup'] = data['tpep_pickup_datetime'].map(get_weekday)

    data['hour_pickup'] = data['tpep_pickup_datetime'].map(get_hour)

    data['minute_pickup'] = data['tpep_pickup_datetime'].map(get_minute)


    #Dropoff datetime transformation and insertion in new column using get_... functions
    data['day_dropoff'] = data['tpep_dropoff_datetime'].map(get_dom)

    data['weekday_dropoff'] = data['tpep_dropoff_datetime'].map(get_weekday)

    data['hour_dropoff'] = data['tpep_dropoff_datetime'].map(get_hour)

    data['minute_dropoff'] = data['tpep_dropoff_datetime'].map(get_minute)

    data['trip_duration'] = (data['tpep_dropoff_datetime'] - data['tpep_pickup_datetime'])
    #Create a new column 'trip_duration' by substract dropoff datetime by pickup datetime and compute it in minutes
    data['trip_duration'] = pd.to_timedelta(data['trip_duration']).dt.total_seconds()/60

    #Create a column 'average_speed' by dividing trip distance by trip duration in hour
    data['average_speed'] = data["trip_distance"] / (data["trip_duration"] / 60) 

    return data

def get_dom(dt):
    return dt.day

def get_weekday(dt):
    return dt.weekday()

def get_hour(dt):
    return dt.hour

def get_minute(dt):
    return dt.minute


def count_rows(rows):
    return len(rows)

@timed
def map(data, lat, lon, zoom):
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": lat,
            "longitude": lon,
            "zoom": zoom,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
                "HexagonLayer",
                data=data,
                get_position=["Lon", "Lat"],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
        ]
    ))

############ END FUNTIONS ############

############ START EXECUTION #########

df=load_data_raw('uber-raw-data-apr14.csv', ',')
dfNy = load_data_ny("ny-trips-data.csv",',')


file_ = open("chart1.png", "rb")
contents = file_.read()
data_url_chart1 = base64.b64encode(contents).decode("utf-8")
file_.close()

file_ = open("chart2.png", "rb")
contents = file_.read()
data_url_chart2 = base64.b64encode(contents).decode("utf-8")
file_.close()



############ END EXECUTION #########

############ START FORMATTING #########
st.sidebar.markdown("<h2 style='text-align: center;font-family=\'Helvetica\';'><b>Dataset selection 📀</b></h2><br/>", unsafe_allow_html=True)


option = st.sidebar.selectbox(
'Choose the dataset whose dashboard you want to consult :',
("Uber April 2014", "Uber NY Trips on 15/01/2015"))

components.html(
    f"""
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
    
    <div style="text-align: center;">
        <h1> Plots display with iFrame</h1>
    </div>
    <div id="accordion">
      <div class="card">
        <div class="card-header" id="headingOne">
          <h5 class="mb-0">
            <button class="btn btn-link" data-toggle="collapse" data-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
            First Plot 📈
            </button>
          </h5>
        </div>
        <div id="collapseOne" class="collapse show" aria-labelledby="headingOne" data-parent="#accordion">
          <div class="card-body" style="text-align: center;">
            <p>This is my first plot displayed in a iFrame component</p>
            <img src="data:image/gif;base64,{data_url_chart1}" style="width: 350px;height:auto;"></img>
          </div>
        </div>
      </div>
      <div class="card">
        <div class="card-header" id="headingTwo">
          <h5 class="mb-0">
            <button class="btn btn-link collapsed" data-toggle="collapse" data-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
            Second Plot 📈
            </button>
          </h5>
        </div>
        <div id="collapseTwo" class="collapse" aria-labelledby="headingTwo" data-parent="#accordion">
          <div class="card-body" style="text-align: center;">
          <p>This is my second plot displayed in a iFrame component</p>
            <img src="data:image/gif;base64,{data_url_chart2}" style="width: 350px;height:auto;"></img>
          </div>
        </div>
      </div>
    </div>
    """,
    height=600,
)

components.iframe("https://www.openstreetmap.org/export/embed.html?bbox=-0.004017949104309083%2C51.47612752641776%2C0.00030577182769775396%2C51.478569861898606&layer=mapnik")


if option == 'Uber April 2014':


    st.markdown("<h1 style='text-align: center;font-family=\'Helvetica\';'>PART 3 - Uber April 2014 Visualization 👁</h1>", unsafe_allow_html=True)

    st.markdown('This is a dashboard to visualize relevant datas and charts about the Uber April 2014 dataset')
    st.markdown('***')

    #Expander Uber 2014 Dataset
    expander = st.expander("Uber 2014 Dataset")
    col1, col2 = expander.columns(2)
    col1.metric("Nombre de lignes", df.shape[0])
    col2.metric("Nombre de colonnes", df.shape[1])
    expander.write(df.head())


    #Date Input - 2 Columns
    st.markdown("<h2 style='text-align: center;font-family=\'Helvetica\';'><b>Visualization between two dates 🗓</b></h2><br/>", unsafe_allow_html=True)

    st.write("You can choose the starting and ending date to visualize frequency by Day of the Month")
    left_column2, right_column2 = st.columns(2)

    start_date = left_column2.date_input(
        "Starting Date",
        datetime.date(2014, 1, 4))

    end_date = right_column2.date_input(
        "Ending Date",
        datetime.date(2014, 1, 30))

    st.markdown("<br/>", unsafe_allow_html=True)

    #Filtered data for chart "Frequency by day of Month"
    in_interval = (df['day'] >= start_date.day) & (df['day'] <= end_date.day)
    filtered_data = df[in_interval]
    filtered_data = filtered_data.groupby('day').apply(count_rows)

    #Chart by Day and Hours
    st.markdown("<h4 style='text-align: center;font-family=\'Helvetica\';'><b>Frequency by DoM - Uber - April 2014</b></h4>", unsafe_allow_html=True)
    st.bar_chart(filtered_data)
    st.markdown('***')




    st.markdown("<h2 style='text-align: center;font-family=\'Helvetica\';'><b>Visualization by hour(s) and by date(s) 🕦</b></h2><br/>", unsafe_allow_html=True)

    #Breakdown of rides per minute between 0:00 and 1:00
    left_column1, right_column1 = st.columns(2)

    breakdown = right_column1.slider(
    "Select time range (of one hour, or more..) to visualize breakdown of rides :",
    0, 
    23, 
    value=(8, 22))

    breakdown_hour_start = breakdown[0]
    breakdown_hour_end = breakdown[1]

    selected_day = 1
    breakdown_day = left_column1.date_input(
        "Breakdown day :",
        datetime.date(2014, 1, 4), 
        datetime.date(2014, 1, 4), 
        datetime.date(2014, 1, 30))


    filter_day_hour = (df['day'] == breakdown_day.day) & (df['hour'] >= breakdown_hour_start) & (df['hour'] <= breakdown_hour_end)
    filtered_day_hour = df[filter_day_hour]
    filtered_day_hour = filtered_day_hour.groupby('minute').apply(count_rows)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;font-family=\'Helvetica\';'><b>" + str("Breakdown of rides on the " + str(breakdown_day) + "/01/2014 per minute between " + str(breakdown_hour_start) + ":00 and " + str(breakdown_hour_end) + ":00.") + "</b></h4>", unsafe_allow_html=True)

    st.bar_chart(filtered_day_hour)

    data = df[df["Date/Time"].dt.hour == breakdown_hour_start][["Lon", "Lat"]]

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;font-family=\'Helvetica\';'><b>" + str("All New-York Pick-up points on" + str(breakdown_day) +  "/01/2014 between " + str(breakdown_hour_start) + ":00 and " + str(breakdown_hour_end) + ":00.") + "</b></h4>", unsafe_allow_html=True)

    midpoint = (np.average(data["Lat"]), np.average(data["Lon"]))
    map(data, midpoint[0], midpoint[1], 11)

else: 
    st.markdown("<h1 style='text-align: center;font-family=\'Helvetica\';'>PART 3 - New-York Uber trips Visualization on 15/01/2015 🗽</h1>", unsafe_allow_html=True)

    st.markdown('This is a dashboard to visualize relevant datas and charts about Ubers\'s trips on 15/01/2015 in New-York')
    st.markdown('***')

    #Expander Uber 2014 Dataset
    expander = st.expander("Uber Trips 15/01/2015 Dataset")
    col1, col2 = expander.columns(2)
    col1.metric("Nombre de lignes", dfNy.shape[0])
    col2.metric("Nombre de colonnes", dfNy.shape[1])
    expander.write(dfNy.head())

    

    pickup_hour = st.slider(
    "Select time range (of one hour, or more..) to visualize Pickup frequency :",
    0, 
    23, 
    value=(0, 23))

    #Filtered data for chart "Frequency of pickup bt Hour"
    ny_in_interval = (dfNy['hour_pickup'] >= pickup_hour[0]) & (dfNy['hour_pickup'] <= pickup_hour[1])
    filtered_data_ny = dfNy[ny_in_interval]
    filtered_data_hour_ny = filtered_data_ny.groupby('hour_pickup').apply(count_rows)

     #Chart Pickup by Hour
    st.markdown("<h4 style='text-align: center;font-family=\'Helvetica\';'><b>Frequency of pickup by hour - Uber - 15/01/2015</b></h4>", unsafe_allow_html=True)
    st.bar_chart(filtered_data_hour_ny)

    #Chart Pickup by Minutes
    filtered_data_minute_ny = filtered_data_ny.groupby('minute_pickup').apply(count_rows)

    st.markdown("<h4 style='text-align: center;font-family=\'Helvetica\';'><b>Frequency of pickup by Minutes during the day - Uber - 15/01/2015</b></h4>", unsafe_allow_html=True)
    st.bar_chart(filtered_data_minute_ny)

    dfNy_plot = filtered_data_ny[["hour_pickup", "average_speed"]].groupby('hour_pickup').mean()
    dfNy_plot = dfNy_plot.fillna(dfNy_plot["average_speed"].mean())
    st.markdown("<h4 style='text-align: center;font-family=\'Helvetica\';'><b>Average trips' speed by hours during the day - Uber - 15/01/2015</b></h4>", unsafe_allow_html=True)
    st.line_chart(dfNy_plot)

st.markdown("<br/><br/><br/>", unsafe_allow_html=True)




    


############ END FORMATTING #########