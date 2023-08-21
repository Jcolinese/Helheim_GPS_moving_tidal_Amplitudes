import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mpl_dates
from datetime import datetime, timedelta
import scipy
import math
from Functions import get_data

def get_moving_power(node):
    print(node)

    height_amp_ = pd.read_csv(f"data/Height/AMP/{node}_4days_frequency_plot_1min_kf_height_comb.csv", index_col=0)
    height_amp_["datetime_middle"] = pd.to_datetime(height_amp_['datetime_middle'], format="%Y-%m-%d %H:%M:%S")

    height_pe_ = pd.read_csv(f"data/Height/PE/{node}_4days_frequency_plot_1min_kf_height_comb.csv", index_col=0)
    height_pe_["datetime_middle"] = pd.to_datetime(height_pe_['datetime_middle'], format="%Y-%m-%d %H:%M:%S")

    horizontal_amp_ = pd.read_csv(f"data/Hoz_flow/AMP/{node}_4days_frequency_plot_1min_north_east_speed_mpd_comb.csv", index_col=0)
    horizontal_amp_["datetime_middle"] = pd.to_datetime(horizontal_amp_['datetime_middle'], format="%Y-%m-%d %H:%M:%S")

    horizontal_pe_ = pd.read_csv(f"data/Hoz_flow/Pe/{node}_4days_frequency_plot_1min_north_east_speed_mpd_comb.csv", index_col=0)
    horizontal_pe_["datetime_middle"] = pd.to_datetime(horizontal_pe_['datetime_middle'], format="%Y-%m-%d %H:%M:%S")

    return height_amp_, height_pe_, horizontal_amp_, horizontal_pe_

Node = "Node0009"
height_amp, height_pe, horizontal_amp, horizontal_pe = get_moving_power(Node)
Quakes_df, calv_pt_df = get_data.get_calving_events()
df, df_og = get_data.get_df(Node)
print(height_amp)
Node_ls = []
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
fig.subplots_adjust(hspace=0.4)

Num_days = "4"
plt.suptitle(f"{Node} - Horizontal flow {Num_days} frequency plot")
ax1.scatter(df_og.datetime, df_og["north_east_speed_mpd"], s=5, color="black")
ax1.scatter(df.datetime, df["north_east_speed_mpd_20_min"], s=5, color="red")

# ax1.set_ylim(10, 50)
ax1.set_ylabel("Horizontal Flow (m/d)")

for const in horizontal_amp.columns:
    if const == "datetime_middle":
        pass
    elif const == "nan":
        print("NANANAN")
        pass
    elif const == "Slope":
        pass
    elif const == "% Available":
        print("% available")
        print(horizontal_amp[const])
    elif const[-3:] == "_95":
        pass
    else:
        if math.isnan(height_amp[const][0]):
            print(const)
            print(height_amp[const])
            # ax2.plot(horizontal_amp["datetime_middle"], horizontal_amp[const].replace(np.nan, 0), label=const)
            pass
        else:
            ax2.plot(horizontal_amp["datetime_middle"], horizontal_amp[const], label=const)

        Node_ls.append(const)
        # ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07),
        #            fancybox=True, shadow=True, ncols=((len(horizontal_amp.columns) - 2)/2))
        # ax2.set_ylim(0, 2)

for const_pe in horizontal_pe.columns:
    if const_pe == "datetime_middle":
        pass
    elif const_pe == "nan":
        pass
    elif const_pe == "Slope":
        pass
    elif const_pe == "% Available":
        print("% available")
    else:
        # ax_2 = ax2.twinx()
        ax3.plot(horizontal_pe["datetime_middle"], horizontal_pe[const_pe], label=const_pe)
        Node_ls.append(const_pe)
        ax3.legend(loc='upper center', bbox_to_anchor=(0.5, -0.3),
                   fancybox=True, shadow=True, ncols=(len(horizontal_pe.columns) - 2))


for calve_event in range(len(calv_pt_df)):
    c_event = calv_pt_df["Datetime_obj"].loc[calve_event]
    ax1.axvline(x=c_event, color='grey')
    ax2.axvline(x=c_event, color='grey')
    ax3.axvline(x=c_event, color='grey')

for quake_event in range(len(Quakes_df)):
    s_event = Quakes_df["datetime"].loc[quake_event]
    ax1.axvline(x=s_event, color='green')
    ax2.axvline(x=s_event, color='green')
    ax3.axvline(x=s_event, color='green')



print(df.datetime.iloc[1])
ax3.set_xlim((df.datetime.iloc[1]-timedelta(days=1)), (df.datetime.iloc[-1] + timedelta(days=1)))

ax2.set_ylabel("Amplitude")
ax3.set_ylabel("Percent Energy")

ax3.xaxis.set_major_formatter(mpl_dates.DateFormatter("%j"))
ax3.set_xlabel("DOY")
# plt.show()




Node_ls = []
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
# fig.subplots_adjust(bottom=0.2)
fig.subplots_adjust(hspace=0.4)

Num_days = "4"
plt.suptitle(f"{Node} -Height - {Num_days} frequency plot")
# ax1.scatter(df.datetime, df["height"], s=5, color="black")
ax1.scatter(df.datetime, df["kf_height_5min"], s=5, color="red")
# ax1.set_ylim(50, 230)
ax1.set_ylabel("Height (m)")

for const in height_amp.columns:
    if const == "datetime_middle":
        pass
    elif const == "nan":
        pass
    elif const == "Slope":
        pass
    elif const == "% Available":
        print("% available")
        print(height_amp[const])
    elif const[-3:] == "_95":
        pass
    else:
        # ax_2 = ax2.twinx()
        if math.isnan(height_amp[const][0]):
            print(const)
            print(height_amp[const])
            # ax2.plot(height_amp["datetime_middle"], height_amp[const].replace(np.nan, 0.0), label=const)
            pass
        else:
            ax2.plot(height_amp["datetime_middle"], height_amp[const], label=const)
        Node_ls.append(const)

        # ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.07),
        #            fancybox=True, shadow=True, ncols=((len(height_amp.columns) - 2)/2))


for const_pe in height_pe.columns:
    if const_pe == "datetime_middle":
        pass
    elif const_pe == "nan":
        pass
    elif const_pe == "Slope":
        pass
    elif const_pe == "% Available":
        print("% available")
    else:
        # ax_2 = ax2.twinx()
        ax3.plot(height_pe["datetime_middle"], height_pe[const_pe], label=const_pe)
        Node_ls.append(const_pe)
        ax3.legend(loc='upper center', bbox_to_anchor=(0.5, -0.3),
                   fancybox=True, shadow=True, ncols=(len(height_pe.columns) - 2))


for calve_event in range(len(calv_pt_df)):
    c_event = calv_pt_df["Datetime_obj"].loc[calve_event]
    ax1.axvline(x=c_event, color='grey')
    ax2.axvline(x=c_event, color='grey')
    ax3.axvline(x=c_event, color='grey')

for quake_event in range(len(Quakes_df)):
    s_event = Quakes_df["datetime"].loc[quake_event]
    ax1.axvline(x=s_event, color='green')
    ax2.axvline(x=s_event, color='green')
    ax3.axvline(x=s_event, color='green')

ax2.set_ylabel("Amplitude")
ax3.set_ylabel("Percent Energy")

ax3.xaxis.set_major_formatter(mpl_dates.DateFormatter("%j"))
ax3.set_xlabel("DOY")
ax3.set_xlim((df.datetime.iloc[1]-timedelta(days=1)), (df.datetime.iloc[-1] + timedelta(days=1)))

plt.show()