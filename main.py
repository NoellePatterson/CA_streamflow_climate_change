import glob
import pandas as pd
import numpy as np
from utils import import_ffc_data, import_drh_data, make_results_dicts,  \
 create_model_tables, combine_mk_model_stats, gini_index_mk_trends
from trends import calc_mk_trend
from plotting import site_hydrograph, merced_models_hydrograph, plot_mk_bars_gini
from eco_endpoints import eco_endpoints

'''
Main run file for data processing and visualization associated with the Patterson et al. 2021 publication
'''

# choose data to process: either 18 western Sierras sites (ca_regional) or Merced River decision scaling
# data (merced)
analysis_type = 'ca_regional'
# analysis_type = 'merced'

if analysis_type == 'merced':
    model_folders = glob.glob('data_inputs/FFC_results/Merced_models_June2021')
elif analysis_type == 'ca_regional':
    model_folders = glob.glob('data_inputs/FFC_results/CA_regional_sites/*')
ffc_data_all = []
rh_data_all = []
for folder in model_folders:
    # run with FFC outputs (copy and paste from FFC) to combine results files and convert to useable format. Use natural flow class #3-for regional sites
    ffc_data_model = []
    ffc_data, model_name = import_ffc_data(folder, analysis_type)
    for data in ffc_data:
        data['model_name'] = model_name
        ffc_data_all.append(data)
        if analysis_type == 'ca_regional':
            ffc_data_model.append(data) # use this one for running MK trends, where you need all sites from one model together
    drh_data, rh_data, model_name = import_drh_data(folder, analysis_type)
    for data in rh_data:
        data['model_name'] = model_name
        rh_data_all.append(data)
    if analysis_type == 'ca_regional':
        results_dicts = make_results_dicts(ffc_data)
        mk_trend = calc_mk_trend(ffc_data_model, results_dicts, model_name) 
if analysis_type == 'ca_regional':
    plots = site_hydrograph(ffc_data_all, rh_data_all)
    processing = combine_mk_model_stats()
    barplots = plot_mk_bars_gini()
    result = create_model_tables(ffc_data_all)
if analysis_type == 'merced':
    eco_endpoints = eco_endpoints(ffc_data_all, rh_data_all)
    plots = merced_models_hydrograph(ffc_data_all, rh_data_all)


