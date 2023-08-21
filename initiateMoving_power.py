import numpy as np
import pandas as pd
from Functions import get_data
import pe_and_amp


Node_ls = ["Node0009"]

time_interval = 1
intervals = int(60 / time_interval)

for Node in Node_ls:
    print(Node)
    df, df_og = get_data.get_df(Node)

    """resample height to 1 minute"""''
    df_height = pd.DataFrame()
    df_height[["datetime", "kf_height"]] = df[["datetime", "kf_height_5min"]]
    Height_df_idx = df_height.set_index(df_height.datetime)
    Height_df_1_min = Height_df_idx["kf_height"].resample(rule=f"{time_interval}T").median().reset_index()
    Height_df_1_min = Height_df_1_min.dropna().reset_index()

    pe_and_amp.get_Frequencies(Height_df_1_min, Node, intervals, "kf_height", ["Height"], time_interval)

    """resample hoz_flow to 1 minute"""
    df_hor_flow = pd.DataFrame()
    df_hor_flow[["datetime", "north_east_speed_mpd"]] = df[["datetime", "north_east_speed_mpd_20_min"]]
    hoz_flow_df_idx = df_hor_flow.set_index(df_hor_flow.datetime)
    hoz_flow_df_1_min = hoz_flow_df_idx["north_east_speed_mpd"].resample(rule=f"{time_interval}T").median().reset_index()
    hoz_flow_df_1_min = hoz_flow_df_1_min.dropna().reset_index()


    pe_and_amp.get_Frequencies(hoz_flow_df_1_min, Node, intervals, "north_east_speed_mpd", ["Hoz_flow"], time_interval)



