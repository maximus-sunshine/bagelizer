# bagelizer.py

# Bagelizer 9000 - the latest & greatest in bagel software technology.

# IMPORTS
from datetime import datetime
from datetime import date
import plotly.express as px
import streamlit as st
from streamlit_extras.dataframe_explorer import dataframe_explorer
import pandas as pd
import nomad_tools as nomad


# FUNCTIONS
def shifts_summary(shifts):
    # takes a "shifts" or "shifts"-like data frame and displays it with some stats
    st.dataframe(shifts)

    regular = shifts['Regular hours'].sum()
    overtime = shifts['Overtime hours'].sum()
    doubletime = shifts['Doubletime hours'].sum()
    labor_cost = nomad.total_labor_cost(shifts)

    st.write('Regular Hours:', regular, 'Overtime Hours:', overtime, 'Doubletime Hours:', doubletime)
    st.write('Total Labor Cost ($):', labor_cost)

    return


# VARIABLES/PATHS
logo = './images/logo_nomad.png'

# START OF SCRIPT
# set layout to fill screen
st.set_page_config(layout="wide")

# start printing stuff to the page, starting with a logo
st.image(logo, width=100)

"""
# Bagelizer 9000
the latest & greatest in bagel software technology.
"""

# create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Bagel Sales", "Bagel Labor", "All Sales", "All Labor"])

# BAGEL SALES
with tab1:
    # allow user to upload a modifier sales report exported from Square
    modifier_sales_report = st.file_uploader("Export and upload a Modifier Sales report from Square")
    if modifier_sales_report is not None:
        # import & process modifier sales report - only care about "Bagel Flavor"
        df_mod = nomad.import_modifier_sales(modifier_sales_report)

        # create & display flavor and category summaries above full dataframe
        flavors, categories = nomad.create_summary(df_mod)

        # create columns
        col_a1, col_a2, col3 = st.columns(3)

        with col_a1:
            st.header("FLAVOR BREAKDOWN")

            # display flavor breakdown and total
            st.dataframe(flavors)
            st.write('Total Bagels: ', flavors['Quantity'].sum())

            # pie chart from flavors
            fig = px.pie(flavors, values='Quantity', names='Flavor', title='Bagel Flavor Breakdown')
            fig.update_traces(textinfo='label+value+percent')
            st.plotly_chart(fig, use_container_width=True)

        with col_a2:
            st.header("CATEGORY BREAKDOWN")

            # display category breakdown & total
            st.dataframe(categories)
            st.write('Total Bagels: ', categories['Bagels'].sum(), '   Total Bagel Sales ($): ', categories['Sales ($)'].sum())


        with col3:
            st.header('MODIFIER SALES DATA')
            st.dataframe(df_mod)

# BAGEL LABOR
with tab2:
    # allow user to upload a shifts report exported from Square
    shifts_report = st.file_uploader("Export and upload a Shifts Report from Square")
    if shifts_report is not None:
        # import and process shifts report
        shifts, admin, am_bake, roll, pm_bake, delivery = nomad.import_shifts(shifts_report)

        # format clockin dates
        shifts['Clockin date'] = pd.to_datetime(shifts['Clockin date'])

        # allow user to select date range
        d = st.date_input(
            "Set date range below",
            value=[shifts['Clockin date'].min(), shifts['Clockin date'].max()])

        # filter the dataframe by date and format it as a string
        shifts = shifts[shifts['Clockin date'] >= pd.to_datetime(d[0])]
        shifts = shifts[shifts['Clockin date'] <= pd.to_datetime(d[1])]
        shifts['Clockin date'] = shifts['Clockin date'].dt.strftime('%Y-%m-%d')

        # create columns
        col_a1, col_a2 = st.columns([3, 1])

        with col_a1:
            # display the dataframe
            st.header("BAGEL CREW SHIFTS")
            shifts_summary(shifts)

        with col_a2:
            """
            #### FRESHLY BAKED PIE CHART
            """
            names = st.selectbox(
                'What kind of pie do you want?',
                ['Job title', 'First name', 'Day'])

            values = st.selectbox(
                'How do you want it sliced?',
                ['Total paid hours', 'Total labor cost'])

            fig = px.pie(shifts, values=values, names=names)
            fig.update_layout(legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            ))
            st.plotly_chart(fig, use_container_width=True)

        # show breakdown by shift type
        st.header("BREAKDOWN BY SHIFT TYPE")

        st.subheader("ADMIN")
        shifts_summary(admin)

        st.subheader("MORNING BAKE")
        shifts_summary(am_bake)

        st.subheader("ROLL")
        shifts_summary(roll)

# ALL SALES
with tab3:
    # allow user to upload a modifier sales report exported from Square
    data = st.file_uploader("Export and upload an Item Sales report from Square")
    if data is not None:

        # read in data & drop the $ in Net Sales column
        df = pd.read_csv(data)
        df['Net Sales'] = df['Net Sales'].str.replace('$', '').str.replace(',', '')

        # format clockin dates
        df['Date'] = pd.to_datetime(df['Date'])

        # allow user to select date range
        d = st.date_input(
            "Set date range below:",
            value=[df['Date'].min(), df['Date'].max()])

        # filter the dataframe by date and format it as a string
        df = df[df['Date'] >= pd.to_datetime(d[0])]
        df = df[df['Date'] <= pd.to_datetime(d[1])]
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        # write some stats
        st.write('Net Sales ($): ', df['Net Sales'].astype(float).sum())
        # st.write('Net Sales ($): ', df['Net Sales'].sum())

        # display a pie chart
        names = st.selectbox(
            'What kind of pie do you want?',
            ['Category', 'Item', 'Location'])

        fig = px.pie(df, values='Net Sales', names=names)
        fig.update_layout(legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ))
        st.plotly_chart(fig, use_container_width=True)

        # display the data
        st.dataframe(df)

# ALL LABOR
with tab4:
    # allow user to upload a shifts report exported from Square
    overall_shifts_report = st.file_uploader("Export and upload a Shifts Report from Square:")
    if overall_shifts_report is not None:
        # allow user to select date range
        d = st.date_input(
            "Set date range below",
            value=[date(2019, 7, 6), date(2019, 7, 7)])