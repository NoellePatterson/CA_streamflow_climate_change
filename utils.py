import glob
import pandas as pd
import numpy as np

'''
Functions for data processing and management associated with analysis and figure generation for the 
Patterson et al. 2021 publication
'''

def import_ffc_data(model_folder, analysis_type):
    if analysis_type == 'ca_regional':
        data_index = 3
    elif analysis_type == 'merced':
        data_index = 2
    # import pdb; pdb.set_trace()
    model_name = model_folder.split('/')[data_index] # the index changes depending on data source. 2 for Merced data, 3 for CA regional data
    if analysis_type == 'ca_regional':
        main_metric_files = sorted(glob.glob('data_inputs/FFC_results/CA_regional_sites/'+model_name+'/*flow_result.csv')) # for regional data
        supp_metric_files = sorted(glob.glob('data_inputs/FFC_results/CA_regional_sites/'+model_name +'/*supplementary_metrics.csv')) # for regional data
    elif analysis_type == 'merced':
        main_metric_files = sorted(glob.glob('data_inputs/FFC_results/'+model_name+'/*flow_result.csv')) # for merced models
        supp_metric_files = sorted(glob.glob('data_inputs/FFC_results/'+model_name +'/*supplementary_metrics.csv')) # for merced models
    ffc_dicts = []
    supp_dicts = []
    for supp_file in supp_metric_files:
        supp_dict = {}
        supp_dict['gage_id'] = supp_file.split('/')[data_index+1][:-26] # index changes depending on data source. 3 for Merced, 4 for CA regions
        supp_dict['supp_metrics'] = pd.read_csv(supp_file, sep=',', index_col=0)
        supp_dicts.append(supp_dict)
    for metric_file in main_metric_files:
        main_metrics = pd.read_csv(metric_file, sep=',', index_col=0)
        # create dictionary for each gage named after gage id, with class and metric results inside 
        gage_dict = {}
        gage_dict['gage_id'] = metric_file.split('/')[data_index+1][:-23] # index changes depending on data source. 3 for Merced, 4 for CA regions
        # align supplemental metric file with main metric file, and add info to the main gage dict
        for supp_dict in supp_dicts:
            if supp_dict['gage_id'] == gage_dict['gage_id']:
                # add supp_dict metrics to gage_dict metrics
                gage_dict['ffc_metrics'] = pd.concat([main_metrics, supp_dict['supp_metrics']], axis=0)
        ffc_dicts.append(gage_dict)
    return ffc_dicts, model_name

def import_drh_data(model_folder, analysis_type):
    if analysis_type == 'ca_regional':
        data_index = 3
    elif analysis_type == 'merced':
        data_index = 2
    model_name = model_folder.split('/')[data_index] # the index changes depending on data source. 2 for Merced data, 3 for CA regional data
    if analysis_type == 'ca_regional':
        drh_files = glob.glob('data_inputs/FFC_results/CA_regional_sites/'+model_name+'/*drh.csv') # for CA regional sites
        rh_files = glob.glob('data_inputs/FFC_results/CA_regional_sites/'+model_name+'/*matrix.csv') # for CA Regional sites
    elif analysis_type == 'merced':
        drh_files = glob.glob('data_inputs/FFC_results/'+model_name+'/*drh.csv') # for Merced data
        rh_files = glob.glob('data_inputs/FFC_results/'+model_name+'/*matrix.csv') # for Merced sites
    drh_dicts = []
    for index, drh_file in enumerate(drh_files):
        drh_dict = {}
        drh_dict['name'] = drh_file.split('/')[data_index+1][:-8] # index changes depending on data source. 3 for Merced, 4 for CA regions
        drh_dict['data'] = pd.read_csv(drh_file, sep=',', index_col=0, header=None)
        drh_dicts.append(drh_dict)

    rh_dicts = []
    for index, rh_file in enumerate(rh_files):
        rh_dict = {} 
        rh_dict['name'] = rh_file.split('/')[data_index+1][:-23] # index changes depending on data source. 3 for Merced, 4 for CA regions
        rh_dict['data'] = pd.read_csv(rh_file, sep=',', index_col=None)
        rh_dicts.append(rh_dict)
        
    return drh_dicts, rh_dicts, model_name

