import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import datetime
import webbrowser
import folium
from folium.plugins import MarkerCluster, Search, MeasureControl, Fullscreen
import seaborn as sns

#############################################################
# Load the weather data from the CSV file
weather_df = pd.read_csv("./combined_reduced.csv")

# Take a sample of 5000 points from weather data
sample_df = weather_df     #.sample(5000, random_state=101)

# Convert the 'date' column to datetime format
#sample_df['date'] = pd.to_datetime(sample_df['date'])

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
    st.markdown(
        'The interactive website is live at https://askvish.github.io/project/brazil_map.html')
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
    average_temp = time_df.groupby('Year')['Temperature(C)'].mean().reset_index()
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

    region_precipitation = weather_df.groupby('regi')['prcp'].mean().reset_index()

    fig = go.Figure(data=[go.Bar(x=region_precipitation['regi'], y=region_precipitation['prcp'])])

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
    st.title("Temperature vs. Pressure by Station")
    st.write(
        "Here is an animated scatter plot of temperature vs. pressure by station:")
    
    # Convert the datetime column to a string column

    sample_df['date'] = sample_df['date'].astype('str')
    sample_df = sample_df[(sample_df["date"] == date)]
    sample_df['frame'] = range(len(sample_df))
    fig = px.scatter(data_frame=sample_df,
                     x="regi",
                     y="stp",
                     animation_frame="frame",
                     animation_group="wsnm",
                     size="prcp",
                     size_max=20,
                     color="temp",
                     hover_name="wsnm",
                     range_x=[sample_df["temp"].min(
                     ), sample_df["temp"].max()],
                     range_y=[sample_df["stp"].min(
                     ), sample_df["stp"].max()],
                     labels={"temperature": "Temperature (Celsius)",
                             "humidity": "Humidity (%)",
                             "elevation": "Elevation (m)",
                             "precipitation": "Precipitation (mm)"},
                     title="Temperature vs. Pressure by Station (Animated)"
                     )
    fig.update_layout(transition_duration=100)
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
                            zoom=3,
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


    #html map
    map(filtered_df)
    webbrowser.open('file://' + 'D:\CS661\Proj\Project\CS661_Project\\brazil_map.html', new=2)

    # Heat Map:
    heatmap_page(filtered_df)
    # Scatter Plot:
    selected_date = str(selected_date)
    scatter_page(sample_df, selected_date)

# create the visualization page

def map(sample_df):
    # Create a map centered on Brazil
    brazil_map = folium.Map(location=[-15.788497, -47.879873], zoom_start=4)

    # Create a MarkerCluster object
    marker_cluster = MarkerCluster(name='Weather Stations')


    # Add markers for weather stations with pop-up information to the MarkerCluster object
    for i, row in sample_df.iterrows():
        popup_text = f"Weather Station: {row['wsnm']} ({row['inme']})<br>Temperature: {row['temp']} &#8451;<br>Elevation: {row['elvt']} m;<br>Pressure: {row['stp']} mb;<br>Humidity: {row['hmdy']} %;<br>Wind Speed: {row['wdsp']} m/s"
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
    search = Search(
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
        position='topright').add_to(brazil_map)

    # Add all weather station names to the search bar options
    search.options = station_names


    # Get the highest and coldest weather stations
    max_temp_info = sample_df.loc[sample_df['temp'].idxmax()]
    min_temp_info = sample_df.loc[sample_df['temp'].idxmin()]
    max_temp = round(max_temp_info['temp'], 2)
    min_temp = round(min_temp_info['temp'], 2)


    # Create a list of locations for the HeatMap
    locations = sample_df[['lat', 'lon']].values.tolist()

    # Create a HeatMap object
    heatmap = folium.plugins.HeatMap(locations, min_opacity=0.2, radius=15)

    # Add the HeatMap object to the map
    brazil_map.add_child(heatmap)

    # Create a MeasureControl object
    measure_control = MeasureControl(
        position='topleft', primary_length_unit='kilometers', secondary_length_unit='miles')

    # Add the MeasureControl object to the map
    brazil_map.add_child(measure_control)

    # Create a LayerControl object
    layer_control = folium.LayerControl()

    # Add the LayerControl object to the map
    brazil_map.add_child(layer_control)

    # Define the HTML for the legend
    legend_html = '''
    <div style="position: fixed; bottom: 30px; left: 30px; width: 200px; height: 160px;
                border: 2px solid grey; z-index: 9999; font-size: 12px;
                background-color: rgba(255, 255, 255, 0.7);">
        <h4 style="text-align:center; margin-top:15px;">Legend</h4>
        <hr>
        <table style="display: flex; flex-wrap: wrap; justify-content: space-evenly; padding: 5px;">
        <tr>
            <td>Minimum Temperature: {min_temp} &#8451;</td>
        </tr>
        <tr>
            <td>Maximum Temperature: {max_temp} &#8451;</td>
        </tr>
        </table>
    </div>
    <div style="position: fixed; bottom: 30px; right: 30px; width: 200px; height: 160px;
                border: 2px solid grey; z-index: 9999; font-size: 16px;
                background-color: rgba(255, 255, 255, 0.7);">
        <h4 style="text-align:center; margin-top:15px;">Markers</h4>
        <hr>
        <table style="display: flex; flex-wrap: wrap; justify-content: space-evenly; padding: 5px;">
        <tr>
            <td><img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png"
                style="width:20px;height:30px;"></td>
            <td>Weather Station</td>
        </tr>
        
        <tr>
            <td><i class="fa-solid fa-circle"></i></td>
            <td>Station Clusters</td>
        </tr>
        </table>
    </div>
    '''.format(min_temp=min_temp, max_temp=max_temp)

    # Add the HTML to the map
    brazil_map.get_root().html.add_child(folium.Element(legend_html))

    # Create a Fullscreen object
    fullscreen = Fullscreen(position='topright',
                            title='Fullscreen', title_cancel='Exit fullscreen')

    # Add the Fullscreen object to the map
    brazil_map.add_child(fullscreen)

    # Add a satellite layer to the map
    folium.TileLayer('Stamen Terrain').add_to(brazil_map)

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
    #date_range = st.sidebar.date_input(
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
    fig1.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig1)

    st.header("Heat Map of Temperature by Region and Month")
    # Convert the datetime column to a string column
    sample_df['date'] = sample_df['date'].astype('str')
    fig5 = px.density_mapbox(filtered1_df, lat="lat", lon="lon", z="temp", radius=10, zoom=2,
                             hover_name="inme", animation_frame=filtered_df["date"].dt.year,
                             mapbox_style="open-street-map", opacity=0.5)
    st.plotly_chart(fig5)

    # Create a histogram of the temperature data
    fig2 = px.histogram(
        filtered1_df,
        x="temp",
        nbins=20,
        title="Distribution of Temperature"
    )
    st.plotly_chart(fig2)

    # Define the visualizations for the interface
    st.header("Temperature vs. Precipitation")
    fig3 = px.scatter(filtered1_df, x="temp", y="prcp",
                      color="regi", hover_name="inme")
    st.plotly_chart(fig3)

    st.header("Average Temperature by Region and Year")
    fig4 = px.line(filtered1_df.groupby(["regi", filtered1_df["date"].dt.year])["temp"].mean().reset_index(),
                   x="date", y="temp", color="regi", labels={"date": "Year", "temperature": "Average Temperature (C)"})
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
