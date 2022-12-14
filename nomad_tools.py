# nomad_tools.py

# tools for Nomad stuff

# IMPORTS
import pandas as pd

# HELPER VARIABLES
dozen = 'Bagel Flavor 12'
half_dozen = 'Bagel Flavor 06'
four_pack = 'Bagel Flavor 04'
single = 'Bagel Flavor 01'


# FUNCTIONS
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


def create_summary(df_mod):
    # get bagel flavor sales data from df_mod
    ev = df_mod.loc[df_mod['Modifier'] == 'Everything', 'Qty Sold'].sum()
    pl = df_mod.loc[df_mod['Modifier'] == 'Plain', 'Qty Sold'].sum()
    ro = df_mod.loc[df_mod['Modifier'] == 'Rosemary Sea Salt', 'Qty Sold'].sum()
    se = df_mod.loc[df_mod['Modifier'] == 'Sesame', 'Qty Sold'].sum()
    za = df_mod.loc[df_mod['Modifier'] == "Za'atar", 'Qty Sold'].sum()

    # create flavors reports from modifier sales report - must call import_modifier_sales() first
    flavors = pd.DataFrame()
    flavors['Flavor'] = ['Everything', 'Plain', 'Rosemary Sea Salt', 'Sesame', "Za'atar"]
    flavors['Quantity'] = [ev, pl, ro, se, za]

    # get category sales data from df_mod
    sandos = df_mod.loc[df_mod['Modifier Set'] == 'Bagel Flavor - Sandwich', 'Qty Sold'].sum()
    dozens = df_mod.loc[df_mod['Modifier Set'] == dozen, 'Qty Sold'].sum()
    half_dozens = df_mod.loc[df_mod['Modifier Set'] == half_dozen, 'Qty Sold'].sum() - dozens
    four_packs = df_mod.loc[df_mod['Modifier Set'] == four_pack, 'Qty Sold'].sum() - dozens - half_dozens
    singles = df_mod.loc[df_mod['Modifier Set'] == single, 'Qty Sold'].sum() - dozens - half_dozens - four_packs

    categories = pd.DataFrame()
    categories['Category'] = ['Sandwich', 'Single Bagel', '4 Pack', '1/2 Dozen', 'Dozen']
    categories['Quantity'] = [sandos, singles, four_packs, half_dozens, dozens]
    categories['Bagels'] = [sandos, singles, four_packs * 4, half_dozens * 6, dozens * 12]

    return flavors, categories


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
    shifts['Total labor cost'] = shifts['Total labor cost'].str[1:]

    # create smaller dataframes for each job title
    admin = shifts[shifts['Job title'].str.contains('Admin', na=False)]
    am_bake = shifts[shifts['Job title'].str.contains('Morning Bake', na=False)]
    roll = shifts[shifts['Job title'].str.contains('Roll', na=False)]
    pm_bake = shifts[shifts['Job title'].str.contains('Evening Bake', na=False)]
    delivery = shifts[shifts['Job title'].str.contains('Delivery', na=False)]

    return shifts, admin, am_bake, roll, pm_bake, delivery


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
