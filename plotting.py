import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12.5})

'''
Produce figures associated with Patterson et al. 2021 publication: hydrographs and metric overlaysfor three sites in the CA 
western sierras, and a bar chart representing a trend analysis for functional flow metrics across all 18 sites
'''

def merced_models_hydrograph(ffc_data, rh_data):
    # Dry yr=2008, avg yr=1979, wet yr=1998

    year = '1979'
    ctrl = {}
    oat_t = {}
    oat_pwet = {}
    oat_pdry = {}
    oat_s = {}
    oat_e = {}
    oat_i = {}
    for model_index, model in enumerate(rh_data):
        if model['name'] == 'SACSMA_CTR_T0P0S0E0I0':
            data = model['data'].apply(pd.to_numeric, errors='coerce')
            ctrl['rh'] = data
        elif model['name'] == 'SACSMA_OATT_T5P0S0E0I0':
            data = model['data'].apply(pd.to_numeric, errors='coerce')
            oat_t['rh'] = data
        elif model['name'] == 'SACSMA_OATP_T0P30S0E0I0':
            data = model['data'].apply(pd.to_numeric, errors='coerce')
            oat_pwet['rh'] = data
        elif model['name'] == 'SACSMA_OATP_T0P-30S0E0I0':
            data = model['data'].apply(pd.to_numeric, errors='coerce')
            oat_pdry['rh'] = data
        elif model['name'] == 'SACSMA_OATS_T0P0S5E0I0':
            data = model['data'].apply(pd.to_numeric, errors='coerce')
            oat_s['rh'] = data
        elif model['name'] == 'SACSMA_OATE_T0P0S0E5I0':
            data = model['data'].apply(pd.to_numeric, errors='coerce')
            oat_e['rh'] = data
        elif model['name'] == 'SACSMA_OATI_T0P0S0E0I5':
            data = model['data'].apply(pd.to_numeric, errors='coerce')
            oat_i['rh'] = data
    for model_index, model in enumerate(ffc_data):
        if model['gage_id'] == 'SACSMA_CTR_T0P0S0E0I0':
            data = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
            ctrl['ffc'] = data
        elif model['gage_id'] == 'SACSMA_OATT_T5P0S0E0I0':
            data = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
            oat_t['ffc'] = data
        elif model['gage_id'] == 'SACSMA_OATP_T0P30S0E0I0':
            data = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
            oat_pwet['ffc'] = data
        elif model['gage_id'] == 'SACSMA_OATP_T0P-30S0E0I0':
            data = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
            oat_pdry['ffc'] = data
        elif model['gage_id'] == 'SACSMA_OATS_T0P0S5E0I0':
            data = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
            oat_s['ffc'] = data
        elif model['gage_id'] == 'SACSMA_OATE_T0P0S0E5I0':
            data = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
            oat_e['ffc'] = data
        elif model['gage_id'] == 'SACSMA_OATI_T0P0S0E0I5':
            data = model['ffc_metrics'].apply(pd.to_numeric, errors='coerce')
            oat_i['ffc'] = data
    # import pdb; pdb.set_trace()
    # Create plot canvas for dry, avg, wet
    dry_fig, ax = plt.subplots()
    def get_plotlines(year, model):
        plot_line = model['rh'][year]
        return(plot_line)
    def get_plot_points(year, model):
        x_dry = model['ffc'][year]['DS_Tim']
        x_sp = model['ffc'][year]['SP_Tim']
        y_dry = model['rh'][year][x_dry]
        y_sp = model['rh'][year][x_sp]
        return(x_dry, x_sp, y_dry, y_sp)
    # dry year = 2008, avg = 1979, wet = 1998
    month_ticks = [0,32,60,91,121,152,182,213,244,274,305,335]
    month_labels = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
    models = [ctrl, oat_t, oat_pwet, oat_pdry, oat_s, oat_e, oat_i]
    colors = ['dimgrey', 'red', 'blue', 'lightblue', 'green', 'darkorange', 'gold']
    labels = ['Control', 'Temperature', 'Precipitation volume - wet', 'Precipitation volume - dry', 'Seasonal variability', 'Event intensity', 'Interannual variability']
    for index, model in enumerate(models):
        plot_line = get_plotlines(year, model)
        x_dry, x_sp, y_dry, y_sp = get_plot_points(year, model)
        if colors[index] == 'dimgrey':
            linewidth = 4
        else:
            linewidth = 1
        ax.plot(plot_line, color=colors[index], label=labels[index], alpha=0.6, linewidth=linewidth)
        ax.plot(x_dry, y_dry, color=colors[index], marker='^', markersize=6.5, markeredgecolor='black')
        ax.plot(x_sp, y_sp, color=colors[index], marker='o', markersize=6.5, markeredgecolor='black')
        # import pdb; pdb.set_trace()
    plt.xticks(month_ticks, month_labels)
    plt.legend(fontsize=9.5)
    plt.title('Average Year')
    ax.set_ylabel('Flow (cfs)')
    plt.savefig('data_outputs/plots/model_hydrographs/average_year_1979.pdf', dpi=1200)
    plt.show()
    # import pdb; pdb.set_trace()
    return 

