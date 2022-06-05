from datetime import datetime,date
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob, os
import altair as alt
from io import BytesIO
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mpl_dates


#space function to control layout
def space(num_lines=1):
    for _ in range(num_lines):
        st.write("")

st.set_page_config(layout="wide",page_icon="💰",page_title="U.S. stocks owned by Warren Buffett")
#add a title
st.title('Warren Buffett U.S. Stocks Portfolio')
space(1)
st.image('photo1.jpeg')
st.markdown('##### This is a summary about the 45 publicly traded U.S. stocks owned by Warren Buffett’s holding company'
            ' Berkshire Hathaway, as reported to the SEC.')
space(2)
###############data preparation
DATE_COLUMN = 'Date'
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

######### Create a list to display company information
data_load_state = st.text('Loading data...')
c1 = load_descdata("archive/Company List.csv")[:-1]
c2 = load_descdata('archive/stock_profile.csv')
c_profile = c2.reset_index().merge(c1,on="Symbol").set_index('Name')
data_load_state.text("Done!")

st.header('Company Investigation')
# Display company information
if st.checkbox("Show full company list"):
    st.subheader('Company List')
    st.table(c_profile)

space(2)

############## Create a pie chart to show the distribution of companies by Sector
def pie_chart(category):
    data_pie = c_profile.groupby(category)['Stake'].count().reset_index()
    labels = data_pie[category]
    sizes = data_pie['Stake']

    #width = st.sidebar.slider("plot width", 1, 25, 3)
    #height = st.sidebar.slider("plot height", 1, 25, 1)
    fig1, ax1 = plt.subplots()
    cmap = plt.get_cmap("tab20")
    ax1.pie(sizes, labels=labels, radius = 1, autopct='%1.1f%%',colors = cmap(np.arange(len(sizes))),
            startangle=90, pctdistance=0.85,textprops={'fontsize': 8},wedgeprops={'edgecolor': 'white', 'linewidth': 1},)
    #draw circle
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig1 = plt.gcf()
    fig1.gca().add_artist(centre_circle)


    ax1.set_title("What Sectors are Buffet Investing in?",fontsize=12,pad=30,horizontalalignment='center')
    ax1.axis('equal')
    return fig1

st.subheader('Sector and Industry')
space(1)
p1, p2 = st.columns(2)
with p1:
    st.pyplot(pie_chart('Sector'))
with p2:
    option = st.selectbox(
         'Choose a sector to explore',
         c_profile.Sector.unique())
    st.table(c_profile[c_profile.Sector==option][['Industry','Num_Employees']])


space(2)
############### Create a bar chart to show the top 10 companies and industries buffet invested in
st.subheader('Main Components of the Portfolio')
space(1)

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

    ax2.set_title("Top10 Holding of Companies Measured by "+title,fontsize= 17,pad=30,horizontalalignment='center')

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
    st.pyplot(top10_plot(top10_Stake,'Stake','Stake Invested'))

space(2)

##########Visualizing stock price
#Load data from csv files
st.header('Evolution of Stock Prices')
space(1)

mycsvdir = "archive/stock"
csvfiles = glob.glob(os.path.join(mycsvdir, '*.csv'))
df_dict = dict()
for csvfile in csvfiles:
    df_dict[csvfile.split('/')[2].split('.')[0]] = load_stockdata(csvfile)

s1, s2 = st.columns(2)
with s1:
    all_symbols = tickers
    symbols = st.multiselect("Choose stocks to visualize", all_symbols, all_symbols[:3])


    selected = list(set(df_dict.keys())&set(symbols))
    sub = dict((k,df_dict[k]) for k in selected)
    fig3, ax3 = plt.subplots()

    for x,frame in sub.items():
        ax3.plot("Date", "Adj Close", lw=1.8, data=frame, label=x)
        st.write()

    plt.xticks(rotation=0, fontsize=10, horizontalalignment='center', alpha=.7)
    plt.yticks(fontsize=10, alpha=.7)
    fig3.suptitle("Trends of Stock Prices Over Decades", fontsize=15)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Price (USD)')
    plt.legend()
    fig3.tight_layout()
    st.write(fig3)

with s2:
    option = st.selectbox(
         'Choose one stock to visualize',
         tickers)
    data = df_dict[option]
    ohlc = data.loc[:, ['Date', 'Open', 'High', 'Low', 'Close']]
    with st.sidebar:
        st.subheader('Select dates to view the daily stock prices change (Candlestick Chart)')
        sf = st.date_input(
         "Start from",
        date(2017, 1, 1))
        eb = st.date_input(
         "End by",
        date(2017, 3, 1))

    start = datetime.combine(sf, datetime.min.time())
    end = datetime.combine(eb, datetime.min.time())

    ohlc = ohlc.set_index('Date')[start:end].reset_index()
    ohlc['Date'] = ohlc['Date'].apply(mpl_dates.date2num)
    ohlc = ohlc.astype(float)

    # Creating Subplots
    fig4, ax4 = plt.subplots()
    candlestick_ohlc(ax4, ohlc.values, width=0.6, colorup='green', colordown='red', alpha=0.8)
    # Setting labels & titles
    ax4.set_xlabel('Date')
    ax4.set_ylabel('Price (USD)')
    fig4.suptitle('Daily Candlestick Chart of '+option)

    # Formatting Date
    date_format = mpl_dates.DateFormatter('%d-%m-%Y')
    ax4.xaxis.set_major_formatter(date_format)
    fig4.autofmt_xdate()
    fig4.tight_layout()
    st.write(fig4)
