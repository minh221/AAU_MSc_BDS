import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
from vega_datasets import data as vega_data
from pages.a_main_page import fetch_and_clean_data, display_filter, filtering, get_filtered_data

def make_geo_chart(data: pd.DataFrame, quan_col:str, var_name:str):
    world_map = alt.topo_feature(vega_data.world_110m.url, 'countries')
    background = alt.Chart(world_map).mark_geoshape(
            fill="white",
            stroke="#05547b", strokeWidth=0.6
        ).properties(
            width=800,
            height=600
        ).transform_filter(
            alt.datum.id != 10
        ).project(type='naturalEarth1')

    foreground = alt.Chart(world_map).mark_geoshape(stroke="#05547b", strokeWidth=0.15)\
            .encode(
                color=alt.Color(f'{quan_col}:Q', title=var_name, scale=alt.Scale(scheme='blues')),
                tooltip=[alt.Tooltip('name:N', title='Country'), alt.Tooltip(f'{quan_col}:Q', title=quan_col, format=',')])\
            .transform_lookup(
                lookup='id',
                from_=alt.LookupData(data, 'country-code', [quan_col, 'name']))\
            .project(
                type='naturalEarth1')\
            .properties(
                width=800,
                height=600)
    
    st.altair_chart(background+foreground, use_container_width=True)


def nbr_loans(data: pd.DataFrame):
    ## ----------------bar chart - nbr by sector ------------------------
    st.header(f'{var} by Sectors')
    count_df = data.groupby('sector')['id'].count().reset_index()
    ## dùng plt thì không resize và interactive được
    # fig = plt.figure()
    # plt.bar(data['sector'], data['id'], color='#219EBC')
    # plt.xlabel('Sectors')
    # plt.ylabel('Number of Loans')
    # st.pyplot(fig)
    st.bar_chart(count_df, x='sector', y='id', color='#219EBC', x_label='Sectors', y_label=var)

    ## ----------------line chart - nbr over time ------------------------
    st.header(f'{var} overtime')
    data['disbursed_time_formatted'] = data['disbursed_time'].dt.strftime('%Y-%m')
    time_df = data.groupby('disbursed_time_formatted')['id'].count().reset_index()
    st.line_chart(time_df, x='disbursed_time_formatted', y='id', color='#05547b', x_label='Disbursed Time', y_label=var)

    ## ----------------geo heatmap ------------------------
    st.header(f'{var} by Country')
    geo_df = data.groupby(['country-code', 'name'])['id'].count().reset_index().rename(columns={'id':'loan_count'})
    make_geo_chart(geo_df, 'loan_count', var)


def loan_amount(data: pd.DataFrame):
    ## ----------------bar chart - nbr by sector ------------------------
    st.header(f'{var} by Sectors')
    sum_df = data.groupby('sector')['loan_amount'].sum().reset_index()
    st.bar_chart(sum_df, x='sector', y='loan_amount', color='#219EBC', x_label='Sectors', y_label=var)

    ## ----------------line chart - nbr over time ------------------------
    st.header(f'{var} overtime')
    data['disbursed_time_formatted'] = data['disbursed_time'].dt.strftime('%Y-%m')
    time_df = data.groupby('disbursed_time_formatted')['loan_amount'].sum().reset_index()
    st.line_chart(time_df, x='disbursed_time_formatted', y='loan_amount', color='#05547b', x_label='Disbursed Time', y_label=var)

    ## ----------------geo heatmap ------------------------
    st.header(f'{var} by Country')
    geo_df = data.groupby(['country-code', 'name'])['loan_amount'].sum().reset_index()
    make_geo_chart(geo_df, 'loan_amount', var)

def avg_loan_amount(data: pd.DataFrame):
    ## ----------------bar chart - nbr by sector ------------------------
    st.header(f'{var} by Sectors')
    sum_df = data.groupby('sector')['loan_amount'].mean().reset_index().rename(columns={'loan_amount':'avg_loan_amount'})
    st.bar_chart(sum_df, x='sector', y='avg_loan_amount', color='#219EBC', x_label='Sectors', y_label=var)

    ## ----------------line chart - nbr over time ------------------------
    st.header(f'{var} overtime')
    data['disbursed_time_formatted'] = data['disbursed_time'].dt.strftime('%Y-%m')
    time_df = data.groupby('disbursed_time_formatted')['loan_amount'].mean().reset_index().rename(columns={'loan_amount':'avg_loan_amount'})
    st.line_chart(time_df, x='disbursed_time_formatted', y='avg_loan_amount', color='#05547b', x_label='Disbursed Time', y_label=var)

    ## ----------------geo heatmap ------------------------
    st.header(f'{var} by Country')
    geo_df = data.groupby(['country-code', 'name'])['loan_amount'].mean().reset_index().rename(columns={'loan_amount':'avg_loan_amount'})
    make_geo_chart(geo_df, 'avg_loan_amount', var)

if __name__ == '__main__':
    st.title('Detail Analysis - Select variable to explore:')
    df = fetch_and_clean_data()
    filtered_df = get_filtered_data(df)
    var = st.selectbox(label='', options=['Number of Loans', 'Total Loan Amount', 'Average Loan Amount'])
    if var == 'Number of Loans':
        nbr_loans(filtered_df)
    elif var == "Total Loan Amount":
        loan_amount(filtered_df)
    elif var == 'Average Loan Amount':
        avg_loan_amount(filtered_df)
