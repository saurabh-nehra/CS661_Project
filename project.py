# CS661A Term Project
# Group 7

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import datetime
import webbrowser
import folium
from folium import plugins
import seaborn as sns
from branca.element import Template, MacroElement
import os

cwd = os.getcwd()

#############################################################
# Load the weather data from the CSV file
weather_df = pd.read_csv(".cleaning/combined_reduced.csv")

# Take a sample of 5000 points from weather data
sample_df = weather_df  # .sample(5000, random_state=101)

# Convert the 'date' column to datetime format
# sample_df['date'] = pd.to_datetime(sample_df['date'])

# Sort the weather data by date
sample_df = sample_df.sort_values(by=['inme', 'date'])

# remove own index with default index
sample_df.reset_index(inplace=True, drop=True)


columns = ['Date', 'Station number', 'Region', 'Provision', 'Station name', 'Latitude', 'Longitude', 'Elevation',
           'Precipitation(mm)', 'Pressure(millibars)', 'Temperature(C)', 'Humidity', 'Wind Direction', 'Wind Speed(m/s)']
#############################################################

# Define a function to display the data on the home page


def home_page():
    st.title("Weather Data Dashboard :partly_sunny:")
    st.write("Welcome to the *Weather Data Dashboard*.")
    st.write("Use the sidebar to navigate through the app :sunglasses:.")
    st.subheader("Big Data Visual Analytics (CS 661A) Term Project")
    st.write("Group 7: Ashok Vishwakarma | Saurabh  | Onkar Dasari | Rick Ghosh")
    st.subheader("Instructor: Soumya Dutta")
    st.markdown(
        'The interactive website is live at https://askvish.github.io/projects/brazil_map.html')
    st.write("The dataset is looks like:")
    sample_df.columns = columns
    st.write(sample_df)


# Define a function to display a summary of the data on a separate page
def summary_page():
    st.title("Data Summary")
    st.write("Here is a summary of the weather data:")
    sample_df.columns = columns
    st.write(sample_df.describe())

    time_df = sample_df
    time_df["Date"] = pd.to_datetime(time_df["Date"])

    time_df['Year'] = time_df['Date'].dt.year
    average_temp = time_df.groupby(
        'Year')['Temperature(C)'].mean().reset_index()
    average_temp = average_temp.iloc[1:-1]

    st.title("Average temperature per year")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=average_temp['Year'],
                  y=average_temp["Temperature(C)"], name="Temperature"))

    fig.update_layout(xaxis_title="Year",
                      yaxis_title="Temperature (in Celsius)")
    st.plotly_chart(fig)

    st.title("Average Precipitation by Region")

    fig = go.Figure()

    region_precipitation = weather_df.groupby(
        'regi')['prcp'].mean().reset_index()

    fig = go.Figure(
        data=[go.Bar(x=region_precipitation['regi'], y=region_precipitation['prcp'])])

    fig.update_layout(xaxis_title='Region',
                      yaxis_title='Average Precipitation (mm)')
    st.plotly_chart(fig)

    st.title("Average Temperature by Month and Region")
    # Extract month from date column
    weather_df['date'] = pd.to_datetime(weather_df['date'])
    weather_df['month'] = weather_df['date'].dt.month

    # Group weather data by month and region and calculate mean temperature
    month_region_temp = weather_df.groupby(['month', 'regi'])[
        'temp'].mean().reset_index()

    # Pivot the data to create a heatmap
    month_region_temp_pivot = month_region_temp.pivot(
        index='month', columns='regi', values='temp')

    # Heatmap of average temperature by month and region
    heatmap = go.Heatmap(z=month_region_temp_pivot.values,
                         x=month_region_temp_pivot.columns,
                         y=month_region_temp_pivot.index,
                         colorscale='RdBu', reversescale=True)
    fig = go.Figure(data=[heatmap])
    fig.update_layout(
        title="Heatmap",
        xaxis_title="Region",
        yaxis_title="Month"
    )

    st.plotly_chart(fig)


# Define a function to create a line chart of temperature and humidity by date
def line_chart(filtered_df):
    st.title("Average Temperature and Humidity by Date")
    st.write("Average Temperature and Humidity by Date:")
    grouped = filtered_df.groupby("date")[["temp", "hmdy"]].mean()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grouped.index,
                  y=grouped["temp"], name="Temperature"))
    fig.add_trace(go.Scatter(x=grouped.index,
                  y=grouped["hmdy"], name="Humidity"))
    fig.update_layout(xaxis_title="Date",
                      yaxis_title="Temperature and Humidity")
    st.plotly_chart(fig)


