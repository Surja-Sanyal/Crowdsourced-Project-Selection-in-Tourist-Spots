#Program:   Tourism Knapsack V1
#Inputs:    None
#Outputs:   Files: (Appends)
#           1. DATA_STORE_LOCATION/Statistics/Per Round.txt
#           2. DATA_STORE_LOCATION/Statistics/Total Cumulative.txt
#           3. DATA_STORE_LOCATION/Statistics/Individual Cumulative.txt
#Author:    Surja Sanyal
#Email:     hi.surja06@gmail.com
#Date:      02 JUL 2022
#Comments:  1. Please create a folder named "Statistics" in the location DATA_STORE_LOCATION. Outputs will be saved there.




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
import pickle
import random
import datetime
import traceback
import itertools
import numpy as np
import collections
import multiprocessing
from textwrap import wrap
from functools import partial
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
from decimal import Decimal, getcontext




##  Global environment   ##

#   Customize here  #
WEIGHTAGE               = 10                 #Number             #Ministers' vote weightage; = {1 / 3 / 5}
TOURISTS                = 500               #Number             #Number of tourists; = {100 / 300 / 500}
FACTOR                  = 5                #Number             #TOURISTS / FACTOR = MINISTERS; = {5 / 6.5 / 10}
SAVE                    = False             #Boolean            #Save option for votes

#   Do not change   #
LOCK                    = multiprocessing.Lock()
DATA_LOAD_LOCATION      = os.path.dirname(sys.argv[0]) + "/"    #Local data load location
DATA_STORE_LOCATION     = os.path.dirname(sys.argv[0]) + "/"    #Local data store location
#DATA_LOAD_LOCATION     = "/content" + "/"                      #Drive data load location
#DATA_STORE_LOCATION    = "/content" + "/"                      #Drive data store location




##  Function definitions    ##


#   Notify completion   #
def notify():
    
    duration = 2    # seconds
    freq = 2000     # Hz
    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))


#   Print with lock    #
def print_locked(*content, sep=" ", end="\n"):

    store = DATA_STORE_LOCATION
    
    with open(store + "_Log_File.txt", "a") as log_file:
    
        try:
        
            with LOCK:
            
                print (*content, sep = sep, end = end)
                print (*content, sep = sep, end = end, file=log_file)

        except Exception:
        
            print ("\n==> Failed to print below content to file.\n")
            print (*content, sep = sep, end = end)
            print ("\n==> Content not in log file ends here.\n")


#   Convert read values to int, str or list    #
def convert(some_value):

    try:
    
        return int(some_value)
        
    except ValueError:
    
        if ',' not in some_value:
        
            return some_value[1:-1]
        
        else:
        
            return [int(element) for element in re.split("\[|, |\]", some_value)]


