import pandas as pd
import os as os
import numpy as np



#installing all of these because who knows what I'll need

def looking_times_processing_OL(datavyucsv, icatcherannotations, lookitcsv, milliseconds, framecountcsvoutput,
                                millicountoutput, framecount_pivot, millicount_pivot, part_summary):
    os.chdir('c:\\Users\\ol1822a\\Documents\\CSV')  #get the right directory
    np.set_printoptions(linewidth=320)
    pd.set_option('display.width', 500)
    pd.set_option('display.max_columns', 30)
    #these three commands are to make sure it prints the whole table and doesn't wrap text, just to make it easier to visualize/inspect

    #first get the datavyu information
    handcoded = pd.read_csv(datavyucsv, usecols=['framenum', 'trials.code01', 'correction.code01'])  #make it a dataframe so I can use it
    handcoded['correction.code01'] = handcoded['correction.code01'].str.replace('l', 'left')  #replace shortened codes with long codes to make it easier to read
    handcoded['correction.code01'] = handcoded['correction.code01'].str.replace('r', 'right')
    handcoded['correction.code01'] = handcoded['correction.code01'].str.replace('a', 'away')
    handcoded.framenum.astype(int)  #change frame numbers to integers instead of strings
    #print(handcoded) #just checking it worked

    # #now get the icatcher annotation information
    annotations = pd.read_csv(icatcherannotations, usecols=['frame', 'icatcherdir'], sep=',', names=['frame', 'icatcherdir', 'confidence'])
    annotations['icatcherdir'] = annotations['icatcherdir'].str.replace('noface', 'away')
    annotations['icatcherdir'] = annotations['icatcherdir'].str.replace(' ', '')
    annotations['frame'] = annotations['frame'].astype(int)  #change frame numbers to integers instead of strings
    #print(annotations)

    # #combine datavyu and annotation information so they're in the same table
    hand_anns = handcoded.merge(annotations, left_on='framenum', right_on='frame', how='left')


    #print(hand_anns)

    # #get just the frames that are trials - calibrations do not matter
    hand_anns_frames = hand_anns[(hand_anns['trials.code01'] != 'c') & (hand_anns['trials.code01'].notnull())]  #only keep frames that are not marked with c and not empty
    hand_anns_frames['trials.code01'] = hand_anns_frames['trials.code01'].astype(int)  #change trial numbers to integers instead of strings


    #print(hand_anns_frames)

    # #now get the lookit data
    # this study uses audio and images so this loop will store pairs as a trial
    lookit = pd.read_csv(lookitcsv, usecols=['frame_id', 'key', 'value'])

    #print(lookit)

    # Filter for rows with audio or image information
    lookit = lookit[lookit['key'].isin(['audioPlayed', 'images.0.src'])].reset_index(drop=True)

    # Create empty lists to collect audio-image trial pairs
    # Create trial pairings: audio followed by image
    audio_list = []
    image_list = []

    i = 0
    while i < len(lookit) - 1:
        if lookit.iloc[i]['key'] == 'audioPlayed' and lookit.iloc[i + 1]['key'] == 'images.0.src':
            audio_list.append(lookit.iloc[i]['value'])
            image_list.append(lookit.iloc[i + 1]['value'])
            i += 2  # Move past this pair
        else:
            i += 1  # Skip malformed entry

    # Build DataFrame from valid trial pairs
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

    # Display
    #print(trials)


    # # #merge the lookit, icatcher, and datavyu info together
    hand_anns_trials = hand_anns_frames.merge(trials, how='left', left_on='trials.code01', right_on='frame_id') #merge lookit trial info with datavyu and icatcher

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(hand_anns_trials)

    #This is just to sum the number of incorrect icatcher codes, so we can use/report the number later
    hand_anns_trials['corrected'] = (hand_anns_trials['icatcherdir'] != hand_anns_trials['correction.code01']) & (hand_anns_trials['correction.code01'].notnull())
    #print(hand_anns_trials)

    # # # #now replace icatcher incorrects with datavyu corrections
    hand_anns_trials.loc[(hand_anns_trials['icatcherdir'] != hand_anns_trials['correction.code01']) & (hand_anns_trials['correction.code01'].notnull()), 'icatcherdir'] = hand_anns_trials['correction.code01']

    #print(hand_anns_trials)

    # #crop this because i don't want to save this whole table
    hand_anns_trials_cropped = hand_anns_trials.drop(['correction.code01', 'frame', 'frame_id'], axis=1)

    #print(hand_anns_trials_cropped)

    #now group hand_anns_trials so it's an easy doc to read quickly
    trial_frame_count = hand_anns_trials.groupby(['trials.code01', 'image', 'audio', 'icatcherdir']).count()
    trial_frame_count = trial_frame_count.drop(['corrected',
                                                'frame', 'frame_id'
                                                ], axis=1)

    print(trial_frame_count)  #should be a nice short spreadsheet of each trial and for how many frames the baby was looking at each picture during each trial
    print(trial_frame_count.index.get_level_values('trials.code01').unique())
    trial_milliseconds = trial_frame_count['framenum'].multiply(milliseconds)  #multiply frame count by number of milliseconds to get timing information


    #print(trial_milliseconds)  #should be same as trial_frame_count but just in milliseconds

    # #now pivot the tables because they might be easier to work with this way
    frames_pivot = trial_frame_count.pivot_table('framenum', index=['image', 'audio', 'trials.code01'], columns='icatcherdir', aggfunc='sum')
    #print(frames_pivot)

    milliseconds_pivot = frames_pivot.reindex(columns=['away', 'left', 'right'], fill_value=0).multiply(milliseconds)


    print(milliseconds_pivot)

    # now just save the tables to your computer :)
    hand_anns_trials_cropped.to_csv(part_summary)  # makes a summary sheet with each frame, the picture on the left and right, where the baby was looking, and if iCatcher was corrected
    trial_frame_count.to_csv(framecountcsvoutput)  # these are the unpivoted versions
    trial_milliseconds.to_csv(millicountoutput)
    frames_pivot.to_csv(framecount_pivot)  # these are the pivoted versions
    milliseconds_pivot.to_csv(millicount_pivot)


