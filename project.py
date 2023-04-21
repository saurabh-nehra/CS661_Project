import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st

#############################################################
# Load the weather data from the CSV file
weather_df = pd.read_csv("./data/combined.csv")

# Take a sample of 5000 points from weather data
sample_df = weather_df.sample(5000, random_state=101)

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
def scatter_page(sample_df):
    st.title("Temperature vs. Pressure by Station")
    st.write(
        "Here is an animated scatter plot of temperature vs. pressure by station:")
    # Convert the datetime column to a string column
    sample_df['date'] = sample_df['date'].astype('str')
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
def heatmap_page(filtered_df, region):
    st.title("Precipitation Density Map by Region")
    st.write(
        "Here is an animated heatmap of precipitation density of selected region:")
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
    fig.update_layout(title=f"Rain and Temperature in {region}",
                      coloraxis_colorbar=dict(title="Temperature (°C)"))
    st.plotly_chart(fig)


# create the exploration page
def exploration_page():
    st.title("Exploration Page")
    st.write("Explore the weather data with the following options:")

    # Define the widgets for user interaction
    region = st.selectbox("Select a region", sorted(
        sample_df["regi"].unique()))

    # Filter the data based on the user's selections
    filtered_df = sample_df[(sample_df["regi"] == region)]

    st.write("Found {} rows".format(len(filtered_df)))
    # display the filtered data
    st.write(filtered_df)

    # Heat Map:
    heatmap_page(filtered_df, region)
    # Scatter Plot:
    scatter_page(sample_df)

# create the visualization page


def visualization_page():
    st.title("Visualization Page")
    st.write("Visualize the weather data with the following options:")

    # Set the default map center and zoom level
    default_coords = (-14.23, -53.18)

    # Define the layout of the interface
    st.sidebar.header("Filters")

    # Create a list of unique regions and stations for filtering
    regions = sorted(sample_df["regi"].unique())
    stations = sorted(sample_df["wsnm"].unique())

    # Convert the 'date' column to datetime format
    sample_df['date'] = pd.to_datetime(sample_df['date'])

    # Create the sidebar widgets (the filters for the interface)
    region_filter = st.sidebar.multiselect(
        "Select region(s)", regions, default=regions)
    date_range = st.sidebar.date_input(
        "Select date range", value=(sample_df["date"].min(), sample_df["date"].max()))
    station_filter = st.sidebar.multiselect(
        "Select station(s)", stations, default=stations)

    # Filter the data based on the user's selection
    filtered_df = sample_df[
        (sample_df["regi"].isin(region_filter)) &
        (sample_df["wsnm"].isin(station_filter)) &
        (sample_df["date"] >= date_range[0].strftime("%Y-%m-%d")) &
        (sample_df["date"] <= date_range[1].strftime("%Y-%m-%d"))
    ]

    # Display the filtered data
    st.write(f"Found {len(filtered_df)} rows.")
    st.write(filtered_df)

    # Create a map visualization of the data
    fig1 = px.scatter_mapbox(
        filtered_df,
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
    fig5 = px.density_mapbox(filtered_df, lat="lat", lon="lon", z="temp", radius=10, zoom=2,
                             hover_name="inme", animation_frame=filtered_df["date"].dt.year,
                             mapbox_style="open-street-map", opacity=0.5)
    st.plotly_chart(fig5)

    # Create a histogram of the temperature data
    fig2 = px.histogram(
        filtered_df,
        x="temp",
        nbins=20,
        title="Distribution of Temperature"
    )
    st.plotly_chart(fig2)

    # Define the visualizations for the interface
    st.header("Temperature vs. Precipitation")
    fig3 = px.scatter(filtered_df, x="temp", y="prcp",
                      color="regi", hover_name="inme")
    st.plotly_chart(fig3)

    st.header("Average Temperature by Region and Year")
    fig4 = px.line(filtered_df.groupby(["regi", filtered_df["date"].dt.year])["temp"].mean().reset_index(),
                   x="date", y="temp", color="regi", labels={"date": "Year", "temperature": "Average Temperature (C)"})
    st.plotly_chart(fig4)

    # Bar Chart:
    bar_chart(filtered_df)
    # Line Chart:
    line_chart(filtered_df)


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
