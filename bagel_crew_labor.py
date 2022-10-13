# bagel_crew_labor.py

# Analyze shift records for the bagel crew & calculate labor cost

# IMPORTS

import pandas as pd

# set paths
shift_record = 'shift_records/shifts-export_2022-08-14_2022-08-20.csv'

# read in data and modify some stuff
df = pd.read_csv(shift_record)
df.columns=df.columns.str.replace(' ', '_').str.lower()  # reset column names

dfbc = df[df.job_title == 'Bagel Crew']

print(df)