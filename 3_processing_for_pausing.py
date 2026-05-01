import numpy as np
import matplotlib as mplt
import pandas as pd
import math as m
import os as os
#installing all of these because who knows what I'll need

def looking_times_processing(datavyucsv, icatcherannotations, lookitcsv, milliseconds, framecountcsvoutput, millicountoutput, framecount_pivot, millicount_pivot, part_summary):
    os.chdir('c:\\Users\\ol1822a\\Documents\\CSV') #get the right directory
    np.set_printoptions(linewidth=320)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_columns',30) #these three commands are to make sure it prints the whole table and doesn't wrap text, just to make it easier to visualize/inspect
    #first get the datavyu information
    handcoded = pd.read_csv(datavyucsv, usecols=['framenum', 'trials.code01', 'correction.code01']) #make it a dataframe so I can use it
    handcoded['correction.code01'] = handcoded['correction.code01'].str.replace('l', 'left') #replace shortened codes with long codes to make it easier to read
    handcoded['correction.code01'] = handcoded['correction.code01'].str.replace('r', 'right')
    handcoded['correction.code01'] = handcoded['correction.code01'].str.replace('a', 'away')
    handcoded.framenum.astype(int) #change frame numbers to integers instead of strings
    # print(handcoded) #just checking it worked

    # #now get the icatcher annotation information
    annotations = pd.read_csv(icatcherannotations, usecols=['frame', 'icatcherdir'], sep=',', names=['frame', 'icatcherdir', 'confidence'])
    annotations['icatcherdir'] = annotations['icatcherdir'].str.replace('noface', 'away')
    annotations['icatcherdir'] = annotations['icatcherdir'].str.replace(' ', '')
    annotations['frame'] = annotations['frame'].astype(int) #change frame numbers to integers instead of strings
    # print(annotations)

    # #combine datacyu and annotation information so they're in the same table
    hand_anns = handcoded.merge(annotations, left_on='framenum', right_on='frame', how='left')
    # # # print(hand_anns)

    # # #get just the frames that are trials - calibrations do not matter
    hand_anns_frames = hand_anns[(hand_anns['trials.code01'] != 'c') & (hand_anns['trials.code01'].notnull())] #only keep frames that are not marked with c and not empty
    hand_anns_frames['trials.code01'] = hand_anns_frames['trials.code01'].astype(int) #change trial numbers to integers instead of strings
    # print(hand_anns_frames)

    # # #now get the lookit data
    lookit = pd.read_csv(lookitcsv, usecols=['frame_id', 'key', 'value'])

    # Filter for rows with audio or image information
    lookit = lookit[lookit['key'].isin(['audioPlayed', 'images.0.src'])].reset_index(drop=True)

    # Create empty lists to collect audio-image trial pairs
    audio_list = []
    image_list = []

    # Track the current state
    current_audio = None

    # Loop through rows and pair each audio with the next image
    for _, row in lookit.iterrows():
        if row['key'] == 'audioPlayed':
            current_audio = row['value']  # Store the audio file
        elif row['key'] == 'images.0.src' and current_audio is not None:
            audio_list.append(current_audio)
            image_list.append(row['value'])
            current_audio = None  # Reset to prepare for next pair

    # Create a clean DataFrame of trials
    trials = pd.DataFrame({
        'frame_id': range(1, len(audio_list) + 1),
        'audio': audio_list,
        'image': image_list
    })

    # Clean up audio/image strings for readability (optional)
    trials['audio'] = trials['audio'].str.replace('https://raw.githubusercontent.com/olowman/lookit-stimuli-template/master/mp3/', '', regex=False)
    trials['audio'] = trials['audio'].str.replace('.mp3', '', regex=False)
    trials['image'] = trials['image'].str.replace(
        'https://raw.githubusercontent.com/olowman/lookit-stimuli-template/master/img/', '', regex=False)
    trials['image'] = trials['image'].str.replace('.png', '', regex=False)

    # #separate out by side so that I can pair the same trials together instead of accidentally doubling
    #trials_left = trials[trials['key'] == 'left']
    #trials_right = trials[trials['key'] == 'right']
    # # # print(trials_left)
    # # # print(trials_right)
    #trials_merge = trials_left.merge(trials_right, on='frame_id', suffixes=('_left', '_right'))
    # # # print(trials_merge)

    # # #merge the lookit, icatcher, and datavyu info together
    hand_anns_trials = hand_anns_frames.merge(trials, how='left', left_on='trials.code01', right_on='frame_id') #merge lookit trial info with datavyu and icatcher
    print(hand_anns_trials)

    #This is just to sum the number of incorrect icatcher codes, so we can use/report the number later
    hand_anns_trials['corrected'] = (hand_anns_trials['icatcherdir'] != hand_anns_trials['correction.code01']) & (hand_anns_trials['correction.code01'].notnull())
    #print(hand_anns_trials)

    # # # #now replace icatcher incorrects with datavyu corrections
    hand_anns_trials.loc[(hand_anns_trials['icatcherdir'] != hand_anns_trials['correction.code01']) & (hand_anns_trials['correction.code01'].notnull()), 'icatcherdir'] = hand_anns_trials['correction.code01']
    #print(hand_anns_trials)

    # #crop this because i don't want to save this whole table
    hand_anns_trials_cropped = hand_anns_trials.drop(['correction.code01', 'frame', 'frame_id', 'audio', 'image'], axis=1)
    print(hand_anns_trials_cropped)

    # now group hand_anns_trials so it's an easy doc to read quickly
    trial_frame_count = hand_anns_trials.groupby(['trials.code01', 'image', 'audio', 'icatcherdir']).count()
    trial_frame_count = trial_frame_count.drop(['corrected',
                                                'frame', 'frame_id'
                                                ], axis=1)
    # print(trial_frame_count) #should be a nice short spreadsheet of each trial and for how many frames the baby was looking at each picture during each trial
    print(trial_frame_count.index.names)
    print(trial_frame_count.index.get_level_values('trials.code01').unique())
    # # # THIS SECTION IS FOR EXCLUDING ENTIRE TRIALS MANUALLY; you can leave it out if you do not want to exclude any trials manually
    trial_frame_count.reset_index(inplace=True) #fixes index so that you can use trial number as index
    trials_to_exclude = [23] #change to the trials you want to exclude
    trial_frame_count.loc[trial_frame_count['trials.code01'].isin(trials_to_exclude), 'framenum'] = 0 #changes all numbers in excluded trials to 0 so that these trials will automatically be excluded in summary stats
    print(trial_frame_count) #double check that things have been removed

    trial_milliseconds = trial_frame_count['framenum'].multiply(milliseconds) # multiply frame count by number of milliseconds to get timing information
    print(trial_milliseconds) # should be same as trial_frame_count but just in milliseconds

    # #now pivot the tables because they might be easier to work with this way
    frames_pivot = trial_frame_count.pivot_table('framenum', index=['image', 'audio', 'trials.code01'], columns='icatcherdir', aggfunc='sum')
    print(frames_pivot)
    milliseconds_pivot = frames_pivot[['away', 'left', 'right']].multiply(milliseconds)
    print(milliseconds_pivot)

    # now just save the tables to your computer :)
    hand_anns_trials_cropped.to_csv(part_summary) #makes a summary sheet with each frame, the picture on the left and right, where the baby was looking, and if iCatcher was corrected
    trial_frame_count.to_csv(framecountcsvoutput) # these are the unpivoted versions, can change them to be the pivoted versions or make new csvs for pivoted
    trial_milliseconds.to_csv(millicountoutput)
    frames_pivot.to_csv(framecount_pivot) # these are the pivoted versions
    milliseconds_pivot.to_csv(millicount_pivot)