# Define a function to display a bar chart of average precipitation by region
def bar_chart(filtered_df):
    st.title("Average Precipitation by Region")
    st.write("Here is a bar chart of average precipitation by region:")
    grouped = filtered_df.groupby("regi")["prcp"].mean()
    fig = px.bar(grouped, x=grouped.index, y=grouped.values, labels={
        "x": "Region", "y": "Average Precipitation"})
    st.plotly_chart(fig)


# Define a function to display an animated scatter plot of temperature vs. humidity on a separate page

def scatter_page(sample_df, date):
    st.title("Temperature v/s Pressure v/s Windspeed")
    st.write(
        "Here is an animated scatter plot of Temperature v/s Pressure v/s Windspeed per region:")

    # Convert the datetime column to a string column

    sample_df['date'] = sample_df['date'].astype('str')
    sample_df = sample_df[(sample_df["date"] == date)]
    sample_df['frame'] = range(len(sample_df))

    fig = px.scatter_3d(sample_df, x="temp", y="stp", z="wdsp", color="regi")

    fig.update_layout(title="Temperature v/s Pressure v/s Windspeed",
                      scene=dict(xaxis_title="Temperature",
                                 yaxis_title="Pressure", zaxis_title="Windspeed"),
                      scene_camera=dict(center=dict(
                          x=0, y=0, z=0.1), eye=dict(x=1.5, y=1.5, z=1.5)))

    st.plotly_chart(fig)


# Define a function to create an animated heatmap of precipitation by region
def heatmap_page(filtered_df):
    st.title("Precipitation Density Map")
    st.write(
        "Here is an animated heatmap of precipitation density of the selected day:")
    # Create a mapbox figure with the filtered data
    fig = px.scatter_mapbox(data_frame=filtered_df,
                            lat="lat",
                            lon="lon",
                            size="prcp",
                            color="temp",
                            color_continuous_scale="icefire",
                            zoom=2,
                            mapbox_style="carto-positron",
                            hover_name="wsnm",
                            hover_data=["regi", "temp",
                                        "hmdy", "wdct", "wdsp"],
                            labels={"precipitation": "Precipitation (mm)",
                                    "temperature": "Temperature (°C)",
                                    "humidity": "Humidity (%)",
                                    "wind_direction": "Wind Direction (°)",
                                    "wind_speed": "Wind Speed (m/s)",
                                    "station_name": "Station Name"}
                            )

    # Update the figure layout and return the figure
    fig.update_layout(title=f"Rain and Temperature",
                      coloraxis_colorbar=dict(title="Temperature (°C)"))
    st.plotly_chart(fig)


# create the exploration page
def exploration_page():
    st.title("Exploration Page")
    st.write("Explore the weather data with the following options:")

    # Define the widgets for user interaction
    selected_date = st.date_input(
        "Pick a date",
        datetime.date(2019, 7, 6),
        min_value=datetime.date(2000, 5, 7),
        max_value=datetime.date(2021, 4, 30))
    if selected_date:
        st.write("You selected:", selected_date)

    sample_df['date'] = sample_df['date'].astype('str')

    # Filter the data based on the user's selections
    filtered_df = sample_df[(sample_df["date"] == str(selected_date))]

    print(type(selected_date).__name__)
    print(sample_df['date'])
    st.write("Found {} rows".format(len(filtered_df)))
    # display the filtered data
    st.write(filtered_df)

    # html map
    map(filtered_df)
    webbrowser.open(
        'file://' + cwd + '\\brazil_map.html', new=2)

    # Heat Map:
    heatmap_page(filtered_df)
    # Scatter Plot:
    selected_date = str(selected_date)
    scatter_page(sample_df, selected_date)

# create the visualization page


