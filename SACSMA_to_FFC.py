"""
Prepare model outputs from SAC SMA to processing with the FFC
Noelle Patterson, UC Davis, 2021
"""
import glob
import pandas as pd
from datetime import datetime as dt

files = glob.glob('data_inputs/SAC_SMA_outputs/*')
for file in files:
    df = pd.read_table(file, sep=" ")
    year = df['Year']
    month = df['Month']
    day = df['Day']
    new_date_col = pd.Series(index=range(len(year)), name='date')
    for index, date in enumerate(day):
        date_string = str(day[index]) + '-' + str(month[index]) + '-' + str(year[index])
        dt_obj = dt.strptime(date_string, '%d-%m-%Y')
        dt_string = dt_obj.strftime('%m/%d/%Y')
        new_date_col[index] = dt_string
    flow = df['Flow_cfs']
    ffc_file = pd.concat([new_date_col, flow], axis=1)
    ffc_file = ffc_file.rename(columns={'date':'date', 'Flow_cfs':'flow'})
    # import pdb; pdb.set_trace()
    filename = file.split('/')[2][0:-4]
    ffc_file.to_csv('data_inputs/FFC_inputs/'+filename+'.csv', index=False)
    