def make_results_dicts(ffc_data):
    all_results = []
    metrics_list = ffc_data[0]['ffc_metrics'].index
    for index, gage_dict in enumerate(ffc_data):
        current_gage = {}
        results = pd.DataFrame(index=metrics_list)
        current_gage['gage_id'] = gage_dict['gage_id']
        # current_gage['class'] = gage_dict['class'] # use with FFC reference data, which has class
        current_gage['results'] = results
        all_results.append(current_gage)
    return all_results

def summarize_data(results_dicts):
    classes = [[] for i in range(9)]
    for gage_dict in results_dicts:
        for i in range(1,10):
            if gage_dict['class'] == i:
                # have to align indexing of classes starting at 1 with Python's default 0-indexing
                classes[i-1].append(gage_dict)
    metrics = results_dicts[0]['results'].index
    summary_df = pd.DataFrame(index=metrics)
    # look in each class for that metric
    for index in range(1,10):
        current_class = classes[index-1]
        summary_df['class_{}_down'.format(index)] = np.nan
        summary_df['class_{}_no_trend'.format(index)] = np.nan
        summary_df['class_{}_up'.format(index)] = np.nan
        for metric in metrics: 
            down_trends = 0
            no_trends = 0
            up_trends = 0
            for gage in current_class:
                mk_decision = gage['results'].loc[metric,'mk_decision']
                if mk_decision == 'decreasing':
                    down_trends += 1
                elif mk_decision == 'no trend':
                    no_trends += 1
                elif mk_decision == 'increasing':
                    up_trends += 1
            summary_df.loc[metric, 'class_{}_down'.format(index)] = down_trends
            summary_df.loc[metric, 'class_{}_no_trend'.format(index)] = no_trends
            summary_df.loc[metric, 'class_{}_up'.format(index)] = up_trends
    summary_df.to_csv('data_outputs/mk_summary.csv')

def summarize_data_no_classes(results_dicts):
    import pdb; pdb.set_trace()
    metrics = results_dicts[0]['results'].index
    summary_df = pd.DataFrame(index=metrics)
    summary_df['Down'] = np.nan
    summary_df['No_trend'] = np.nan
    summary_df['Up'] = np.nan
    for metric in metrics: 
        down_trends = 0
        no_trends = 0
        up_trends = 0
        for gage in results_dicts:
            mk_decision = gage['results'].loc[metric,'mk_decision']
            if mk_decision == 'decreasing':
                down_trends += 1
            elif mk_decision == 'no trend':
                no_trends += 1
            elif mk_decision == 'increasing':
                up_trends += 1
        summary_df.loc[metric, 'Down'] = down_trends
        summary_df.loc[metric, 'No_trend'] = no_trends
        summary_df.loc[metric, 'Up'] = up_trends
    summary_df.to_csv('data_outputs/mk_summary_dwr.csv')

def create_model_tables(ffc_data):
    # perform calculations separately for rcp 4.5 and rcp 8.5
    models_45 = []
    models_85 = []
    for model in ffc_data:
        if '85' in model['model_name']:
            models_85.append(model)
        elif '45' in model['model_name']:
            models_45.append(model)

    def create_table(rcp_models, rcp_id):
        # create list of unique sites in ffc_data list (18 total)
        sites_list = []
        for model in rcp_models:
            if model['gage_id'] in sites_list:
                continue
            else:
                sites_list.append(model['gage_id'])
        # append all models in rcp_models to respective sites list, after calculating fut-hist difference. 
        metrics_list = rcp_models[0]['ffc_metrics'].index
        all_site_models = {}
        for site in sites_list:
            all_site_models[site] = {}
            all_site_models[site]['hist'] = []
            all_site_models[site]['fut'] = []
            for model in rcp_models:
                if model['gage_id'] == site:
                    metrics = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
                    metrics_hist = metrics.iloc[:,0:65].mean(axis=1) # years 1950-2015
                    metrics_fut = metrics.iloc[:,85:150].mean(axis=1) # years 2035-2100
                    all_site_models[site]['hist'].append(metrics_hist)
                    all_site_models[site]['fut'].append(metrics_fut)
        # take all historic and future metrics from each site and average them together. 
        # for flow-based metrics, compute percent change instead of simple difference
        for site in all_site_models:
            np_array_hist = np.array(all_site_models[site]['hist'])
            hist_avg = np.nanmean(np_array_hist, axis=0)
            np_array_fut = np.array(all_site_models[site]['fut'])
            fut_avg = np.nanmean(np_array_fut, axis=0)
            result_list = np.zeros([28,])
            flow_mag_indices = [0, 3, 4, 7, 8, 9, 16, 20, 21, 24]
            for index, value in enumerate(hist_avg):
                if index in flow_mag_indices:
                    result_list[index] = (fut_avg[index] - hist_avg[index])/hist_avg[index] * 100
                else:
                    result_list[index] = fut_avg[index] - hist_avg[index]
            all_site_models[site] = result_list
        
        # print results in dict into table, save to csv
        output = pd.DataFrame(all_site_models, index = metrics_list)
        output.to_csv('data_outputs/CA_regions_fut_hist_differences_'+rcp_id+'.csv')
    output = create_table(models_45, 'rcp4.5')
    output = create_table(models_85, 'rcp8.5')

    return output

