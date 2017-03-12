"""
Analysis code for inspecting the data

"""
# Force matplotlib to not use x-windows backend (because it breaks when I SSH)
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def read_robo_counts(fname_csv):
    """
    
    """
    f = open(fname_csv,'r')
    # Throw away the first row housing variable names
    _ = f.readline()
    x = []
    y = []
    counts = []
    for ln in f:
        ci,xi,yi = (ln.split('\n')[0]).split(',') 
        x.append(xi)
        y.append(yi)
        counts.append(ci)
    return x,y,counts

def histo_radmap(fname_csv):
    """
    Use a cheap trick to try to count the number counts vs x/y positions by 
    spawning multiple x,y points for each count at that location
    """
    x,y,counts = read_robo_counts(fname_csv)
    x_final, y_final = ([], [])
    for i,ci in enumerate(counts):
        for j in range(int(ci)):
            x_final.append(x[i])
            y_final.append(y[i])
    plt.scatter(x_final,y_final)
    plt.savefig('tst.png')
    return x_final,y_final

def radmap(fname_csv):
    """
    Makes a very simple color map of the given csv file's "counts/x/y" data.
    """
    dat = pd.read_csv(fname_csv)
    plt.pcolor(dat['x'].as_matrix(),dat['y'].as_matrix(),dat['counts'].as_matrix())
    plt.colorbar()
    plt.savefigure(fname_csv+".png")

if __name__=="__main__":
    print("Oh hai, Mark!")

    histo_radmap('clean_scan_1.csv')
    '''
    radmap('clean_scan_1.csv')
    radmap('clean_scan_2.csv')
    radmap('clean_scan_3.csv')
    radmap('dirty_scan_1.csv')
    radmap('dirty_scan_2.csv')
    radmap('dirty_scan_3.csv')

    '''


