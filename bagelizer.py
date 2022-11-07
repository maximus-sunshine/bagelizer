# bagelizer.py

# Bagelizer 9000 - the latest & greatest in bagel software technology.

# IMPORTS
from datetime import datetime
from datetime import date
import plotly.express as px
import streamlit as st
import nomad_tools as nomad

# set layout to fill screen
st.set_page_config(layout="wide")

# set paths for Streamlit hosted app
logo = './images/logo_nomad.png'

# start printing stuff to the page, starting with a logo
st.image(logo, width=100)

"""
# Bagelizer 9000
the latest & greatest in bagel software technology.
"""

# create tabs
tab1, tab2 = st.tabs(["Bagel Sales", "Bagel Labor"])

with tab1:
    # BAGEL SALES

    # allow user to upload a modifier sales report exported from Square
    modifier_sales_report = st.file_uploader("Export and upload a Modifier Sales report from Square")
    if modifier_sales_report is not None:
        # import & process modifier sales report - only care about "Bagel Flavor"
        df_mod = nomad.import_modifier_sales(modifier_sales_report)

        # create & display flavor and category summaries above full dataframe
        flavors, categories = nomad.create_summary(df_mod)

        # create columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.header("FLAVOR BREAKDOWN")

            # display flavor breakdown and total
            st.dataframe(flavors)
            st.write(flavors['Quantity'].sum())

            # pie chart from flavors
            fig = px.pie(flavors, values='Quantity', names='Flavor', title='Bagel Flavor Breakdown')
            fig.update_traces(textinfo='label+value+percent')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header("CATEGORY BREAKDOWN")

            # display category breakdown & total
            st.dataframe(categories)
            st.write(categories['Bagels'].sum())

        with col3:
            st.header('MODIFIER SALES DATA')
            st.dataframe(df_mod)

with tab2:
    # BAGEL LABOR

    # allow user to upload a modifier sales report exported from Square
    shifts_report = st.file_uploader("Export and upload a Shifts Report from Square")
    if shifts_report is not None:

        # # allow user to select date range
        # d = st.date_input(
        #     "Set date range below",
        #     value=[date(2019, 7, 6), date(2019, 7, 7)])

        # import and process shifts report and display the dataframe
        shifts = nomad.import_shifts(shifts_report)
        st.dataframe(shifts)

        # calculate total regular hours, overtime hours, and doubletime hours
        regular = shifts['Regular hours'].sum()
        overtime = shifts['Overtime hours'].sum()
        doubletime = shifts['Doubletime hours'].sum()
        st.write('Regular Hours:', regular, 'Overtime Hours:', overtime, 'Doubletime Hours:', doubletime)

        # calculate total labor cost
        total_labor_cost = nomad.total_labor_cost(shifts)
        st.write('Total Labor Cost ($):', total_labor_cost)