def combine_mk_model_stats():
    files = glob.glob('data_outputs/MK_outputs_all_models/*')
    mk_files_45 = []
    mk_files_85 = []
    for file in files:
        stats = pd.read_csv(file)
        stats = stats.set_index('Year')
        if '45' in file:
            mk_files_45.append(stats)
        elif '85' in file:
            mk_files_85.append(stats)
    # create final output table to compile all results
    metrics = stats.index
    locations = stats.columns
    mk_output_45 = pd.DataFrame(0, index=metrics, columns=locations)
    mk_output_85 = pd.DataFrame(0, index=metrics, columns=locations)
    # loop through each file, convert character values to numbers 
    for mk_file in mk_files_45:
        mk_file = mk_file.replace('decreasing', -1)
        mk_file = mk_file.replace('no trend', 0)
        mk_file = mk_file.replace('increasing', 1)
        mk_output_45 = mk_output_45.add(mk_file)
    for mk_file in mk_files_85:
        mk_file = mk_file.replace('decreasing', -1)
        mk_file = mk_file.replace('no trend', 0)
        mk_file = mk_file.replace('increasing', 1)
        mk_output_85 = mk_output_85.add(mk_file)
        # import pdb; pdb.set_trace()
    mk_output_45.to_csv('data_outputs/All_MK_results_RCP4.5.csv')
    mk_output_85.to_csv('data_outputs/All_MK_results_RCP8.5.csv')
    # matrix addition until all dfs added up
    return()

def gini_index_mk_trends():
    files = glob.glob('data_outputs/MK_outputs_all_models/*')
    mk_files_45 = []
    mk_files_85 = []
    for file in files:
        stats = pd.read_csv(file)
        stats = stats.set_index('Year')
        temp_dict = {}
        if '45' in file:
            temp_dict['model_name'] = file.split('/')[2][:-4]
            temp_dict['data'] = stats
            mk_files_45.append(temp_dict)
        elif '85' in file:
            temp_dict['model_name'] = file.split('/')[2][:-4]
            temp_dict['data'] = stats
            mk_files_85.append(temp_dict)
    metrics = mk_files_85[0]['data'].index # can switch between _85 and _45
    all_dfs = pd.DataFrame(index=metrics)
    for mk_file in mk_files_45:
        name = mk_file['model_name'][11:]
        df = pd.DataFrame(0, index=metrics, columns=['gini_index'])
        for metric in metrics:
            inc = 0 
            dec = 0 
            same = 0
            for trend in mk_file['data'].loc[metric]:
                if trend == 'increasing':
                    inc += 1
                elif trend == 'decreasing':
                    dec += 1
                elif trend == 'no trend':
                    same += 1
            tot = inc + dec + same
            gini = 1 - ((inc/tot)**2 + (dec/tot)**2 + (same/tot)**2)
            gini_perc = 100*(1 - gini/(2/3))
            df.loc[metric] = gini_perc
        all_dfs[name] = df
    all_dfs.to_csv('data_outputs/Gini_trends_RCP8.5.csv') # specify 8.5 or 4.5 in filename
