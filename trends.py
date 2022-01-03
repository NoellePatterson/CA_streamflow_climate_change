import pandas as pd
import numpy as np
import pymannkendall as mk
import statsmodels.api as sm
import statsmodels.formula.api as smf

'''
Calculate Mann-Kendall trends in input flow data processed by the functional flows calculator
'''

def calc_mk_trend(ffc_data, results_dicts, model_name):
# This func needs substantial reworking with most recent version of ffc_data_all in order to work. 
    for gage_index, gage in enumerate(ffc_data): # loop through sites in a model
        # create two new columns for output data
        results_dicts[gage_index]['results']['mk_decision'] = np.nan
        results_dicts[gage_index]['results']['sen_slope'] = np.nan
        # loop through each metric timeseries in the gage (28 metrics total)
        for index, value in enumerate(gage['ffc_metrics'].index):
            metric = gage['ffc_metrics'].loc[value]
            # drop rows with 'None' string as value
            metric = metric.mask(metric.eq('None')).dropna()
            # only perform trend analyses if years of data are above ten
            if len(metric) < 11:
                continue
            # convert string numbers to floats
            for i, val in enumerate(metric):
                metric[i] = float(val)
            metric = pd.to_numeric(metric, errors='coerce')
            mk_stats, ljung = mk_and_ljung(metric)
            # if p-val insig, there is no autocorrelation. can report results and be done with the metric. 
            # Otherwise, need to remove autocorrelation.
            # Try differencing with increasing lag until autocorrelation is removed or timeseries is too short to perform analysis.
            if float(ljung['lb_pvalue']) < 0.05:
                for lag in range(1,len(metric)):
                    if float(ljung['lb_pvalue']) < 0.05:
                        diff = differencing(metric, lag)
                        if len(diff) < 11:
                            break
                        mk_stats, ljung = mk_and_ljung(diff)
                        if float(ljung['lb_pvalue']) < 0.05:
                            continue
                        else:
                            # import pdb; pdb.set_trace()
                            results_dicts[gage_index]['results'].loc[value, 'mk_decision'] = mk_stats.trend
                            # only record slope value if mk result is significant up or down trend
                            if mk_stats.trend != 'no trend':
                                results_dicts[gage_index]['results'].loc[value, 'sen_slope'] = mk_stats.slope  
                                # correct for an occasional error in which a slope of 0 is considered significant by the MK statistic
                                if mk_stats.slope == 0:
                                    results_dicts[gage_index]['results'].loc[value, 'mk_decision'] == 'no trend'
                                    results_dicts[gage_index]['results'].loc[value, 'sen_slope'] == np.nan
                            break
            else: 
                results_dicts[gage_index]['results'].loc[value, 'mk_decision'] = mk_stats.trend
                # only record slope value if mk result is significant up or down trend
                if mk_stats.trend != 'no trend':
                    results_dicts[gage_index]['results'].loc[value, 'sen_slope'] = mk_stats.slope 
                    # correct for an occasional error in which a slope of 0 is considered significant by the MK statistic  
                    if mk_stats.slope == 0:
                        results_dicts[gage_index]['results'].loc[value, 'mk_decision'] = 'no trend'
                        results_dicts[gage_index]['results'].loc[value, 'sen_slope'] = np.nan  

    metrics = results_dicts[0]['results'].index
    summary_df = pd.DataFrame(index=metrics)
    for index, site in enumerate(results_dicts):
        summary_df[site['gage_id']] = site['results']['mk_decision']
    summary_df.to_csv('data_outputs/MK_outputs_all_models/mk_summary_'+ model_name +'.csv')
    return summary_df

def mk_and_ljung(array):
    mk_stats = mk.original_test(array)
    x_vals = np.arange(1, len(array)+1, 1)
    y_vals = x_vals * mk_stats.slope + mk_stats.intercept
    residuals = array - y_vals
    # Use up to 10 lags in ljung test, considered good default value 
    ljung = sm.stats.acorr_ljungbox(residuals, lags=[10], return_df=True)
    return mk_stats, ljung

def differencing(array, lag=1):
    # keep in mind differencing shortens the timeseries by len=lag
    diff = []
    for i in range(len(array)-lag):
        diff.append(array[i+lag] - array[i])
    return diff