#   Get statistics  #
def get_stats(tourists, weightage):

    B = 1000000

    load, store, factor, save, item_price_list = DATA_LOAD_LOCATION, DATA_STORE_LOCATION, FACTOR, SAVE, []

    with open(load + "_item_price_list.txt", "r") as fp:
                                        
        for line in fp:

            item_price_list = item_price_list + [[convert(piece) for piece in [x for x in re.split("\[|, |\]", line) if x.strip()]]]

    h_t_votes, h_m_votes, d_t_votes, d_m_votes = [], [], [], []
    items, prices = [it[0] for it in item_price_list], [it[1] for it in item_price_list]

    if(save):

        #   For tourists    #
        h_t_guy, h_m_guy = [], []
        for i in range(tourists):

            total, choices, visited = 0, [], []

            while(len(visited) < len(items)):
                
                print(i, len(visited), len(choices), len(items))
                next_item = random.choice([item for item in items if item not in visited])

                if(next_item not in visited):

                    visited = visited + [next_item]

                    if(total + prices[items.index(next_item)] <= B):
                        
                        choices = choices + [next_item]
                        total += prices[items.index(next_item)]

            h_t_votes = h_t_votes + choices

            if(i == 0):

                h_t_guy = copy.deepcopy(choices)

        #   For ministers   #
        
        for i in range(int(tourists/factor)):

            total, choices, visited = 0, [], []

            while(len(visited) < len(items)):
                
                print(i, len(visited), len(choices), len(items))
                next_item = random.choice([item for item in items if item not in visited])

                if(next_item not in visited):

                    visited = visited + [next_item]

                    if(total + prices[items.index(next_item)] <= B):

                        choices = choices + [next_item]
                        total += prices[items.index(next_item)]

            h_m_votes = h_m_votes + choices

            if(i == 0):

                h_m_guy = copy.deepcopy(choices)

        #   Save votes  #
        with open(store + "_honest_tourist_votes.pickle", "wb") as fp:
                                    
            pickle.dump(h_t_votes, fp)

        with open(store + "_honest_minister_votes.pickle", "wb") as fp:
                                    
            pickle.dump(h_m_votes, fp)

        with open(store + "_honest_tourist_1.pickle", "wb") as fp:
                                    
            pickle.dump(h_t_guy, fp)

        with open(store + "_honest_minister_1.pickle", "wb") as fp:
                                    
            pickle.dump(h_m_guy, fp)

        #   Dishonest   #
        d_t_votes, d_m_votes = copy.deepcopy(h_t_votes), copy.deepcopy(h_m_votes)
        
        '''
        for i in range(len(d_t_votes)):

            if(i % tourists == 0):
                
                d_t_votes[i] = random.choice(items)

        for i in range(len(d_m_votes)):

            if(i % (tourists/factor) == 0):
                
                d_m_votes[i] = random.choice(items)
        '''

        d_t_votes[0] = random.choice([item for item in items if item != d_t_votes[0]])
        d_m_votes[0] = random.choice([item for item in items if item != d_m_votes[0]])

        
        #   Save votes  #
        with open(store + "_dishonest_tourist_votes.pickle", "wb") as fp:
                                    
            pickle.dump(d_t_votes, fp)

        with open(store + "_dishonest_minister_votes.pickle", "wb") as fp:
                                    
            pickle.dump(d_m_votes, fp)

    else:

        #   Load votes  #
        with open(load + "_honest_tourist_votes.pickle", "rb") as fp:
                                    
            h_t_votes = pickle.load(fp)

        with open(load + "_honest_minister_votes.pickle", "rb") as fp:
                                    
            h_m_votes = pickle.load(fp)

        #   Load votes  #
        with open(load + "_dishonest_tourist_votes.pickle", "rb") as fp:
                                    
            d_t_votes = pickle.load(fp)

        with open(load + "_dishonest_minister_votes.pickle", "rb") as fp:
                                    
            d_m_votes = pickle.load(fp)

        with open(load + "_honest_tourist_1.pickle", "rb") as fp:
                                    
            h_t_guy = pickle.load(fp)

        with open(load + "_honest_minister_1.pickle", "rb") as fp:
                                    
            h_m_guy = pickle.load(fp)

    h_t_votes, h_m_votes, d_t_votes, d_m_votes = h_t_votes[:tourists], h_m_votes[:int(tourists/factor)], d_t_votes[:tourists], d_m_votes[:int(tourists/factor)]

    h_t_freq, h_m_freq = collections.Counter(h_t_votes), collections.Counter(h_m_votes)

    m_weighted_freq = collections.Counter()
    for i in h_m_freq:
        
        m_weighted_freq[i] = h_m_freq[i] * weightage

    results = h_t_freq + m_weighted_freq
    results = sorted(results.items(), key=lambda x:(-x[1], x[0]), reverse=False)
    
    projects, costs, total_cost = [], [], 0
    for item, freq in results:

        index = items.index(item)
        price = prices[index]
        
        if(total_cost + price <= B):

            total_cost += price
            projects = projects + [item]
            costs = costs + [price]

    print_locked("\n\t<== HONEST VOTE RESULTS ==>\n")
    print_locked("\nWeightage given per vote for ministers:\t", weightage)
    print_locked("\nTotal number of tourists for this vote:\t", tourists)
    print_locked("\nTotal number of ministers for this vote:", int(tourists/factor))
    print_locked("\nTotal number of projects selected:\t", len(projects))

    print(tourists/factor)

    print_locked("\n\nPROJECTS SELECTED AND THEIR VOTE COUNTS:\n")
    print_locked("Projects Selected -> Tourist Votes -> Minister Votes -> Final Votes\n")

    [print_locked(projects[i] + 1, end = "\t") for i in range(5)]
    print_locked()
    [print_locked(h_t_freq[projects[i]], end = "\t") for i in range(5)]
    print_locked()
    [print_locked(m_weighted_freq[projects[i]], end = "\t") for i in range(5)]
    print_locked()
    [print_locked(results[i][1], end = "\t") for i in range(5)]
    print_locked()

    t_budget_utilization = 0
    for item in projects:

        if(item in h_t_freq.elements()):

            t_budget_utilization += prices[items.index(item)] * h_t_freq[item]

    m_budget_utilization = 0
    for item in projects:

        if(item in h_m_freq.elements()):

            m_budget_utilization += prices[items.index(item)] * h_m_freq[item]

    h_t_guy_utility = 0
    for item in projects:

        if(item in h_t_guy):

            h_t_guy_utility += prices[items.index(item)]

    h_m_guy_utility = 0
    for item in projects:

        if(item in h_m_guy):

            h_m_guy_utility += prices[items.index(item)]

    print_locked("\n\nHONEST BUDGET UTILIZATION: ( % )\n")
    print_locked("Tourists -> Ministers\n")
    print_locked("{:.2f}".format((100 * h_t_guy_utility)/(B)), "{:.2f}".format((100 * h_m_guy_utility)/(B)))
    print_locked()

    #h_t_freq, h_m_freq = copy.deepcopy(t_freq), copy.deepcopy(m_freq)
    t_freq, m_freq = collections.Counter(d_t_votes), collections.Counter(d_m_votes)

    m_weighted_freq = collections.Counter()
    for i in m_freq:
        
        m_weighted_freq[i] = m_freq[i] * weightage

    results = t_freq + m_weighted_freq
    results = sorted(results.items(), key=lambda x:(-x[1], x[0]), reverse=False)
    
    projects, costs, total_cost = [], [], 0
    for item, freq in results:

        index = items.index(item)
        price = prices[index]
        
        if(total_cost + price <= B):

            total_cost += price
            projects = projects + [item]
            costs = costs + [price]

    print_locked("\n\t<== DISHONEST VOTE RESULTS ==>\n")
    print_locked("\nWeightage given per vote for ministers:\t", weightage)
    print_locked("\nTotal number of tourists for this vote:\t", tourists)
    print_locked("\nTotal number of ministers for this vote:", int(tourists/factor))
    print_locked("\nTotal number of projects selected:\t", len(projects))

    print_locked("\n\nPROJECTS SELECTED AND THEIR VOTE COUNTS:\n")
    print_locked("Projects Selected -> Tourist Votes -> Minister Votes -> Final Votes\n")

    [print_locked(projects[i] + 1, end = "\t") for i in range(5)]
    print_locked()
    [print_locked(t_freq[projects[i]], end = "\t") for i in range(5)]
    print_locked()
    [print_locked(m_weighted_freq[projects[i]], end = "\t") for i in range(5)]
    print_locked()
    [print_locked(results[i][1], end = "\t") for i in range(5)]
    print_locked()

    t_budget_utilization = 0
    for item in projects:

        if(t_freq[item] > 0 and h_t_freq[item] > 0):

            t_budget_utilization += prices[items.index(item)] * min(h_t_freq[item], t_freq[item])

    m_budget_utilization = 0
    for item in projects:

        if(m_freq[item] > 0 and h_m_freq[item] > 0):

            m_budget_utilization += prices[items.index(item)] * min(h_m_freq[item], m_freq[item])

    d_t_guy_utility = 0
    for item in projects:

        if(item in h_t_guy):

            d_t_guy_utility += prices[items.index(item)]

    d_m_guy_utility = 0
    for item in projects:

        if(item in h_m_guy):

            d_m_guy_utility += prices[items.index(item)]

    print_locked("\n\nDISHONEST BUDGET UTILIZATION: ( % )\n")
    print_locked("Tourists -> Ministers\n")
    print_locked("{:.2f}".format((100 * d_t_guy_utility)/(B)), "{:.2f}".format((100 * d_m_guy_utility)/(B)))
    print_locked()

    #[print(i + 1, end=" ") for i in h_t_guy]
    #print()
    #[print(i + 1, end=" ") for i in h_m_guy]
    #print(h_t_guy, h_m_guy, sep="\n")



##  The main function   ##

#   Main    #
def main():

    #   Get volunteer number    #
    tourists, weightage = TOURISTS, WEIGHTAGE

    #   Generate statistics #
    get_stats(tourists, weightage)



##  Call the main function  ##

#   Initiation  #
if __name__=="__main__":

    try:
    
        #   Clear the terminal  #
        os.system("clear")
    
        #   Start logging to file     #        
        print_locked('\n\n\n\n{:.{align}{width}}'.format("Execution Start at: " 
            + str(datetime.datetime.now()), align='<', width=70), end="\n\n")
        
        print_locked("\n\nProgram Name:\n\n" + str(sys.argv[0].split("/")[-1]))
        
        print_locked("\n\nProgram Path:\n\n" + os.path.dirname(sys.argv[0]))
        
        print_locked("\n\nProgram Name With Path:\n\n" + str(sys.argv[0]), end="\n\n\n")
        
        #   Call the main program   #
        start = datetime.datetime.now()
        main()
        print_locked("\nProgram execution time:\t\t", datetime.datetime.now() - start, "hours\n")
        
        #   Notify completion   #
        #notify()
        
    except Exception:
    
        #   Print reason for abortion   #
        print_locked(traceback.format_exc())


##   End of Code   ##