#change these to match whatever baby you're working with - for first coder
participants = [(106, 33.5)]  # list and for look so that you can do this stuff to multiple particpants at once first number is participant number, second is MPF
for i, x in participants:
    datavyucsv = f'{i}_framebyframe.csv'
    icatcherannotations = f'{i}.txt'
    lookitcsv = f'{i}_lookit.csv'
    milliseconds = x
    framecountcsvoutput = f'{i}_frame_count.csv'
    millicountoutput = f'{i}_milliseconds.csv'
    framecount_pivot = f'{i}_frame_pivot.csv'
    millicount_pivot = f'{i}_milli_pivot.csv'
    part_summary = f'{i}_summary.csv'
looking_times_processing_OL(datavyucsv, icatcherannotations, lookitcsv, milliseconds, framecountcsvoutput,
                            millicountoutput, framecount_pivot, millicount_pivot, part_summary)

#change these to match whatever baby you're working with - for second-coder
#participants =  [(1)] # list and for loop so that you can do this stuff to multiple particpants at once
#for 1,33.97 in participants:
#   datavyucsv = f'0{i}_framebyframe_2.csv'
#  icatcherannotations = f'0{i}.txt'
# lookitcsv = f'0{i}_lookit.csv'
#milliseconds = x
#framecountcsvoutput = f'0{i}_frame_count_2.csv'
#millicountoutput = f'0{i}_milliseconds_2.csv'
#framecount_pivot = f'0{i}_frame_pivot_2.csv'
#millicount_pivot = f'0{i}_milli_pivot_2.csv'
#part_summary = f'0{i}_summary_2.csv'
#looking_times_processing_OL(datavyucsv, icatcherannotations, lookitcsv, milliseconds, framecountcsvoutput,
# millicountoutput, framecount_pivot, millicount_pivot, part_summary)
