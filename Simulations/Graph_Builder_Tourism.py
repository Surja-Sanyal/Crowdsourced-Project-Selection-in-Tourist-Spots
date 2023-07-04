#Program:   Surplus Food Redistribution Simulations
#Inputs:    TBD
#Outputs:   TBD
#Author:    Surja Sanyal
#Date:      29 JUN 2022
#Comments:  None




##   Start of Code   ##


#   Imports    #

import os
import re
import sys
import math
import copy
import time
import psutil
import shutil
import random
import datetime
import traceback
import itertools
import matplotlib
import numpy as np
import multiprocessing
from textwrap import wrap
from functools import partial
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from scipy.stats import truncnorm




##  Global environment   ##

#   Customize here  #
AGENTS                  = 5000                  #Number                             Default number of agent requests
PAYLOAD_MAX             = 100                   #Number                             Volunteer payload limit in kilograms
COORDINATE_MAX          = 50                    #Number                             City start (at 0) to end limit in kilometers
DAY_MAX                 = 18                    #Number                             Day start (at 0) to end limit in hours
SAVE                    = "OFF"                 #ON/OFF                             Save data
SORTING                 = "END"                 #START/END                          Receiver sorting
PREFERENCE              = "ELIGIBLE"            #ORIGINAL/ELIGIBLE/UPDATED          Usage of preference lists
VOLUNTEERS              = "1X"                  #1X/2X/4X/8X/16X/32X                Volunteer availability (1/2/4/8/16/32) times donors
MANIPULATION            = "ON"                  #ON/OFF                             Manipulation of preferences

#   Thresholds  #
To      = 0.25                                  #Overlap time (hours)
Tl      = 5                                     #Off-routing (percentage)
Tm      = 1                                     #Meal size  (kilograms)
Ta      = 20                                    #Extra payload (percentage)
Tpm     = 5000                                  #Default perishable food travel distance (kilometers)
Tpnm    = 1000                                  #Default perishable food travel distance (kilometers)
Tnp     = 10000                                 #Default non-perishable food travel distance (kilometers)
Td      = 2                                     #Process advance start threshold for donors (hours)
Tr      = 3                                     #Process advance start threshold for receivers (hours)
Tw      = 10                                    #Match acceptance window (minutes)

#   Do not change   #
RESOLUTION          = 1000                                                  #Output resolution
LOCK                = multiprocessing.Lock()                                #Multiprocessing lock
CPU_COUNT           = multiprocessing.cpu_count()                           #Logical CPUs
MEMORY              = math.ceil(psutil.virtual_memory().total/(1024.**3))                   #RAM capacity
DATA_LOAD_LOCATION  = os.path.dirname(sys.argv[0]) + "/Statistics/"         #Data load location
#DATA_LOAD_LOCATION = os.path.dirname(sys.argv[0]) + "/Statistics/Incentive Module/Foolproof/"          #Data load location
DATA_STORE_LOCATION = os.path.dirname(sys.argv[0]) + "/Graphs/"             #Data store location
#DATA_STORE_LOCATION    = os.path.dirname(sys.argv[0]) + "/Graphs/Incentive Module/Foolproof/"              #Data store location




##  Function definitions    ##


#   Print with lock    #
def print_locked(*content, sep=" ", end="\n"):

    store = DATA_LOAD_LOCATION
    
    with open(store + "_Log_File.txt", "a") as log_file:
    
        try:
        
            with lock:
            
                print (*content, sep = sep, end = end)
                print (*content, sep = sep, end = end, file=log_file)

        except Exception:
        
            with LOCK:
            
                print (*content, sep = sep, end = end)
                print (*content, sep = sep, end = end, file=log_file)


#   Convert string to int or float    #
def convert(some_value):

    try:
        return int(some_value)
        
    except ValueError:
    
        try:
        
            return float(some_value)
        
        except ValueError:
        
            print_locked(traceback.format_exc())


#   Heights of bars #
def autolabel(rects, ax):

    for rect in rects:
    
        h = rect.get_height()
        ax.text(rect.get_x()+rect.get_width()/2., 1.05*h, '%.2f'%float(h), ha='center', va='bottom', rotation='vertical')


