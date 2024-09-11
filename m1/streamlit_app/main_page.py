import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(layout="wide")

@st.cache_data
def fetch_and_clean_data():
    loan_data = [pd.read_csv(f'https://github.com/minh221/AAU_MSc_BDS/raw/main/m1/kiva_data_{i}.zip') for i in [1,2]]
    ## concat all parts of kiva_loan_data
    data = pd.concat(loan_data)
    mpi = pd.read_csv('https://raw.githubusercontent.com/aaubs/ds-master/main/data/assignments_datasets/KIVA/kiva_mpi_region_locations.csv')

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
    data = data.merge(mpi[['country', 'world_region']].drop_duplicates(), on='country')

    mpi = mpi[['country', 'region', 'MPI']].dropna()

    return data, mpi


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
    selected_countries = st.sidebar.multiselect("Select Country", sorted(data['country'].unique()))
    selected_sector = st.sidebar.multiselect("Select Sector", sorted(data['sector'].unique()))
    selected_subsector = st.sidebar.multiselect("Select Sub-sector", sorted(data['activity'].unique()))

    return start_date, end_date, selected_world_regions, selected_countries, selected_sector, selected_subsector

## calculate and display KPIs
def display_kpi(data):
    ## calculating metrics
    nr_country = f"{len(data['country'].unique())} countries"
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

def get_filtered_data(data):

    start_date, end_date, selected_world_regions, selected_countries, selected_sector, selected_subsector = display_filter(df)
    filtered_df = filtering(data, 'world_region', selected_world_regions)
    filtered_df = filtering(filtered_df, 'country', selected_countries)
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


def bar_loan_term(data, col):
    bin_edges = [0, 6, 12, 36, 60, 120]
    bin_labels = ['< 6M', '6M - 1Y', '1-3 Y', '3-5 Y', '5-10 Y']
    data['loan_term'] = pd.cut(data['term_in_months'], bins=bin_edges, labels=bin_labels, right=False)
    grouped = data.groupby('loan_term')['id'].count().reset_index()

    fig, ax = plt.subplots()
    ax.bar(grouped['loan_term'], grouped['id'], color='#219EBC')
    
    with col:
        col.header = "Number of Loans by Loan Term"
        col.write("Number of Loans by Loan Term")
        st.pyplot(fig)

def days_fully_funded(data, col):
    data['day_to_funded'] = (data['funded_time'] - data['disbursed_time']) / np.timedelta64(1, 'D')
    df_days = data[~((data['day_to_funded'].isna()) | (data['day_to_funded'] < 0))]

    fig, ax = plt.subplots()
    ax.hist(df_days['day_to_funded'], color='#219EBC', density=True, bins=int(df_days['day_to_funded'].max()-df_days['day_to_funded'].min()))
    
    with col:
        col.header = "Number of Loans by Days to Fully Funded"
        col.write("Number of Loans by Days to Fully Funded")
        st.pyplot(fig)

if __name__ == '__main__':
    st.title("Minh's Kiva Application")
    df, mpi = fetch_and_clean_data()
    filtered_df = get_filtered_data(df)
    display_kpi(filtered_df)

    col1, col2, col3 = st.columns(3)
    
    dist_loan_amount(filtered_df, col1)
    bar_loan_term(filtered_df, col2)
    days_fully_funded(filtered_df, col3)
    st.markdown(
        """
    <style>
    /* Change the font size and color of the metric label */
    label[data-testid="stMetricLabel"] .st-emotion-cache-jkfxgf p {
    word-break: break-word;
    margin-top: 2px;
    font-size: 20px;
    color: #219EBC;
    text-align: center;
    width: 100%;

    }
    /* Change the font size and color of the metric value */
    div[data-testid="stMetricValue"] {
        font-size: 30px;
        color: #FFFFFF;
        margin: 2px;
        text-align: center;
    }

    div[data-testid="stMetricLabel"] {
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    /* Align filter text to center */
    div[data-testid="stMarkdownContainer"] {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%; /* Ensure it takes full width */
    }

    /* Format the kpi mectric columns */
    div[data-testid="column"]{
        display: flex;
        align-items: center;
        justify-content: center;
    }
    /* change color kpi mectric columns */
    .st-emotion-cache-12w0qpk{
        background: #055A84;
        align-items: center;
        display: flex;
        width: 100%;
    }
    /* metric label center alignment */
    .st-emotion-cache-17c4ue {
        align-items: center;
        display: flex;
        width: 100%;
    }

    /* chart title format */
    .st-emotion-cache-1rsyhoq p {
        word-break: break-word;
        margin-top: 2px;
        font-size: 20px;
        color: #055A84;
        font-weight: bold;
    }

    /* Removing white space at the top of the app */
    .block-container {
                    padding-top: 2.5rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
    h1 {color:#F0F4F6; margin-top: 10px
    }
    h2 {color:#FFFFFF; font-size: 30px; margin-bottom: 10px
    }
    div[data-testid="stHeading"]{background:#023047; 
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