def map(sample_df):
    # Create a map centered on Brazil
    brazil_map = folium.Map(
        location=[-15.788497, -47.879873], zoom_start=4, tiles='Open Street Map')

    # Create a MarkerCluster object
    marker_cluster = folium.plugins.MarkerCluster(name='Weather Stations')

    # Add markers for weather stations with pop-up information to the MarkerCluster object
    for i, row in sample_df.iterrows():
        popup_text = f"Weather Station: {row['wsnm']} ({row['inme']})<br>Region: {row['regi']} (Provision: {row['prov']})<br>Temperature: {round(row['temp'], 4)} &#8451;<br>Latitude: {row['lat']} m<br>Longitude: {row['lon']} m<br>Elevation: {row['elvt']} m<br>Pressure: {row['stp']} millibars<br>Precipitation: {row['prcp']} mm<br>Humidity: {row['hmdy']} <br>Wind Speed: {row['wdsp']} m/s<br>Wind Direction: {row['wdct']}"
        folium.Marker(location=[row['lat'], row['lon']],
                      popup=folium.Popup(popup_text, max_width=500),
                      icon=folium.Icon(color='red')).add_to(marker_cluster)

    # Add the MarkerCluster object to the map
    brazil_map.add_child(marker_cluster)

    # Create a list of all weather station names
    station_names = list(set(weather_df['wsnm']))

    # Create a list of all weather stations
    stations = weather_df[['wsnm', 'inme', 'lat', 'lon']
                          ].drop_duplicates().values.tolist()

    # Define a custom search function that filters results based on user input

    def search_func(query, item):
        # Return True if the query matches the start of the item name
        return query.lower() in item['wsnm'].lower()

    # Add a search bar to the map
    search = folium.plugins.Search(
        layer=marker_cluster,
        geom_type='Point',
        search_data=stations,  # Add the search data
        search_func=search_func,  # Add the custom search function
        placeholder='Search for a location',
        collapsed=False,
        search_label='wsnm',
        search_zoom=200,  # Increase search_zoom to show all markers on the map
        weight=3,
        show=True,
        tooltip=True,
        marker=True,
        custom_icon=None,
        highlight=True,
        data=sample_df[['lat', 'lon', 'wsnm']],
        position='topleft').add_to(brazil_map)

    # Add all weather station names to the search bar options
    search.options = station_names

    # Create a list of locations for the HeatMap
    locations = sample_df[['lat', 'lon']].values.tolist()

    # Create a HeatMap object
    heatmap = folium.plugins.HeatMap(
        data=locations, name='Weather Stations Heatmap', min_opacity=0.2, radius=15)

    # Add the HeatMap object to the map
    brazil_map.add_child(heatmap)

    # Create a list of precipitation for the HeatMap
    prcps = sample_df[['lat', 'lon', 'prcp']].values.tolist()

    # Create a list of wind speeds for the HeatMap
    wind_speeds = sample_df[['lat', 'lon', 'wdsp']].values.tolist()

    # Add the HeatMap object to the map
    folium.plugins.HeatMap(data=wind_speeds, name='Wind Speed (m/s) Heatmap', min_opacity=0.2,
                           radius=15, overlay=True, control=True, show=False,).add_to(brazil_map)

    # Add the HeatMap object to the map
    folium.plugins.HeatMap(data=prcps, name='Precipitation (mm) Heatmap', min_opacity=0.2,
                           radius=15, overlay=True, control=True, show=False,).add_to(brazil_map)

    # Creating Minimaps
    minimap = plugins.MiniMap(toggle_display=True)
    brazil_map.add_child(minimap)

    # Add a scroll zoom toggler to the map
    # plugins.ScrollZoomToggler().add_to(brazil_map)

    # Add a satellite layer to the map
    folium.raster_layers.TileLayer('Stamen Terrain').add_to(brazil_map)
    folium.raster_layers.TileLayer('CartoDB Positron').add_to(brazil_map)
    folium.raster_layers.TileLayer('Stamen Toner').add_to(brazil_map)
    folium.raster_layers.TileLayer('Stamen Watercolor').add_to(brazil_map)
    folium.raster_layers.TileLayer('CartoDB Dark_Matter').add_to(brazil_map)

    # Add the MeasureControl object to the map
    folium.plugins.MeasureControl(position='topleft', primary_length_unit='kilometers',
                                  secondary_length_unit='miles', primary_area_unit='sqmeters', secondary_area_unit='acres').add_to(brazil_map)

    # Add the Fullscreen object to the map
    folium.plugins.Fullscreen(
        position='topleft', title='Fullscreen', title_cancel='Exit fullscreen').add_to(brazil_map)

    # Add the Draw object
    plugins.Draw(export=True).add_to(brazil_map)

    # Add the LayerControl of the layer to the map
    folium.LayerControl(collapsed=True).add_to(brazil_map)

    # Get the highest and coldest weather stations
    max_temp_info = sample_df.loc[sample_df['temp'].idxmax()]
    min_temp_info = sample_df.loc[sample_df['temp'].idxmin()]
    max_temp = max_temp_info['temp']
    min_temp = min_temp_info['temp']
    max_temp_ws = max_temp_info['inme']
    min_temp_ws = min_temp_info['inme']
    max_press_info = sample_df.loc[sample_df['stp'].idxmax()]
    min_press_info = sample_df.loc[sample_df['stp'].idxmin()]
    max_press = max_press_info['stp']
    min_press = min_press_info['stp']
    max_press_ws = max_press_info['inme']
    min_press_ws = min_press_info['inme']

    # Define the HTML for the legend
    legend_html = '''
    <div style="position: fixed; bottom: 150px; left: 50px; width: 220px; height: 160px;
                border: 2px solid grey; z-index: 9999; font-size: 12px;
                background-color: rgba(255, 255, 255, 0.7);">
    <h4 style="text-align:center; margin-top:10px;">Legend</h4>
    <table style="display: flex; flex-wrap: wrap; justify-content: space-evenly; padding: 0px;">
        <tr>
        <td>Min. Temp: {min_temp} &#8451; at {min_temp_ws}</td>
        </tr>
        <tr>
        <td>Max. Temp: {max_temp} &#8451; at {max_temp_ws}</td>
        </tr>
        <tr>
        <td>Min. Pressure: {min_press} mb at {min_press_ws}</td>
        </tr>
        <tr>
        <td>Max. Pressure: {max_press} mb at {max_press_ws}</td>
        </tr>
        <tr>
        <td>* mb = millibars</td>
        </tr>
    </table>
    </div>
    '''.format(min_temp=min_temp, max_temp=max_temp, min_press=min_press, max_press=max_press, min_temp_ws=min_temp_ws, max_temp_ws=max_temp_ws, min_press_ws=min_press_ws, max_press_ws=max_press_ws)

    # Add the HTML to the map
    brazil_map.get_root().html.add_child(folium.Element(legend_html))

    # Define draggable legend
    template = """
    {% macro html(this, kwargs) %}
    <!doctype html>
    <html lang="en">

    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Brazil Weather Analysis</title>
    <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

    <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

    <script>
        $(function () {
        $("#maplegend").draggable({
            start: function (event, ui) {
            $(this).css({
                right: "auto",
                top: "auto",
                bottom: "auto"
            });
            }
        });
        });

    </script>
    </head>

    <body>

    <div id='maplegend' class='maplegend' style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
        border-radius:6px; padding: 10px; font-size:14px; left: 50px; bottom: 50px;'>

        <div class='legend-title'>Legend (draggable!)</div>
        <div class='legend-scale'>
        <ul class='legend-labels'>
            <li><i class="fa-solid fa-location-dot fa-2xl" style="color: #ff0000;"></i></span>&nbsp;&nbsp;Weather Station
            </li>
            <li><i class="fa-solid fa-circle fa-xl"></i></span>&nbsp;Station Cluster</li>
        </ul>
        </div>
    </div>

    </body>

    </html>

    <style type='text/css'>
    .maplegend .legend-title {
        text-align: left;
        margin-bottom: 5px;
        font-weight: bold;
        font-size: 90%;
    }

    .maplegend .legend-scale ul {
        margin: 0;
        margin-bottom: 5px;
        padding: 0;
        float: left;
        list-style: none;
    }

    .maplegend .legend-scale ul li {
        font-size: 80%;
        list-style: none;
        margin-left: 0;
        line-height: 18px;
        margin-bottom: 2px;
    }

    .maplegend ul.legend-labels li span {
        display: block;
        float: left;
        height: 16px;
        width: 30px;
        margin-right: 5px;
        margin-left: 0;
        border: 1px solid #999;
    }

    .maplegend .legend-source {
        font-size: 80%;
        color: #777;
        clear: both;
    }

    .maplegend a {
        color: #777;
    }
    </style>
    {% endmacro %}"""

    macro = MacroElement()
    macro._template = Template(template)

    brazil_map.get_root().add_child(macro)

    # Save the map as an HTML file
    brazil_map.save('brazil_map.html')


