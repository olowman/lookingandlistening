These files are used to process looking times using iCatcher, Datavyu, and Lookit outputs.

Each script is marked in order of use

If specific trials need to be manually excluded use step 3 processing_for_pausing

summary stats uses final outputs to give included trial information. 

Step 1: Pivots

Inputs iCatcher .txt file, Datavyu frame .csv, and Lookit frame .csv. Pivots information to determine looking times left, right, or away. This is based on frame rate from the video.

Step 2: Combine Files

Combines all pivot files into one large file

Step 3: Left right processing

Calculates time looking towards target object based on image file name and coded looking direction.

Step 4: Exclude Trials

Excludes trials based on side bias or amount of looking time.

Summary stats gives number of included trials per participant. 

# lookingandlistening
