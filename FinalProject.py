'''
Author: Alisher Ubaydulloev
CS 230: Section 4
Data: AirBnB
date: 12.12.2021
'''

default_region = ["Westminster", "Islington"]
default_price = 600
default_type = ["Private room"]

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pydeck as pdk


# open data and read it
def open_file():
    return pd.read_csv("LondonAirBnBSep2021.csv").set_index("id")

# filter the data
def filter_data(sel_cost, sel_region, sel_type):
    df = open_file()
    df = df.loc[df['price'] < sel_cost]
    df = df.loc[df['neighbourhood'].isin(sel_region)]
    df = df.loc[df['room_type'].isin(sel_type)]

    return df


# icnlude streamlit options for regions
def all_regions():
    df = open_file()
    listRegions = []
    for ind, row in df.iterrows():
        if row['neighbourhood'] not in listRegions:
            listRegions.append(row['neighbourhood'])

    return listRegions

# icnlude streamlit options for room types
def all_types():
    df = open_file()
    listTypes = []
    for ind, row in df.iterrows():
        if row['room_type'] not in listTypes:
            listTypes.append(row['room_type'])

    return listTypes

# count the number of properties in selected region draw a chart
def count_region(sel_regions, df):
    return [df.loc[df['neighbourhood'].isin([neighbourhood])].shape[0] for neighbourhood in sel_regions]

# draw a chart
def chart(count, sel_regions):
    plt.figure()


    explodes = [0 for i in range(len(count))] # put some space in pie chart
    maximum = count.index(np.max(count))
    explodes[maximum] = 0.05
    plt.pie(count, labels=sel_regions, explode=explodes, autopct="%.2f")
    plt.title(f"The proportion of selected neighbourhoods: {', '.join(default_region)}")
    return plt

# create list of prices for each region
def price_regions(df):
    prices = [row['price'] for ind, row in df.iterrows()]
    regions = [row['neighbourhood'] for ind, row in df.iterrows()]

    dict = {}
    for region in regions:
        dict[region] = [] # make dict based on key

    for i in range(len(prices)):
        dict[regions[i]].append(prices[i])
    return dict

# ready to find average price on each region based on list
def price_average(dict_prices):
    dict = {}
    for key in dict_prices.keys():
        dict[key] = np.mean(dict_prices[key])

    return dict

# generate histogram
def price_histogram(dictAverages):
    x = dictAverages.keys()
    y = dictAverages.values()

    plt.bar(x, y)
    plt.xticks(rotation=45)
    plt.ylabel("Price")
    plt.xlabel("Regions")
    plt.title(f"Average listing prices in selected regions: {', '.join(dictAverages.keys())}")
    return plt

# put map
def create_map(df):
    map_df = df.filter(['latitude', 'longitude'])

    view_state = pdk.ViewState(latitude=map_df["latitude"].mean(), longitude=map_df["longitude"].mean(), zoom=12)
    layer = pdk.Layer('ScatterplotLayer', data=map_df, get_position='[longitude, latitude]', get_radius=70,
                      get_color=[220, 117, 156],
                      pickable=True)
    tool_tip = {'html': 'Listing:<br/> <b>{name}</b>', 'style': {'backgroundColor': 'steelblue', 'color': 'white'}}
    map = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9', initial_view_state=view_state, layers=[layer],
                   tooltip=tool_tip)

    st.pydeck_chart(map)

# create main function
def main():
    st.title("Get the best of Airbnb with our website!")
    st.write("Not sure where to stay? Just open the sidebars!")

    st.sidebar.write("Please sort your destinations from options below.")
    regions = st.sidebar.multiselect("Select a region: ", all_regions())

    maxPrice = st.sidebar.slider("Max price: ", 0, 500)
    roomType = st.sidebar.multiselect("Room type : ", all_types())

    data = filter_data(maxPrice, regions, roomType)
    series = count_region(regions, data)

    if len(regions) > 0 and maxPrice > 0 and len(roomType) > 0:
        st.write("View your options on map")
        create_map(data)

        st.write("View some statistics: ")
        st.pyplot(price_histogram(price_average(price_regions(data))))
        st.pyplot(chart(series, regions))


main()

