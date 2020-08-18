import pandas as pd
import numpy as np
from math import sqrt
from functools import reduce

window_size = 50
step_size = 25


def get_features_dataset_from_raw(data, gt):
    df_windowed = windows(data, window_size, step_size)
    df_features = extract_features(df_windowed, data.shape[0], window_size, step_size)
    df_norm = df_features.apply(normalize, axis=1)
    df_norm['CLASS'] = gt

    return df_norm


def windows(data, window_size, step):
    r = np.arange(len(data))
    s = r[::step]
    z = list(zip(s, s + window_size))
    f = '{0[0]}:{0[1]}'.format
    g = lambda step : data.iloc[step[0]:step[1]]
    return pd.concat(map(g, z), keys=map(f, z))


def extract_features(wdf, data_shape, window_size, step_size):
    df = pd.DataFrame()
    for i in range(0, data_shape, step_size):
        window = wdf.loc['{0}:{1}'.format(i, i + window_size)].drop(columns=['timestamp'])

        pitch_roll = pitch_and_roll(window)
        v_mean = window.mean(axis=0)
        v_median = window.median(axis=0)
        v_max = window.max(axis=0)
        v_min = window.min(axis=0)
        v_std = window.std(axis=0)
        v_range = v_max - v_min
        v_rms = rms_series(window)
        v_diff = diff_series(window)
        v_cross = zero_crossing_series(window, v_mean)

        window_df = join_series([pitch_roll, v_mean, v_median, v_max, v_min, v_std, v_range, v_rms, v_diff, v_cross],
                                ["", "_mean", "_median", "_max", "_min", "_std", "_range", "_rms", "_diff", "_cross"])

        df = pd.concat([df, window_df], ignore_index=True)

    return df


def normalize(data):
    return (data - data.min()) / (data.max() - data.min())


################################
## Feature extraction methods ##
################################

def join_series(series, suffixes):
    for i, serie in enumerate(series):
        current_df = serie.to_frame().transpose()
        if i == 0:
            df = current_df
        else:
            df = df.join(current_df, lsuffix=suffixes[i - 1], rsuffix=suffixes[i])
    return df


def to_series(data, index):
    return pd.Series(data, index=index)


def angular_function(a, b):
    return (np.arctan2(a / 9.81, b / 9.81) * 180 / np.pi).mean()


def pitch_and_roll(window):
    return to_series([angular_function(window['y'], window['z']), angular_function(window['x'], window['z'])],
                     ['pitch', 'roll'])


def rms_series(window):
    def rms(values):
        return sqrt(reduce(lambda prev, curr: prev + curr ** 2, values, 0) / len(values))

    return to_series([rms(window['x']), rms(window['y']), rms(window['z'])], ['x', 'y', 'z'])


def diff_series(window):
    return window.diff(periods=1).abs().mean()


def zero_crossing_series(window, means):
    def zero_crossing(values, mean):
        return (np.sign(values - mean).diff().dropna() != 0).sum()

    zero_crossings = []
    for i in means.index:
        zero_crossings.append(zero_crossing(window[i], means[i]))

    return to_series(zero_crossings, ['x_cross', 'y_cross', 'z_cross'])