def site_hydrograph(ffc_data, rh_data):
    # narrow down for sites of interest
    def get_site_data(dataset, search_key, data_key, rcp):
        macclure = []
        battle = []
        englebright = []
        for site_index, site in enumerate(dataset):
            # error in results having to do with data as string type in upload!!!!
            if rcp in site['model_name']:
                if site[search_key] == 'I20____Lake_McClure_Inflow_calsim_and_wytypes':
                    data = site[data_key].apply(pd.to_numeric, errors='coerce')
                    macclure.append(data)
                elif site[search_key] == 'I10803_Battle_Creek_Inflow_to_Sacramento_River_calsim':
                    data = site[data_key].apply(pd.to_numeric, errors='coerce')
                    battle.append(data)
                elif site[search_key] == '11418000_Englebright_Stern_and_wytypes':
                    data = site[data_key].apply(pd.to_numeric, errors='coerce')
                    englebright.append(data)
        return(macclure, battle, englebright)

    # replace all Nones with row avg, so average across all df's will work
    def site_hydrograph_plotter(site_ffc, site_rh):
        # take avg of models for hist/fut metrics and for rh
        metrics_list = site_ffc[0].index
        all_models_hist = []
        all_models_fut = []
        rh_all_models_hist = []
        rh_all_models_fut = []
        for model in site_ffc:
            metrics_hist = model.iloc[:,0:65].mean(axis=1) # years 1950-2015
            metrics_fut = model.iloc[:,85:150].mean(axis=1) # years 2035-2100
            all_models_hist.append(metrics_hist)
            all_models_fut.append(metrics_fut)
        for model in site_rh:
            rh_all_models_hist.append(model.iloc[:, 0:65]) # 1950-2015
            rh_all_models_fut.append(model.iloc[:, 85:150]) # 2035-2100

        array_hist = np.array(all_models_hist)
        avg_hist = np.nanmean(array_hist, axis=0)
        array_fut = np.array(all_models_fut)
        avg_fut = np.nanmean(array_fut, axis=0)
        final_hist_metrics = pd.DataFrame(data=avg_hist, index = metrics_list)
        final_fut_metrics = pd.DataFrame(data=avg_fut, index = metrics_list)

        for model_index, model in enumerate(site_rh):  
            site_rh[model_index] = site_rh[model_index].replace('None', np.nan)
        site_rh_avg = pd.DataFrame(0, index=site_rh[0].index, columns = site_rh[0].columns)
        for model in site_rh:
            site_rh_avg = site_rh_avg.add(model.apply(pd.to_numeric))
        site_rh_avg = site_rh_avg.divide(10)   

        site_rh_hist = site_rh_avg.iloc[:, 0:65] # 1950-2015
        site_rh_fut = site_rh_avg.iloc[:, 85:150] # 2035-2100

        rh_hist = {}
        rh_fut = {}
        percentile_keys = ['twenty_five', 'fifty', 'seventy_five']
        percentiles = [25, 50, 75]
        for index, percentile in enumerate(percentile_keys):
            rh_hist[percentile] = []
            rh_fut[percentile] = []
        for row_index, _ in enumerate(site_rh_hist.iloc[:,0]): # loop through each row, 366 total
                # loop through all 3 percentiles
                for index, percentile in enumerate(percentiles): 
                    # calc flow percentiles across all years for each row of flow matrix
                    flow_row_hist = pd.to_numeric(site_rh_hist.iloc[row_index, :], errors='coerce')
                    rh_hist[percentile_keys[index]].append(np.nanpercentile(flow_row_hist, percentile))
                    flow_row_fut = pd.to_numeric(site_rh_fut.iloc[row_index, :], errors='coerce')
                    rh_fut[percentile_keys[index]].append(np.nanpercentile(flow_row_fut, percentile))
        np.nanmax(pd.to_numeric(site_rh[7].iloc[:,100]))
        fig, ax = plt.subplots()
        x = np.arange(0,366,1)
        month_ticks = [0,32,60,91,121,152,182,213,244,274,305,335]
        month_labels = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
        ax.plot(rh_hist['fifty'], color = 'navy', label = "Historic (1950-2015)", linewidth=2)
        plt.fill_between(x, rh_hist['twenty_five'], rh_hist['fifty'], color='powderblue', alpha=.5)
        plt.fill_between(x, rh_hist['fifty'], rh_hist['seventy_five'], color='powderblue', alpha=.5)

        ax.plot(rh_fut['fifty'], color = 'darkred', label = "Future (2035-2100)", linewidth=2)
        plt.fill_between(x, rh_fut['twenty_five'], rh_fut['fifty'], color='lightpink', alpha=.5)
        plt.fill_between(x, rh_fut['fifty'], rh_fut['seventy_five'], color='lightpink', alpha=.5)
        
        # add plot anotations using ffc metrics
        ds_tim_fut = np.nanmean(final_fut_metrics.loc['DS_Tim'])
        sp_tim_fut = np.nanmean(final_fut_metrics.loc['SP_Tim'])
        wet_tim_fut = np.nanmean(final_fut_metrics.loc['Wet_Tim'])
        fa_tim_fut = np.nanmean(final_fut_metrics.loc['FA_Tim'])
        ds_mag_fut = np.nanmean(final_fut_metrics.loc['DS_Mag_50'])
        wet_mag_fut = np.nanmean(final_fut_metrics.loc['Wet_BFL_Mag_50'])

        ds_tim_hist = np.nanmean(final_hist_metrics.loc['DS_Tim'])
        sp_tim_hist = np.nanmean(final_hist_metrics.loc['SP_Tim'])
        wet_tim_hist = np.nanmean(final_hist_metrics.loc['Wet_Tim'])
        fa_tim_hist = np.nanmean(final_hist_metrics.loc['FA_Tim'])
        ds_mag_hist = np.nanmean(final_hist_metrics.loc['DS_Mag_50'])
        wet_mag_hist = np.nanmean(final_hist_metrics.loc['Wet_BFL_Mag_50'])
        # np.nanmean(site_ffc_fut.loc['SP_Mag'])
        # np.nanmean(site_ffc_hist.loc['SP_Mag'])

        plt.vlines([ds_tim_hist, sp_tim_hist, wet_tim_hist, fa_tim_hist], ymin=0, ymax= max(rh_fut['seventy_five']), color='navy', alpha=.75)
        plt.vlines([ds_tim_fut, sp_tim_fut, wet_tim_fut, fa_tim_fut], ymin=0, ymax= max(rh_fut['seventy_five']), color='darkred', alpha=.75)
        plt.hlines([ds_mag_hist], xmin=ds_tim_fut, xmax=366, color='navy', alpha=.65)
        plt.hlines([wet_mag_hist], xmin=wet_tim_hist, xmax=sp_tim_hist, color='navy', alpha=.65)
        plt.hlines([ds_mag_fut], xmin=ds_tim_fut, xmax=366, color='darkred', alpha=.65)
        plt.hlines([wet_mag_fut], xmin=wet_tim_fut, xmax=sp_tim_fut, color='darkred', alpha=.65)

        ax.legend(loc='upper left')
        # ax.grid(which="major", axis='y')
        ax.set_ylabel('Flow (cfs)')
        plt.xticks(month_ticks, month_labels)
        # plt.title('Merced River at Lake McClure (Southern)')
        # plt.title('Yuba River below Englebright Dam (Central)')
        plt.title('Battle Creek (Northern)')
        plt.savefig('data_outputs/plots/regional_hist_fut_hydrographs/Battle_regional_hydrograph_rcp85.pdf', format='pdf', dpi=1200) # specify 8.5 or 4.5 in filename
        plt.show()

    macclure_ffc, battle_ffc, englebright_ffc = get_site_data(ffc_data, 'gage_id', 'ffc_metrics', '85') # can switch between 8.5 and 4.5
    macclure_rh, battle_rh, englebright_rh = get_site_data(rh_data, 'name', 'data', '85') # can switch between 8.5 and 4.5
    site_hydrograph_plotter(battle_ffc, battle_rh)

    ## Bar plot for MK results, all FF metrics
