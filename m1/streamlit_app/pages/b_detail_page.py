import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from vega_datasets import data as vega_data
from duckduckgo_search import DDGS
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
    count_df = data.groupby('sector')['id'].count().reset_index().rename(columns={'id':'nbr_of_loan'})
    ## dùng plt thì không resize và interactive được
    # fig = plt.figure()
    # plt.bar(data['sector'], data['id'], color='#219EBC')
    # plt.xlabel('Sectors')
    # plt.ylabel('Number of Loans')
    # st.pyplot(fig)
    st.bar_chart(count_df, x='sector', y='nbr_of_loan', color='#219EBC', x_label='Sectors', y_label=var)

    ## ----------------line chart - nbr over time ------------------------
    st.header(f'{var} overtime')
    data['disbursed_time_formatted'] = data['disbursed_time'].dt.strftime('%Y-%m')
    time_df = data.groupby('disbursed_time_formatted')['id'].count().reset_index().rename(columns={'id':'nbr_of_loan'})
    st.line_chart(time_df, x='disbursed_time_formatted', y='nbr_of_loan', color='#05547b', x_label='Disbursed Time', y_label=var)

    ## ----------------geo heatmap ------------------------
    st.header(f'{var} by Country')
    geo_df = data.groupby(['country-code', 'name'])['id'].count().reset_index().rename(columns={'id':'loan_count'})
    make_geo_chart(geo_df, 'loan_count', var)
    return f'''data about number of loan:
               1. nbr_of_loan_by_sector: {str(count_df)};
               2. nbr_of_loan_overtime: {str(time_df)};
               3. nbr_of_loan_by_country: {str(geo_df)}
               '''


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

    return f'''data about total loan amount:
               1. total_loan_amount_by_sector: {str(sum_df)};
               2. disbursed_amount_overtime: {str(time_df)};
               3. loan_amount_by_country: {str(geo_df)}
               '''

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

    return f'''data about average loan amount:
               1. avg_loan_amount_by_sector: {str(sum_df)};
               2. avg_amount_overtime: {str(time_df)};
               3. avg_amount_by_country: {str(geo_df)}
               '''

if __name__ == '__main__':
    st.title('Detail Analysis - Select variable to explore:')
    df = fetch_and_clean_data()
    filtered_df = get_filtered_data(df)
    var = st.selectbox(label='', options=['Number of Loans', 'Total Loan Amount', 'Average Loan Amount'])
    if var == 'Number of Loans':
        info_text = nbr_loans(filtered_df)
    elif var == "Total Loan Amount":
        info_text = loan_amount(filtered_df)
    elif var == 'Average Loan Amount':
        info_text = avg_loan_amount(filtered_df)

    if st.button('AI Assitant'):
            with st.expander('Take a look!:'):
                st.markdown(DDGS().chat(f'''summarize and make recommendation based on Kiva's loan info: {info_text}''', model='gpt-4o-mini'))
    
