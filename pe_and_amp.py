import numpy as np
import pandas as pd
import matplotlib
import mplcursors
import math
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from scipy.signal import find_peaks
from scipy.stats import linregress
from datetime import datetime, timedelta
from utide import solve, reconstruct
from Functions.time_step import get_5min_gap

def plot_sections(df_current, df, Var):
    plt.scatter(df.datetime, df[Var])
    plt.scatter(df_current.datetime, df_current[Var])

    date_format = mpl_dates.DateFormatter("%j")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.show()

def get_reliable_per(df):
    dp = len(df)
    Num_nan = len(df.dropna())
    percent_real = Num_nan/dp
    return percent_real

def detrend_data(df_import, value):
    df_ = df_import
    value_slope = linregress(x=df_.index, y=df_[value])
    py_slope = value_slope.slope
    py_intercept = value_slope.intercept

    df_detrend = pd.DataFrame()
    df_detrend["datetime"] = df_.datetime
    df_detrend[f"detrend_{value}"] = ((py_slope * df_.index) + py_intercept) - df_[value]
    df_detrend[value] = df_[value]
    return df_detrend, py_slope

def plot_detrend(df_, Node, val):
    """Plots the Original Line and the Detrended data"""
    fig, (ax1, ax2) = plt.subplots(2, 1,)
    plt.suptitle(f"{Node}: {val} Detrended", fontsize=18)
    plt.subplots_adjust(wspace=0.2, hspace=0.35)
    ax1.set_ylabel(val)
    ax1.scatter(df_.datetime, df_[val].replace(0, np.nan), marker="s", s=2, color="red", )

    ax2.scatter(df_.datetime, df_[f"detrend_{val}"].replace(0, np.nan), marker="s", s=2, color="red", )

    ax2.xaxis.set_major_formatter(mpl_dates.DateFormatter("%j"))
    ax2.set_xlabel("Doy")
    ax2.xaxis.set_major_formatter(mpl_dates.DateFormatter("%j"))

    plt.show()

def run_utide(df, value):
    df_go = df.dropna()
    try:
        coef = solve(
            df_go.datetime,
            df_go[f"detrend_{value}"],
            lat=66,
            method="ols",
            conf_int="MC",
            verbose=False,
        )
        # print(coef.keys())
        # print(coef.nR)

        constituents = coef.name
        AMP = coef.A
        PE = coef.PE
        confidence_interval = coef.A_ci
        continue_loop = True
        return constituents, AMP, PE, continue_loop, confidence_interval

    except np.linalg.LinAlgError as err:
        print(f"Unexpected")
        AMP, constituents, PE = ["NONE"], [np.nan], ["NONE"]
        continue_loop = False
        confidence_interval = [np.nan]
        print("skip")

        return constituents, AMP, PE, continue_loop, confidence_interval


