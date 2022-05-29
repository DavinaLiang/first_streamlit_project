from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob, os
import altair as alt
from io import BytesIO

#space function to control layout
def space(num_lines=1):
    for _ in range(num_lines):
        st.write("")

st.set_page_config(layout="wide",page_icon="💰",page_title="U.S. stocks owned by Warren Buffett")
#add a title
st.title('Warren Buffett U.S. Stocks Portfolio')

###############data preparation
DATE_COLUMN = 'Date'
tickers = ['AMZN','AXP','AAPL','AXTA','BAC','BK','GOLD','BIIB','CHTR','KO','COST','DVA','GM','GL','JNJ','JPM','KHC','KR',
           'LBTYA','LBTYK','LILA','LILAK','LSXMA','LSXMK','MTB','MA','MDLZ','MCO','PNC','PG','RH','SIRI','SNOW','SPY','STNE',
           'STOR','SU','SYF','TEVA','USB','UPS','VOO','VRSN','V','WFC']

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)

#effortless caching: relieve long-running computation in your code for continuously updating
@st.cache
def load_stockdata(data):
    data = pd.read_csv(data)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

def load_descdata(data):
    data = pd.read_csv(data,delimiter=';',index_col="Name")
    return data

def percent_to_float(s):
    s = str(float(s.rstrip("%")))
    i = s.find(".")
    if i == -1:
        return int(s) / 100
    if s.startswith("-"):
        return -percent_to_float(s.lstrip("-"))
    s = s.replace(".", "")
    i -= 2
    if i < 0:
        return float("." + "0" * abs(i) + s)
    else:
        return float(s[:i] + "." + s[i:])

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
c1 = load_descdata("archive/Company List.csv")[:-1]
c2 = load_descdata('archive/stock_profile.csv')
c_profile = c2.reset_index().merge(c1,on="Symbol").set_index('Name')
data_load_state.text("Done!")
# Display company information
if st.checkbox("Show complete company list"):
    st.subheader('Company List')
    st.table(c_profile)

space(2)

############## Create a pie chart to show the distribution of companies by Sector
data_pie = c_profile.groupby(['Sector'])['Stake'].count().reset_index()
labels = data_pie['Sector']
sizes = data_pie['Stake']

#width = st.sidebar.slider("plot width", 1, 25, 3)
#height = st.sidebar.slider("plot height", 1, 25, 1)
fig1, ax1 = plt.subplots()
cmap = plt.get_cmap("tab20")
ax1.pie(sizes, labels=labels, radius = 1, autopct='%1.1f%%',colors = cmap(np.arange(len(sizes))),
        startangle=90, pctdistance=0.85,textprops={'fontsize': 5},wedgeprops={'edgecolor': 'white', 'linewidth': 1},)
#draw circle
centre_circle = plt.Circle((0,0),0.70,fc='white')
fig1 = plt.gcf()
fig1.gca().add_artist(centre_circle)


ax1.set_title("What Sectors are Buffet Investing in?",fontsize=10,pad=30,horizontalalignment='center')
ax1.axis('equal')
st.pyplot(fig1)

############### Create a bar chart to show the top 10 companies and industries buffet invested in
c_profile['Stake'] = c_profile['Stake'].apply(lambda s:percent_to_float(s))
c_profile['Market Price'] = c_profile['Market Price'].replace('[\$,]', '', regex=True).astype(float)
c_profile['Value'] = c_profile['Value'].replace('[\$,]', '', regex=True).astype(float)
top10_Value = c_profile.sort_values(by='Value',ascending=False)[:10]
top10_Stake = c_profile.sort_values(by='Stake',ascending=False)[:10]

def top10_plot(data,by,title):
    # we first need a numeric placeholder for the y axis
    my_range=list(range(1,len(data.index)+1))
    fig2, ax2 = plt.subplots()
    # create for each expense type an horizontal line that starts at x = 0 with the length
    # represented by the specific expense percentage value.
    plt.hlines(y=my_range, xmin=0, xmax=data[by], color='#007ACC', alpha=0.2, linewidth=5)
    # create for each expense type a dot at the level of the expense percentage value
    plt.plot(data[by], my_range, "o", markersize=5, color='#007ACC', alpha=0.6)
    # set labels
    ax2.set_xlabel(by, fontsize=15, fontweight='black', color = '#333F4B')
    ax2.set_ylabel('')

    # set axis
    ax2.tick_params(axis='both', which='major', labelsize=12)
    plt.yticks(my_range, data.index)

    ax2.set_title("Top10 Holding of Companies Measured by "+title,fontsize= 20,pad=30,horizontalalignment='center')

    # change the style of the axis spines
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_bounds((1, len(my_range)))
    ax2.spines['left'].set_position(('outward', 8))
    ax2.spines['bottom'].set_position(('outward', 5))
    return fig2

col1, col2 = st.columns(2)
with col1:
    st.pyplot(top10_plot(top10_Value,'Value','Capital Invested'))
with col2:
    st.pyplot(top10_plot(top10_Stake,'Stake','Stake'))



##########Visualizing stock price
#Load data from csv files
mycsvdir = "archive/stock"
csvfiles = glob.glob(os.path.join(mycsvdir, '*.csv'))
df_dict = dict()
for csvfile in csvfiles:
    df_dict[csvfile.split('/')[2].split('.')[0]] = load_stockdata(csvfile)

all_symbols = tickers
symbols = st.multiselect("Choose stocks to visualize", all_symbols, all_symbols[:3])

space(1)

selected = list(set(df_dict.keys())&set(symbols))
sub = dict((k,df_dict[k]) for k in selected)
fig3, ax3 = plt.subplots(figsize = (14, 8.5))

for x,frame in sub.items():
    ax3.plot("Date", "Adj Close", lw=1.8, data=frame, label=x)


plt.xticks(rotation=0, fontsize=10, horizontalalignment='center', alpha=.7)
plt.yticks(fontsize=10, alpha=.7)
plt.title("Evolution of Stock Prices", fontsize=15)
plt.xlabel('Year')
plt.ylabel('Price (USD)')
plt.legend()
st.write(fig3)
