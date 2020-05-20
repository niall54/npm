import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def oscilloscopeReader(filename, plot=False):
    """
    This function reads a csv file from a KeySight DSOX2024A oscilloscope and
    outputs the data from all relevant channels
    """
    data = pd.read_csv(filename)
    channels = {}
    for i in data:
        if i == 'x-axis':
            time = data[i][2:].astype('float').to_numpy()
        else:
            channels[i] = data[i][2:].astype('float').to_numpy()
            
    if plot:
        for i in channels.keys():
            plt.plot(time,channels[i],label='Ch: {}'.format(i))
        plt.legend()
    
    return time, channels
