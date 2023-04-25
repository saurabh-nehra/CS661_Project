# CS661_Project

Create a config.toml file in:

"C:\Users\<user>\.streamlit\config.toml" for Windows
In the directory where Streamlit App is located for Linux/Mac

Add the following code to the config.toml file:

####################################################

[server]
maxUploadSize = 500

maxMessageSize = 500

####################################################

Stremlit has a by default max data size of 250mb.
Since our data is larger than that, we are increasing the limit to 500mb using the above code.

Raw Dataset: https://www.kaggle.com/datasets/PROPPG-PPG/hourly-weather-surface-brazil-southeast-region

Cleaned and Reduced Dataset: https://drive.google.com/file/d/1Ko5ujthAwLAVQKayeZ_EKT_tAjDE3VH0/view?usp=sharing

Predicted Datasets folder: https://drive.google.com/drive/folders/1XQfUxC7FTnF-cre6IuJEensiejYqhMfd?usp=sharing

Download the raw .csv files in the cleaning folder
Download the Cleaned and reduced .sv file in the cleaning folder
Download predicted datasets in the parent folder

##################################################

CLEANING (OPTIONAL, TAKES TIME)

1. Run centralwest.ipynb, north.ipynb, northeast.ipynb, south.ipynb, southeast.ipynb

This will reduce the data from hourly to daily, and removing unwanted columns.
Since each .csv file in the raw data is very large (~2GB) the code takes long time to run.
Cleaned data can be used directly (download from the google drive link above) instead.

2. After the above notebooks have generated cleaned files in the cleaning folder,
run combine.ipynb to create combined.csv (Combined and reduced daily data of all regions)

3. After generating combined.csv, run the reduce.ipynb to reduce the number
of decimal places in the data, further reducing the size of the data.
Final cleaned data is named combined_reduced.csv

##################################################

WEATHER PREDICTION (OPTIONAL, TAKES TIME)

1. Run predict.ipynb on /cleaning/combined_reduced.csv (Download from drive link ok create from cleaning)

This will create weather_states.csv. It will have a new column added to the data
which will show the weather state at each day

2. Run model.ipynb on weather_states.csv.

This will create weather_states1.csv (Same as weather_states.csv but with variable classes)
And also create predicted_weather.csv (Predicted weather for over 1 year using Markov Model)

3. Run predicted_correct.ipynb on predicted_weather.csv

This will create predicted.csv, this will have a states column too unlike predicted_weather.csv

4. Run comparison.ipynb to compare the predicted vs actual weather data
by representing both on a map. This will also show the model accuracy.

##################################################

DATA VISUALISATION

1. Run project.py in your terminal using the following command

Streamlit run project.py

Make sure that config.toml is created at the location mentioned earlier.
The code will create brazil_map.html when the exploration tab is opened.
This map will be updated everytime a new date is selected in the exploration tab
and the map will be opened in a new tab.

Navigate through the web based app and have fun <3



