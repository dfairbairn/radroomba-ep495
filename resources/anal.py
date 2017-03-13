"""
Analysis code for inspecting the data

"""
# Force matplotlib to not use x-windows backend (because it breaks when I SSH)
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

data_path="data/"
clean1=data_path+"clean_scan_1.csv"
clean2=data_path+"clean_scan_2.csv"
clean3=data_path+"clean_scan_3.csv"
dirty1=data_path+"dirty_scan_1.csv"
dirty2=data_path+"dirty_scan_2.csv"
dirty3=data_path+"dirty_scan_3.csv"

def read_counts(fname_csv):
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
        x.append(float(xi))
        y.append(float(yi))
        counts.append(int(ci))
    # Since I want these as useful arrays, I'll go from list to array now..
    return np.array(x),np.array(y),np.array(counts)

def histo_radmap(fname_csv):
    """
    Use a cheap trick to try to count the number counts vs x/y positions by 
    spawning multiple x,y points for each count at that location
    """
    x,y,counts = read_counts(fname_csv)
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
    x,y,counts = read_counts(fname_csv)
    X,Y = np.meshgrid(x,y)
    Cnts = X*0

    plt.pcolor(X,Y,Cnts)
    plt.colorbar()
    plt.savefigure(fname_csv+".png")

if __name__=="__main__":
    print("Oh hai, Mark!")

    #histo_radmap('clean_scan_1.csv')
    radmap(clean1)

    '''
    radmap(clean2)
    radmap(clean3)
    radmap(dirty1)
    radmap(dirty2)
    radmap(dirty3)

    '''