def visualization_page():
    st.title("Visualization Page")
    st.write("Visualize the weather data with the following options:")

    selected_date = st.date_input(
        "Pick a date",
        datetime.date(2019, 7, 6),
        min_value=datetime.date(2000, 5, 7),
        max_value=datetime.date(2021, 4, 30))
    if selected_date:
        st.write("You selected:", selected_date)

    # Set the default map center and zoom level
    default_coords = (-14.23, -53.18)

    # Define the layout of the interface
    st.sidebar.header("Filters")

    sample_df['date'] = sample_df['date'].astype('str')
    filtered_df = sample_df[(sample_df["date"] == str(selected_date))]

    # Create a list of unique regions and stations for filtering
    regions = sorted(filtered_df["regi"].unique())
    stations = sorted(filtered_df["wsnm"].unique())

    # Convert the 'date' column to datetime format
    filtered_df['date'] = pd.to_datetime(sample_df['date'])

    # Create the sidebar widgets (the filters for the interface)
    region_filter = st.sidebar.multiselect(
        "Select region(s)", regions, default=regions)
    # date_range = st.sidebar.date_input(
    #    "Select date range", value=(sample_df["date"].min(), sample_df["date"].max()))
    station_filter = st.sidebar.multiselect(
        "Select station(s)", stations, default=stations)

    # Filter the data based on the user's selection
    filtered1_df = filtered_df[
        (sample_df["regi"].isin(region_filter)) &
        (sample_df["wsnm"].isin(station_filter))
    ]

    # Display the filtered data
    st.write(f"Found {len(filtered1_df)} rows.")
    st.write(filtered1_df)

    # Create a map visualization of the data
    fig1 = px.scatter_mapbox(
        filtered1_df,
        lat="lat",
        lon="lon",
        hover_name="wsnm",
        hover_data=["regi", "temp", "hmdy"],
        zoom=2,
        center={"lat": default_coords[0], "lon": default_coords[1]},
        height=500
    )
    fig1.update_layout(mapbox_style="open-street-map",
                       title="Weather Stations found after applying the filters:")
    st.plotly_chart(fig1)

    st.header("Heat Map of Temperature by Region of selected date")
    # Sort the weather data by date
    filtered_df = filtered_df.sort_values(by=['inme', 'date'])
    # Convert the datetime column to a string column
    sample_df['date'] = sample_df['date'].astype('str')
    # remove own index with default index
    filtered_df.reset_index(inplace=True, drop=True)
    fig5 = px.density_mapbox(filtered1_df, lat="lat", lon="lon", z="temp", radius=10, zoom=2,
                             hover_name="inme", animation_frame=filtered_df["date"].dt.year,
                             color_continuous_scale="icefire", mapbox_style="open-street-map", opacity=0.5)
    st.plotly_chart(fig5)

    # Create a histogram of the temperature data
    fig2 = px.histogram(
        filtered1_df,
        x="temp",
        nbins=100,
        title="Distribution of Temperature across Brazil"
    )
    st.plotly_chart(fig2)

    # Define the visualizations for the interface
    st.header("Temperature vs. Precipitation per region")
    fig3 = px.scatter(filtered1_df, x="temp", y="prcp",
                      color="regi", hover_name="inme")
    fig3.update_layout(xaxis_title="Temperature",
                       yaxis_title="Precipitation")
    st.plotly_chart(fig3)

    st.header("Average Temperature by Region per Year")
    fig4 = px.line(filtered1_df.groupby(["regi", filtered1_df["date"].dt.year])["temp"].mean().reset_index(),
                   x="date", y="temp", color="regi", labels={"date": "Year", "temperature": "Average Temperature (C)"})
    fig4.update_layout(xaxis_title="Temperature",
                       yaxis_title="Average Temperature (C)")
    st.plotly_chart(fig4)

    # Bar Chart:
    bar_chart(filtered1_df)
    # Line Chart:
    line_chart(filtered1_df)


# Define the main function to run the interactive interface using Streamlit
def main():
    # Set the app title and favicon
    st.set_page_config(page_title="Weather Data Dashboard",
                       page_icon=":partly_sunny:")

    # create a sidebar menu options for multiple pages
    options = ["Homepage", "Summary", "Exploration", "Visualization"]
    choice = st.sidebar.selectbox("Navigation Dropdown", options)

    # Show the appropriate page based on the user's choice
    if choice == "Homepage":
        home_page()
    elif choice == "Summary":
        summary_page()
    elif choice == "Exploration":
        exploration_page()
    elif choice == "Visualization":
        visualization_page()


if __name__ == "__main__":
    main()
