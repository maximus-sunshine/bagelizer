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
import re

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
tab1, tab2, tab3 = st.tabs(["Sales & Labor Report", "Bagel Sales", "Bagel Labor"])

# SALES & LABOR REPORT
with tab1:
    # allow user to upload a category sales report exported from Square
    cat_sales = st.file_uploader("Export and upload an Category Sales report from Square")
    if cat_sales is not None:

        # read in data
        df = pd.read_csv(cat_sales)

        # add a column for "Area"
        df.insert(0, 'Area', '')  # Inserting a column titled 'Area' at index 0 with empty values

        # Create a dictionary mapping categories to areas
        category_area_mapping = {
            'Beer': 'Beverages',
            'Bottled & Canned Drinks': 'Beverages',
            'Day Tripper': 'Beverages',
            'Mimosas, Rose': 'Beverages',
            'Not-Coffee': 'Beverages',
            'Coffee': 'Coffee',
            "B'Fast Sandwiches": 'Day Kitchen',
            "B'Rad Sandwiches": 'Day Kitchen',
            'Catering & Events': 'Day Kitchen',
            'Daily Specials': 'Day Kitchen',
            'Extras': 'Day Kitchen',
            'Side Sauce': 'Day Kitchen',
            'Sidekicks': 'Day Kitchen',
            'Sides': 'Day Kitchen',
            'Spreads To Go': 'Day Kitchen',
            'Bakery': 'Donut',
            'Basic Donuts': 'Donut',
            'Donut Holes': 'Donut',
            'Dozen Donuts': 'Donut',
            'Specialty Donuts': 'Donut',
            'Uncategorized': 'Misc',
            'Locally Made': 'Misc',
            'Merch': 'Misc',
            'Bagels To Go': 'Wholesale',
            'Wholesale': 'Wholesale'
        }

        # Populate the 'Area' column based on the 'Category' column (exact match with ignoring extra spaces) - hard
        # coding sandwiches because the apostrophe is messing things up
        for category, area in category_area_mapping.items():
            df.loc[df['Category'].str.strip() == category, 'Area'] = area
            df.loc[df['Category'].str.contains('Sandwich', case=False, na=False), 'Area'] = 'Day Kitchen'

        # sort alphabetically by Area
        df = df.sort_values(['Area', 'Category'], ascending=True)

        # display the data
        st.dataframe(df)

        # Remove '$' and ',' from 'Net Sales' values and convert to numeric
        df['Net Sales'] = df['Net Sales'].str.replace('[\$,]', '', regex=True).astype(float)

        # Calculate the total Net Sales (without dollar signs and commas) for each area
        area_net_sales = df.groupby('Area')['Net Sales'].sum()

        # Calculate the total Net Sales across all areas
        total_net_sales = area_net_sales.sum()

        # Print the summary of Net Sales by Area
        st.write('Summary:')
        for area, net_sales in area_net_sales.items():
            st.write(f'{area}: ${net_sales:,.2f}')

        # Add a line for the total Net Sales across all areas
        st.write(f'Total Net Sales: ${total_net_sales:,.2f}')

# BAGEL SALES
with tab2:
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
with tab3:
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

# # DONUT SALES
# with tab3:
#     # allow user to upload a modifier sales report exported from Square
#     data = st.file_uploader("Export and upload an Item Sales report from Square")
#     if data is not None:
#
#         # read in data & drop the $ in Net Sales column
#         df = pd.read_csv(data)
#         df['Net Sales'] = df['Net Sales'].str.replace('$', '').str.replace(',', '')
#
#         # format clockin dates
#         df['Date'] = pd.to_datetime(df['Date'])
#
#         # allow user to select date range
#         d = st.date_input(
#             "Set date range below:",
#             value=[df['Date'].min(), df['Date'].max()])
#
#         # filter the dataframe by date and format it as a string
#         df = df[df['Date'] >= pd.to_datetime(d[0])]
#         df = df[df['Date'] <= pd.to_datetime(d[1])]
#         df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
#
#         # write some stats
#         st.write('Net Sales ($): ', df['Net Sales'].astype(float).sum())
#         # st.write('Net Sales ($): ', df['Net Sales'].sum())
#
#         # display a pie chart
#         names = st.selectbox(
#             'What kind of pie do you want?',
#             ['Category', 'Item', 'Location'])
#
#         values = st.selectbox(
#             'How do you want it sliced?',
#             ['Net Sales', 'Qty'])
#
#         fig = px.pie(df, values=values, names=names)
#         fig.update_layout(legend=dict(
#             yanchor="top",
#             y=0.99,
#             xanchor="left",
#             x=0.01
#         ))
#         st.plotly_chart(fig, use_container_width=True)
#
#         # display the data
#         st.dataframe(df)