# change these to match whatever baby you're working with - for first coder
participants =  [(105, 33.34)] # list and for loop so that you can do this stuff to multiple particpants at once
for i,x in participants:
    datavyucsv = f'{i}_framebyframe.csv'
    icatcherannotations = f'{i}.txt'
    lookitcsv = f'{i}_lookit.csv'
    milliseconds = x
    framecountcsvoutput = f'{i}_frame_count.csv'
    millicountoutput = f'{i}_milliseconds.csv'
    framecount_pivot = f'{i}_frame_pivot.csv'
    millicount_pivot = f'{i}_milli_pivot.csv'
    part_summary = f'{i}_summary.csv'
    looking_times_processing(datavyucsv, icatcherannotations, lookitcsv, milliseconds, framecountcsvoutput, millicountoutput, framecount_pivot, millicount_pivot, part_summary)


# #change these to match whatever baby you're working with - for second-coder
# participants =  [(19, 33.5)] # list and for loop so that you can do this stuff to multiple particpants at once
# for i,x in participants:
#     datavyucsv = f'0{i}_framebyframe_2.csv'
#     icatcherannotations = f'0{i}.txt'
#     lookitcsv = f'0{i}_lookit.csv'
#     milliseconds = x
#     framecountcsvoutput = f'0{i}_frame_count_2.csv'
#     millicountoutput = f'0{i}_milliseconds_2.csv'
#     framecount_pivot = f'0{i}_frame_pivot_2.csv'
#     millicount_pivot = f'0{i}_milli_pivot_2.csv'
#     part_summary = f'0{i}_summary_2.csv'
#     looking_times_processing(datavyucsv, icatcherannotations, lookitcsv, milliseconds, framecountcsvoutput, millicountoutput, framecount_pivot, millicount_pivot, part_summary)