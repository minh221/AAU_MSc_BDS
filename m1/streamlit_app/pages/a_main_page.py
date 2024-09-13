import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from duckduckgo_search import DDGS

@st.cache_data
def fetch_and_clean_data():
    loan_data = [pd.read_csv(f'https://github.com/minh221/AAU_MSc_BDS/raw/main/m1/data/kiva_data_{i}.zip') for i in [1,2]]
    ## concat all parts of kiva_loan_data
    data = pd.concat(loan_data)
    iso = pd.read_csv('https://raw.githubusercontent.com/minh221/AAU_MSc_BDS/main/m1/data/iso_3166.csv')
    iso = iso[['name', 'alpha-2', 'alpha-3', 'country-code', 'region', 'sub-region']].rename( columns={'region':'world_region'}
    )

    ## --------------------------------------------- Cleaning data ------------------------------------------
    data.dropna(subset=['borrower_genders', 'country_code', 'disbursed_time', 'funded_time'], inplace=True)

    ## using the IQR method to remove outliers in loan amount
    Q1 = np.percentile(data['loan_amount'], 25, method='midpoint')
    Q3 = np.percentile(data['loan_amount'], 75, method='midpoint')
    IQR = Q3 - Q1
    # finding the upper and lower bound
    upper = Q3 + 1.5*IQR
    lower = Q1 - 1.5*IQR
    # remove outliers
    data = data[(data['loan_amount'] < upper) & (data['loan_amount'] > lower)]

    ## change the datatype of the datetime columns
    date_cols = ['posted_time', 'disbursed_time', 'funded_time', 'date']
    for col in date_cols:
        data[col] = pd.to_datetime(data[col])
    
    ## join with mpi_df to find the world region
    data = iso.merge(data, left_on='alpha-2', right_on='country_code')

    return data


## ---------------------------------------------- Starting building app -----------------------------------------
## function for filtering data based on selection
def filtering(data: pd.DataFrame, column: str, values: list[str]) -> pd.DataFrame:
    return data[data[column].isin(values)] if values else data

## display sidebar and filters
def display_filter(data):
    st.sidebar.header("Filters")

    start_date = pd.Timestamp(st.sidebar.date_input("Start date", data['date'].min().date()))
    end_date = pd.Timestamp(st.sidebar.date_input("End date", data['date'].max().date()))

    selected_world_regions = st.sidebar.multiselect("Select World region", sorted(data['world_region'].unique()))
    selected_countries = st.sidebar.multiselect("Select Country", sorted(data['name'].unique()))
    selected_sector = st.sidebar.multiselect("Select Sector", sorted(data['sector'].unique()))
    selected_subsector = st.sidebar.multiselect("Select Sub-sector", sorted(data['activity'].unique()))

    return start_date, end_date, selected_world_regions, selected_countries, selected_sector, selected_subsector

## calculate and display KPIs
def display_kpi(data):
    ## calculating metrics
    nr_country = f"{len(data['name'].unique())} countries"
    total_loan_amt = data['loan_amount'].sum()
    loan_amt_in_M = f"{total_loan_amt/1000000 :.2f}M USD"
    nr_loan = f"{len(data) :,}"
    avg_loan_amt = f"{total_loan_amt/len(data) :.2f} USD"
    
    ## displaying
    kpi_names = ['Number of Markets', 'Number of Loans', 'Total Loan Amount', 'Average Loan Amount']
    kpi_values = [nr_country, nr_loan, loan_amt_in_M, avg_loan_amt]
    st.header("KPI Metrics")
    for i, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(4), zip(kpi_names, kpi_values))):
        col.metric(label=kpi_name, value=kpi_value)
    return str({'nbr_of_market_country':nr_country, 
                'loan_amt_in_M': loan_amt_in_M, 
                'avg_loan_amt': avg_loan_amt})

def get_filtered_data(data):
    start_date, end_date, selected_world_regions, selected_countries, selected_sector, selected_subsector = display_filter(data)
    filtered_df = filtering(data, 'world_region', selected_world_regions)
    filtered_df = filtering(filtered_df, 'name', selected_countries)
    filtered_df = filtering(filtered_df, 'sector', selected_sector)
    filtered_df = filtering(filtered_df, 'activity', selected_subsector)
    filtered_df = filtered_df[filtered_df['date'].between(start_date, end_date)]

    return filtered_df

def dist_loan_amount(data, col):
    fig, ax = plt.subplots()
    plot = ax.boxplot(df['loan_amount'], patch_artist=True, tick_labels=['loan_amount'])
    plot['boxes'][0].set_facecolor('#219EBC')
    
    with col:
        # st.markdown('<div class="custom-column">', unsafe_allow_html=True)    
        col.header = "Distribution of Loan Amount (USD)"
        col.write("Distribution of Loan Amount (USD)")
        st.pyplot(fig)
    return str(df['loan_amount'].describe())


def bar_loan_term(data, col):
    bin_edges = [0, 6, 12, 36, 60, 120]
    bin_labels = ['< 6M', '6M - 1Y', '1-3 Y', '3-5 Y', '5-10 Y']
    data['loan_term'] = pd.cut(data['term_in_months'], bins=bin_edges, labels=bin_labels, right=False)
    grouped = data.groupby('loan_term')['id'].count().reset_index().rename(columns={'id':'nbr_of_loan'})

    fig, ax = plt.subplots()
    ax.bar(grouped['loan_term'], grouped['nbr_of_loan'], color='#219EBC')
    
    with col:
        col.header = "Number of Loans by Loan Term"
        col.write("Number of Loans by Loan Term")
        st.pyplot(fig)
    return str(grouped[['loan_term', 'nbr_of_loan']])

def days_fully_funded(data, col):
    data['day_to_funded'] = (data['funded_time'] - data['disbursed_time']) / np.timedelta64(1, 'D')
    df_days = data[~((data['day_to_funded'].isna()) | (data['day_to_funded'] < 0))]

    fig, ax = plt.subplots()
    ax.hist(df_days['day_to_funded'], color='#219EBC', density=True, bins=int(df_days['day_to_funded'].max()-df_days['day_to_funded'].min()))
    
    with col:
        col.header = "Number of Loans by Days to Fully Funded"
        col.write("Number of Loans by Days to Fully Funded")
        st.pyplot(fig)
    return str(df_days['day_to_funded'].describe())

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


if __name__ == '__main__':
    df = fetch_and_clean_data()
    filtered_df = get_filtered_data(df)
    kpi_str = display_kpi(filtered_df)

    col1, col2, col3 = st.columns(3)
    
    loan_amount_str = dist_loan_amount(filtered_df, col1)
    loan_term_str = bar_loan_term(filtered_df, col2)
    days_funded_str = days_fully_funded(filtered_df, col3)
    local_css("C:/Users/ADMIN/Downloads/MSc Business Data Science/bds_assignment/m1/streamlit_app/style_main.css")
    chat_text = f'''This is loan information of Kiva, with these kpis: {kpi_str};
                        and discribe of loan amount: {loan_amount_str}
                        and table number of loans by loan_term: {loan_term_str}
                        and describe of number_of_days_to_fully_funded: {days_funded_str}
                    As an advanced data analyst, generate 4 short sentences to summarize and give recommendation for each point,
                    display in vertical order
                    '''
    if st.button('AI Assitant'):
        with st.expander('Take a look!:'):
            st.markdown(DDGS().chat(chat_text, model='gpt-4o-mini'))