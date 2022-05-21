from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#space function to control layout
def space(num_lines=1):
    for _ in range(num_lines):
        st.write("")

st.set_page_config(layout="centered",page_icon="💰",page_title="U.S. stocks owned by Warren Buffett")
#add a title
st.title('Warren Buffett U.S. Stocks Portfolio')

###############data preparation
DATE_COLUMN = 'date/time'
tickers = ['AMZN','AXP','AAPL','AXTA','BAC','BK','GOLD','BIIB','CHTR','KO','COST','DVA','GM','GL','JNJ','JPM','KHC','KR',
           'LBTYA','LBTYK','LILA','LILAK','LSXMA','LSXMK','MTB','MA','MDLZ','MCO','PNC','PG','RH','SIRI','SNOW','SPY','STNE',
           'STOR','SU','SYF','TEVA','USB','UPS','VOO','VRSN','V','WFC']

#effortless caching: relieve long-running computation in your code for continuously updating
@st.cache
def load_stockdata(data):
    data = pd.read_csv(data)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

def load_descdata(data):
    data = pd.read_csv(data,delimiter=';',index_col="Name")
    return data
# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
c_info = load_descdata("archive/Company List.csv")[:-1]
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done!")

fig, ax = plt.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))


if st.checkbox("Show complete company list"):
    st.subheader('Company List')
    st.table(c_info)

##########Draw a histogram
#add a sub header
st.subheader('Number of pickups by hour')
#use numpy to generate a histogram
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

#########Plot data on a map
#####show the concentration of pickups at each hour
hour_to_filter = st.slider('hour', 0, 23, 17)  # min: 0h, max: 23h, default: 17h
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f'Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)
#Filter results with a slider
