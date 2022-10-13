# bagel_sales.py

# analyze Nomad bagel sales data

# IMPORTS
import nomad_tools as nomad

# SCRIPT
date_range = '2022-10-06-2022-10-08'  # specify date range - must match file names exactly

# create dataframes for item sales, category sales, and modifier sales.
df_item, df_cat, df_mod = nomad.import_sales_data(date_range)

# create dataframe for all Bagel Flavor modifiers, as well as for individual flavors
df_bagels = df_mod[df_mod['Modifier Set'].str.contains('Bagel Flavor')]
df_everything = df_bagels[df_bagels['Modifier'] == 'Everything']
df_plain = df_bagels[df_bagels['Modifier'] == 'Plain']
df_rose = df_bagels[df_bagels['Modifier'] == 'Rosemary Sea Salt']
df_sesame = df_bagels[df_bagels['Modifier'] == 'Sesame']
df_zaatar = df_bagels[df_bagels['Modifier'] == "Za'atar"]

# calculate totals
tot_bagels = df_bagels['Net Qty Sold'].sum()
tot_everything = df_everything['Net Qty Sold'].sum()
tot_plain = df_plain['Net Qty Sold'].sum()
tot_rose = df_rose['Net Qty Sold'].sum()
tot_sesame = df_sesame['Net Qty Sold'].sum()
tot_zaatar = df_zaatar['Net Qty Sold'].sum()

print(tot_bagels)
