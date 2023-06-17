# nomad_tools.py

# tools for Nomad stuff

# IMPORTS
import pandas as pd
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
import streamlit as st

# HELPER VARIABLES
dozen = 'Bagel Flavor 12'
half_dozen = 'Bagel Flavor 06'
four_pack = 'Bagel Flavor 04'
single = 'Bagel Flavor 01'


# FUNCTIONS
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns
    Args:
        df (pd.DataFrame): Original dataframe
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
                df[col].dt.strftime('%Y-%m-%d')
            except Exception:
                pass

        # if is_datetime64_any_dtype(df[col]):
        #     df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 100:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df


def import_modifier_sales(csv):
    # create dataframe for Modifier Sales exported from Square
    df_mod = pd.read_csv(csv)

    # drop non "Bagel Flavor" mods
    df_mod = df_mod[df_mod['Modifier Set'].str.contains('Bagel Flavor')]

    # sort dataframe
    df_mod.sort_values(['Modifier Set', 'Modifier'], inplace=True, ignore_index=True)

    # drop unwanted columns
    df_mod.drop(columns=['Net Sales',
                         'Gross Sales',
                         'Qty Refunded',
                         'Refunds'], inplace=True)

    return df_mod


def import_shifts(csv):
    # create dataframe for Shifts Report exported from Square
    shifts = pd.read_csv(csv)

    # drop non bagel shifts
    shifts = shifts[shifts['Job title'].str.contains('Bagel', na=False)]

    # drop unwanted columns
    shifts.drop(columns=['Doubletime labor cost', 'Overtime labor cost', 'Regular labor cost',
                         'Unpaid break', 'Break end time', 'Break end date',
                         'Break start time', 'Break start date', 'Clockout date', 'Location', 'Employee number',
                         'Transaction tips', 'Declared cash tips'], inplace=True)

    # format clockin dates
    shifts['Clockin date'] = pd.to_datetime(shifts['Clockin date'])
    shifts['Clockin date'] = shifts['Clockin date'].dt.strftime('%Y-%m-%d')

    # add day of week column
    shifts.insert(3, 'Day', pd.to_datetime(shifts['Clockin date']).dt.day_name())

    # format clockin times
    shifts['Clockin time'] = pd.to_datetime(shifts['Clockin time'])
    shifts['Clockin time'] = shifts['Clockin time'].dt.strftime('%X')

    # sort by clockin date then clockin time
    shifts = shifts.sort_values(['Clockin date', 'Clockin time'], ignore_index=True)

    # drop $ sign in total labor cost column
    shifts['Total labor cost'] = shifts['Total labor cost'].str.replace('$', '').str.replace(',', '')

    # create smaller dataframes for each job title
    admin = shifts[shifts['Job title'].str.contains('Admin', na=False)]
    am_bake = shifts[shifts['Job title'].str.contains('Morning Bake', na=False)]
    roll = shifts[shifts['Job title'].str.contains('Roll', na=False)]
    pm_bake = shifts[shifts['Job title'].str.contains('Evening Bake', na=False)]
    delivery = shifts[shifts['Job title'].str.contains('Delivery', na=False)]

    return shifts, admin, am_bake, roll, pm_bake, delivery


def create_summary(df_mod):
    # get bagel flavor sales data from df_mod
    ev = df_mod.loc[df_mod['Modifier'] == 'Everything', 'Qty Sold'].sum()
    pl = df_mod.loc[df_mod['Modifier'] == 'Plain', 'Qty Sold'].sum()
    se = df_mod.loc[df_mod['Modifier'] == 'Sesame', 'Qty Sold'].sum()
    za = df_mod.loc[df_mod['Modifier'] == "Za'atar", 'Qty Sold'].sum()
    ro = df_mod.loc[df_mod['Modifier'] == 'Rosemary Sea Salt', 'Qty Sold'].sum()
    ja = df_mod[df_mod['Modifier'].str.contains("Jalapeño")]['Qty Sold'].sum()
    bl = df_mod.loc[df_mod['Modifier'] == "Blueberry", 'Qty Sold'].sum()

    # create flavors reports from modifier sales report - must call import_modifier_sales() first
    flavors = pd.DataFrame()
    flavors['Flavor'] = ['Everything', 'Plain', 'Sesame', "Za'atar", 'Rosemary Sea Salt', "Jalapeño", "Blueberry"]
    flavors['Quantity'] = [ev, pl, se, za, ro, ja, bl]

    # get category sales data from df_mod
    sandos = df_mod.loc[df_mod['Modifier Set'] == 'Bagel Flavor - Sandwich', 'Qty Sold'].sum()
    dozens = df_mod.loc[df_mod['Modifier Set'] == dozen, 'Qty Sold'].sum()
    half_dozens = df_mod.loc[df_mod['Modifier Set'] == half_dozen, 'Qty Sold'].sum() - dozens
    four_packs = df_mod.loc[df_mod['Modifier Set'] == four_pack, 'Qty Sold'].sum() - dozens - half_dozens
    singles = df_mod.loc[df_mod['Modifier Set'] == single, 'Qty Sold'].sum() - dozens - half_dozens - four_packs

    categories = pd.DataFrame()
    categories['Category'] = ['Sandwich', 'Single Bagel', '4 Pack', '1/2 Dozen', 'Dozen']
    categories['Price ($)'] = [1, 2, 6, 9, 18]
    categories['Quantity'] = [sandos, singles, four_packs, half_dozens, dozens]
    categories['Bagels'] = [sandos, singles, four_packs * 4, half_dozens * 6, dozens * 12]
    categories['Sales ($)'] = categories['Quantity'] * categories['Price ($)']

    return flavors, categories


def count_money(series):
    # takes a pandas Series of currency values in $USD as an argument and returns the sum

    # drop $ sign so we can sum
    series = series.str[1:]

    # sum
    total = series.astype(float).sum()

    return total


def total_labor_cost(shifts):
    # calculates total labor cost from a shifts report

    # get the total labor cost
    total_labor_cost = shifts['Total labor cost'].astype(float).sum()

    return total_labor_cost


def shifts_summary(shifts):
    # takes a "shifts" or "shifts"-like dataframe and returns total regular hours, OT hours, DT hours, and total
    # labor cost
    regular = shifts['Regular hours'].sum()
    overtime = shifts['Overtime hours'].sum()
    doubletime = shifts['Doubletime hours'].sum()
    labor_cost = total_labor_cost(shifts)

    return regular, overtime, doubletime, labor_cost


# def get_date_range(df_mod):
#     # get date range from df_mod

def import_sales_data(date_range):
    # create dataframes for item sales, category sales, and modifier sales.
    df_item = pd.read_csv(
        './item_sales/items-' + date_range + '.csv')
    df_cat = pd.read_csv(
        './category_sales/category-sales-' + date_range + '.csv')
    df_mod = pd.read_csv(
        './modifier_sales/modifier-sales-' + date_range + '.csv')

    # sort dataframes
    df_item.sort_values(['Location', 'Category', 'Item'], inplace=True, ignore_index=True)
    df_mod.sort_values(['Modifier Set', 'Modifier'], inplace=True, ignore_index=True)
    df_cat.sort_values(['Category'], inplace=True, ignore_index=True)

    return df_item, df_cat, df_mod
