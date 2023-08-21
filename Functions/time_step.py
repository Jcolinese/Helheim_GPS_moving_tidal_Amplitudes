import pandas as pd
from datetime import datetime, timedelta


def get_5min_gap(dataframe, time_step):
    dict_1 = []

    def get_5minsnow(date):
        time_ = time_step
        current_d = date["datetime"]
        previous_5 = current_d - timedelta(minutes=time_ + 5)
        next_5 = current_d + timedelta(minutes=time_)
        dict_ = {
            "start_time": current_d,
            "previous_5": previous_5,
            "next_5": next_5,
        }
        return dict_

    df_f = dataframe
    df_f["datetime"] = pd.to_datetime(df_f['datetime'], format="%Y-%m-%d %H:%M:%S")
    df_f["5mins_time_gap_og"] = df_f["5mins_time_gap"]

    df_f["my_column_changes"] = df_f["5mins_time_gap"].shift() != df_f["5mins_time_gap"]

    for x in df_f[df_f["my_column_changes"] == True].index:
        if x == 0:
            pass
        elif x == 1:
            pass
        else:
            df = get_5minsnow(df_f.loc[x])
            dict_1.append(df)

    # print(dict_1)
    df_1 = pd.DataFrame(dict_1)
    # print(df_1)

    for y in df_1.index:
        start_date = df_1["previous_5"].loc[y]
        end_date = df_1["next_5"].loc[y]

        after_start_date = df_f["datetime"] >= start_date
        before_end_date = df_f["datetime"] <= end_date
        between_two_dates = after_start_date & before_end_date
        df_f.loc[between_two_dates, "5mins_time_gap"] = 1.0

    return df_f