#   Display execution data in a graph   #
def display_graph(file_name):

    load, store = DATA_LOAD_LOCATION, DATA_STORE_LOCATION
    receiver, data = [], []
    total_votes, tourists, ministers, selected = [], [], [], []
    fig_name = file_name
    
    #   Read data   #
    receiver = [1, 2, 3, 4, 5]
    with open(load + file_name + ".txt", "r") as fp:
        
        for row, line in enumerate(fp):
        
            pieces = [convert(stat) for stat in line.strip().split()]
            data.append(pieces)
            
                
    
    for row, each_entry in enumerate(data):
    
        if (row == 0):
            
            selected.extend(each_entry)
        
        elif (row == 1):
        
            tourists.extend(each_entry)

        elif (row == 2):

            ministers.extend(each_entry)

        else:

            total_votes.extend(each_entry)

    #print([i * float(file_name) for i in ministers], receiver)    


    #   Create the figure   #
    comparison = plt.figure(fig_name)
    
    labels = ['Tourists & Residents', 'Ministers - Weighted', 'Final - Selected']
    ax = plt.subplot(111, ylim=(0, 1.4 * max(total_votes)))
    #plt.xticks(rotation=20)
    
    width = 0.2
    bars = []
    colors = ['r', 'b', 'g', 'y']

    y_axis = np.vstack((tourists, ministers, total_votes))
    for row in range(len(y_axis)):
    
        bars.append(ax.bar([each + (row - 1) * (width) for each in receiver], y_axis[row], width=width, color=colors[row], align='center'))
    
    #ax.set_xticks([tick for tick in receiver])
    #ax.set_xticklabels(['Constant', 'Linearly\nIncreasing', 'Linearly\nDecreasing', 'Random', 'Exponential'])
    #ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    #ax.set_yticklabels(['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'])

    plt.rcParams['legend.title_fontsize'] = 10
    ax.legend(bars, labels, loc='upper center', title='Vote Count Type', fontsize=8, ncol = 3)
    
    #   Customize plot   #
    [autolabel(bars[row], ax) for row in range(len(bars))]
    
    ax.set_xticks(receiver)
    ax.set_xticklabels([pos + ": Project " + str(winner) for pos, winner in zip(['I', 'II', 'III', 'IV', 'V'], selected)], fontsize=8)
    plt.ylabel('Weighted Vote Counts ' + r'$\rightarrow$', fontsize=20)
    plt.xlabel('\nSelection Order ' + r'$\rightarrow$', fontsize=20, labelpad=-12)
    #plt.tight_layout(pad=1.0, w_pad=1.0, h_pad=1.0)
    
    comparison.savefig(store + file_name + ".pdf", bbox_inches='tight')


#   Display execution data in a graph   #
def display_customized_graph(file_name):

    load, store = DATA_LOAD_LOCATION, DATA_STORE_LOCATION
    receiver, data = [], []
    true, false = [], []
    fig_name = file_name
    
    #   Read data   #
    receiver = [100, 200, 300, 400, 500]
    with open(load + file_name + ".txt", "r") as fp:
        
        for row, line in enumerate(fp):
        
            pieces = [convert(stat) for stat in line.strip().split()]
            data.append(pieces)
            
    
    for row, each_entry in enumerate(data):
    
        if (row == 0):
            
            true.extend(each_entry)
        
        elif (row == 1):
        
            false.extend(each_entry)


    #print([i * float(file_name) for i in ministers], receiver)    


    #   Create the figure   #
    comparison = plt.figure(fig_name)
    
    labels = ['Honest', 'Dishonest']
    ax = plt.subplot(111, ylim=(0, 1.4 * max(true)))
    #plt.xticks(rotation=20)
    
    width = 20
    bars = []
    colors = ['g', 'r', 'b', 'y']

    y_axis = np.vstack((true, false))
    for row in range(len(y_axis)):
    
        bars.append(ax.bar([each + ((-1) ** (row + 1)) * (width/2) for each in receiver], y_axis[row], width=width, color=colors[row], align='center'))
    
    ax.set_xticks([tick for tick in receiver])
    ax.set_xticklabels([str(tick) for tick in receiver])
    #ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    #ax.set_yticklabels(['0.0', '0.2', '0.4', '0.6', '0.8', '1.0'])

    plt.rcParams['legend.title_fontsize'] = 10
    ax.legend(bars, labels, loc='upper center', title='Vote Type', fontsize=8, ncol = 3)
    
    #   Customize plot   #
    [autolabel(bars[row], ax) for row in range(len(bars))]
    
    #ax.set_xticks(receiver)
    #ax.set_xticklabels([pos + ": Project " + str(winner) for pos, winner in zip(['I', 'II', 'III', 'IV', 'V'], selected)], fontsize=8)
    plt.ylabel('Budget Utilization ( % )' + r'$\rightarrow$', fontsize=20)
    plt.xlabel('\nTotal Participants ' + r'$\rightarrow$', fontsize=20, labelpad=-12)
    #plt.tight_layout(pad=1.0, w_pad=1.0, h_pad=1.0)
    
    comparison.savefig(store + file_name + ".pdf", bbox_inches='tight')



##  The main function   ##

#   Main    #
def main():

    data_sources = [1, 3, 5, 10, 15, 20, 100, 300, 500, 'Tourists', 'Ministers']
    
    [display_graph(str(name)) for name in data_sources[:-2]]
    [display_customized_graph(str(name)) for name in data_sources[-2:]]
    #display_line_graph_3D("3D")



##  Call the main function  ##

#   Initiation  #
if __name__=="__main__":

    try:
    
        #   Start logging to file     #        
        print_locked('\n\n\n\n{:.{align}{width}}'.format("Execution Start at: " 
            + str(datetime.datetime.now()), align='<', width=70), end="\n\n")
        
        print_locked("\n\nProgram Name:\n\n" + str(sys.argv[0].split("/")[-1]))
        
        print_locked("\n\nProgram Path:\n\n" + os.path.dirname(sys.argv[0]))
        
        print_locked("\n\nProgram Name With Path:\n\n" + str(sys.argv[0]), end="\n\n\n")
        
        #   Clear the terminal  #
        os.system("clear")
        
        #   Initiate lock object    #
        lock = multiprocessing.Lock()

        #   Initiate pool objects   #
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        
        #   Call the main program   #
        start = datetime.datetime.now()
        main()
        print_locked("\nProgram execution time:\t\t", datetime.datetime.now() - start, "hours\n")
        
        #   Close Pool object    #
        pool.close()

    except Exception:
    
        print_locked(traceback.format_exc())


##   End of Code   ##

