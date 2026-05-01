import numpy as np
import matplotlib as mplt
import pandas as pd
import math as m
import os as os
import inspect
def retrieve_variable_name(value):
    for var, val in inspect.currentframe().f_back.f_locals.items():
        if val is value:
            return var

#FOR EXCLUDE VS INCLUDE
path = 'c:\\Users\\ol1822a\\Documents\\pivots'
os.chdir(path) #right directory
np.set_printoptions(linewidth=320)
pd.set_option('display.width', 500)
pd.set_option('display.max_columns',30)

include = [] # will eventually list the participants we can include
exclude = [] # will eventually list the participants we need to exclude
total_trials = 0 # initiate

for filename in os.listdir(): #for loop to do one file at a time
    full_path = path+'\\'+filename
    # print(filename)
    if os.path.isdir(full_path) or filename =='Thumbs.db' or filename=='.DS_Store':
        continue # skips over anything that is not a .csv file
    data = pd.read_csv(filename)
    # print(data) #just checking
    data_notnull = data.fillna(0) #change nulls to 0 so you can calculate correct averages
    # print(data_notnull)
    # averages = data_notnull[['away','left','right']].mean() # gives average time looking away, left, and right for each baby
    # print(averages)
    # stats = data_notnull[['away','left','right']].describe() # describes some of the looking time info for each baby
    # print(stats)
    data_notnull['include?'] = ((data_notnull['left'] + data_notnull['right'] >= 1000)) # marks trials as included or not based on inclusion criteria
    print(data_notnull)
    var_name = str(filename[:3]) # shortens the name of the file to make it easier to read
    print(f'{var_name}:', '\n', data_notnull['include?'].value_counts()) # lists how many trials are included and excluded
    if data_notnull['include?'].value_counts()[True] >= 12: # if the baby has at least 12 valid trials
        include.append(var_name) # include them in the included list
        total_trials += data_notnull['include?'].value_counts()[True] # add their trials to the number of included trials
    else:
        exclude.append(var_name) #otherwise add them to the excluded list

#print all this info out nice and easy for you to read :)
print(f'include: {include}')
print(f'exclude: {exclude}')
print(f'Total included babies: {len(include)}')
print(f'Total included trials : {total_trials}')
print(f'Average trial per included babies: {total_trials / len(include)}')



# FOR ICATCHER CALCs
# path = 'J:\\Bayet Lab\\Projects\\Consortium\\Lookit Differential Looking Times\\Processed\\Summaries'
# os.chdir(path) # right directory
#
# all_frames = 0 #initialize variables
# icatcher_replacements = 0
# total_left = 0
# total_right = 0
# total_away = 0
#
#
# for filename in os.listdir(): #for loop to do one file at a time
#     full_path = path+'\\'+filename
#     if os.path.isdir(full_path) or filename =='Thumbs.db' or filename=='.DS_Store':
#         continue #skips anything that is not a .csv file
#     data = pd.read_csv(filename)
#     frames = len(data.index) # gets number of frames
#     all_frames += frames
#     icatcher = data['corrected'].value_counts()[True] # gets number of frames where we had to manually correct iCatcher
#     icatcher_replacements += icatcher
#     left = data['icatcherdir'].value_counts()['left'] # gets number of frames where baby was looking left
#     total_left += left
#     right = data['icatcherdir'].value_counts()['right'] # gets number of frames where baby was looking right
#     total_right += right
#     away = data['icatcherdir'].value_counts()['away'] # gets number of frames where baby was looking away
#     total_away += away
#
# #print all this info out nice and easy for you to read :)
# print(f'Total number of frames: {all_frames}')
# print(f'Total iCatcher frames that had to be replaced: {icatcher_replacements}')
# print(f'Total frames looking away: {total_away}')
# print(f'Total frames looking left: {total_left}')
# print(f'Total frames looking right: {total_right}')