def plot_mk_bars_gini():

    df = pd.read_csv('data_outputs/All_MK_results_RCP8.5.csv') # can change between 8.5 and 4.5
    df = df.set_index('Year')
    df = df.drop(['Peak_5', 'Peak_10', 'Peak_Dur_2', 'Peak_Dur_5', 'Peak_Dur_10', 'Peak_Fre_2', 'Peak_Fre_5', 'Peak_Fre_10','DS_No_Flow', 'Std'])
    # matplotlib bar chart will plot bars with same labels together... which is why there are some trailing zeros on labels. 
    x_labels = ['Magnitude', 'Timing', 'Duration', 'Magnitude 10%', 'Magnitude 50%', 'Timing ', 'Duration ', 'Peak annual flow', 'Magnitude ', 'Timing  ', 'Duration  ', 'Rate of change', 'Magnitude 50% ', 'Magnitude 90%', ' Timing', ' Duration', 'Avg. annual flow', 'Coeff. of variation']
    df.index = x_labels
    x = df.index
    # average results across all sites
    metric_avg = []
    for row in range(len(df)):
        metric_avg.append(np.nanmean(df.iloc[row]))
    y = metric_avg

    # Prep gini data for plotting
    # took gini averages across models in spreadsheet, and pasted results here, in decimal form. 
    # See Utils func gini_index_mk_trends() to generate Gini index values
    gini_85 = [0.86, 0.63, 0.97, 0.37, 0.70, 0.40, 0.35, 0.55, 0.55, 0.86, 0.87, 0.89, 0.98, 1.00, 0.46, 0.34, 0.69, 0.32, 0.42, 0.45, 0.45, 0.40, 0.82, 0.59]
    gini_45 = [0.91, 0.86, 0.98, 0.58, 0.79, 0.67, 0.30, 0.55, 0.64, 0.92, 0.98, 0.98, 1.00, 1.00, 0.51, 0.31, 0.80, 0.46, 0.40, 0.53, 0.33, 0.30, 0.88, 0.68]
    def make_gini_stars_rank(gini_nums):
        gini_stars = []
        for index in range(len(gini_nums)):
            if gini_nums[index] < 0.25:
                gini_stars.append('')
                continue
            elif gini_nums[index] < 0.5:
                gini_stars.append('*')
                continue
            elif gini_nums[index] < 0.75:
                gini_stars.append('**')
                continue
            else:
                gini_stars.append('***')
        return(gini_stars)
    gini_85_stars = make_gini_stars_rank(gini_85)
    gini_45_stars = make_gini_stars_rank(gini_45)
    # create bar plot
    colors_ls = ['gold', 'gold', 'gold', 'cornflowerblue', 'cornflowerblue','cornflowerblue','cornflowerblue', 'navy', 
    'yellowgreen', 'yellowgreen','yellowgreen','yellowgreen','lightcoral','lightcoral','lightcoral','lightcoral','grey','grey']
    bars = plt.bar(x, y,  color = colors_ls, edgecolor='black', linewidth=0)
    plt.axis((None,None,-10,10)) 
    # plt.margins(x=.75)

    for index, bar in enumerate(bars):
        height = bar.get_height()
        if height >=0:
            bar_height = height - 0.2
        elif height < 0: 
            bar_height = height - .85
        plt.text(bar.get_x() + bar.get_width()/2., bar_height, gini_45_stars[index],
            ha='center', va='bottom')

    plt.xticks(rotation = 285, fontweight='bold') 
    plt.xticks(fontsize= 8)
    plt.tight_layout()
    # import pdb; pdb.set_trace() 
    plt.savefig('data_outputs/plots/mk_trends_gini_stars85.png', format='png', dpi=1200) # specify in filename: RCP 8.5/4.5
    plt.show()
    return
