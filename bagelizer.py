# bagelizer.py

# Bagelizer 9000 - the latest & greatest in bagel software technology.

# IMPORTS
from datetime import datetime
from datetime import date
import plotly.express as px
import streamlit as st
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

# BAGEL LABOR
with tab2:
    # allow user to upload a modifier sales report exported from Square
    shifts_report = st.file_uploader("Export and upload a Shifts Report from Square")
    if shifts_report is not None:
        # # allow user to select date range
        # d = st.date_input(
        #     "Set date range below",
        #     value=[date(2019, 7, 6), date(2019, 7, 7)])

        # create columns
        col1, col2 = st.columns([3, 1])

        with col1:
            # import and process shifts report and display the dataframe
            st.header("BAGEL CREW SHIFTS")
            shifts, admin, am_bake, roll, pm_bake, delivery = nomad.import_shifts(shifts_report)
            shifts_summary(shifts)

        with col2:
            # admin_labor = nomad.total_labor_cost(admin)
            # am_bake_labor = nomad.total_labor_cost(am_bake)
            # roll_labor = nomad.total_labor_cost(roll)
            # pm_bake_labor = nomad.total_labor_cost(pm_bake)
            # delivery_labor = nomad.total_labor_cost(delivery)
            # values = [admin_labor, am_bake_labor, roll_labor, pm_bake_labor]

            fig = px.pie(shifts, values='Total paid hours', names='Job title', title='BREAKDOWN BY HOURS')
            # fig.update_traces(textinfo='label+value+percent')
            st.plotly_chart(fig, use_container_width=True)

        # show breakdown by shift type
        st.header("BREAKDOWN BY SHIFT TYPE")

        st.subheader("ADMIN")
        shifts_summary(admin)

        st.subheader("MORNING BAKE")
        shifts_summary(am_bake)

        st.subheader("ROLL")
        shifts_summary(roll)

        st.subheader("EVENING BAKE")
        shifts_summary(pm_bake)

        st.subheader("DELIVERY")
        shifts_summary(delivery)