def get_Frequencies(df, node, intervals, Variable, saving_vars, time_step):

    """ Used to tell the loop when to stop"""
    Num_days = 4
    last_day = df["datetime"].iloc[-1]
    stop_work = last_day - timedelta(days=Num_days)

    print("\nFirst day ", df["datetime"].iloc[0])
    print("Last day ", last_day)
    print("Stop work ", stop_work, "\n")

    """ For loop of the dataframe in 60min intervals
        - using mask Gets the dataframe
        - Gets the percent of Available data
        - Detrends the Data
        - Runs the Detrended data through Utide
        - Appends the Start, stop, Middle, M2percent and data availability to respective lists
        - if start_date Greater than  stop_work(last day - 4 days to get the last 4 day bin) - Stop
    """
    info_list_dict = {}
    info_list_dict_2 = {}
    info_list_dict_PE = {}
    reliable_data_ls = []
    Slope_ls = []

    for x in range(0, len(df), intervals):
        print(x)
        """ 4 day bin creation"""
        start_date = df.datetime.loc[x]
        end_date = start_date + timedelta(days=Num_days)
        mask = (df['datetime'] > start_date) & (df['datetime'] <= end_date)
        df_current = df.loc[mask]

        # plot_sections(df_current, df, Variable)

        reliable_percent = get_reliable_per(df_current)
        reliable_data_ls.append(reliable_percent)

        """ detrend data """
        if len(df_current.dropna()) <= 10:
            df_detrended, var_slope = np.nan, np.nan
        else:
            df_detrended, var_slope = detrend_data(df_current.dropna(), Variable)
            # plot_detrend(df_detrended, node, Variable)

        Slope_ls.append(var_slope)

        """Run Utide - after checking data"""
        if math.isnan(var_slope):
            print("Bad")
            ls_const, ls_Amplitude, ls_PE, continue_running, confidence_int = ["none"], [np.nan], [np.nan], [False], [np.nan]
        else:
            print("Good")
            ls_const, ls_Amplitude, ls_PE, continue_running, confidence_int = run_utide(df_detrended, Variable)

        dict_running = {}
        dict_running_2 = {}
        dict_running_PE = {}
        for i in range(len(ls_const)):
            dict_running[ls_const[i]] = ls_Amplitude[i]
        for i in range(len(ls_const)):
            dict_running_2[f"{ls_const[i]}_95"] = confidence_int[i]

        for i in range(len(ls_const)):
            dict_running_PE[f"{ls_const[i]}"] = ls_PE[i]

        concat_info = {start_date + timedelta(days=(Num_days / 2)): dict_running}
        # print("concat info", concat_info)

        concat_info_2 = {start_date + timedelta(days=(Num_days / 2)): dict_running_2}

        concat_info_PE = {start_date + timedelta(days=(Num_days / 2)): dict_running_PE}

        info_list_dict.update(concat_info)
        info_list_dict_2.update(concat_info_2)
        info_list_dict_PE.update(concat_info_PE)
        if start_date >= stop_work:
            break

    Nested_ls_df = pd.DataFrame(info_list_dict)
    Nested_ls_df.loc[len(Nested_ls_df)] = reliable_data_ls
    Nested_ls_df = Nested_ls_df.rename(index={(len(Nested_ls_df) - 1): '% Available'})
    Nested_ls_df.loc[len(Nested_ls_df)] = Slope_ls
    Nested_ls_df = Nested_ls_df.rename(index={(len(Nested_ls_df) - 1): 'Slope'})

    Nested_ls_df = Nested_ls_df.reset_index()
    final_data = Nested_ls_df.T
    final_data.columns = final_data.iloc[0]
    final_data.drop(index=final_data.index[0], axis=0, inplace=True)
    final_data = final_data.reset_index()
    final_data.rename(columns={"index": "datetime_middle"}, inplace=True)

    print("Confidence interval!!")
    Nested_ls_df_2 = pd.DataFrame(info_list_dict_2)
    Nested_ls_df_2 = Nested_ls_df_2.reset_index()
    final_data_2 = Nested_ls_df_2.T
    final_data_2.columns = final_data_2.iloc[0]
    final_data_2.drop(index=final_data_2.index[0], axis=0, inplace=True)
    final_data_2 = final_data_2.reset_index()
    final_data_2.rename(columns={"index": "datetime_middle"}, inplace=True)

    final_data.set_index("datetime_middle", inplace=True)
    final_data_2.set_index("datetime_middle", inplace=True)

    final_data_real = final_data.join(final_data_2).reset_index()

    Nested_ls_df_PE = pd.DataFrame(info_list_dict_PE)

    Nested_ls_df_PE.loc[len(Nested_ls_df_PE)] = reliable_data_ls
    Nested_ls_df_PE = Nested_ls_df_PE.rename(index={(len(Nested_ls_df_PE) - 1): '% Available'})
    Nested_ls_df_PE.loc[len(Nested_ls_df_PE)] = Slope_ls
    Nested_ls_df_PE = Nested_ls_df_PE.rename(index={(len(Nested_ls_df_PE) - 1): 'Slope'})

    Nested_ls_df_PE = Nested_ls_df_PE.reset_index()
    final_data_pe = Nested_ls_df_PE.T
    final_data_pe.columns = final_data_pe.iloc[0]
    final_data_pe.drop(index=final_data_pe.index[0], axis=0, inplace=True)
    final_data_pe = final_data_pe.reset_index()
    final_data_pe.rename(columns={"index": "datetime_middle"}, inplace=True)

    print(f"{saving_vars[0]} PE \n", final_data_pe)
    save_loc = f"data/{saving_vars[0]}/PE/{node}_{Num_days}days_frequency_plot_{time_step}min_{Variable}_comb.csv"
    final_data_pe.to_csv(save_loc)


    print(f"{saving_vars[0]}] AMP \n", final_data_real)
    save_loc = f"data/{saving_vars[0]}/AMP/{node}_{Num_days}days_frequency_plot_{time_step}min_{Variable}_comb.csv"
    final_data_real.to_csv(save_loc)


