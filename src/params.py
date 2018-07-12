"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3

Module that contains all global parameters. Values of parameters are specific to the project.

@author: Samad Kardan (creator), Sebastien Lalle
Institution: The University of British Columbia.
"""


# ####################### Eye tracker type and path ##############################################################

# the folder that has the files exported from eye trackers
EYELOGDATAFOLDER = "./sampledata"

# the folder that has the external log files
EXTERNALLOGDATAFOLDER = "./sampledata/external logs"

# the eye tracker and/or software used to collect and export the data
#EYETRACKERTYPE = "TobiiV2" #Tobii Studio version 1x and 2x
EYETRACKERTYPE = "TobiiV3" #Tobii Studio version 3x
#EYETRACKERTYPE = "SMI" # SMI/BeGaze


# ####################### Eye tracker specific parameters ##############################################################

# number of extra lines at the beginning of the files exported from Tobii
# this is specific to study and is based on the number of variables defined in Tobii studio for the experiment
NUMBEROFEXTRAHEADERLINES = 8

# number of lines at the beginning of the 'Fixation-Data' files exported from Tobii before the actual data
FIXATIONHEADERLINES = 19

# number of lines at the beginning of the 'All-Data' files exported from Tobii before the actual data
ALLDATAHEADERLINES = 26

# number of lines at the beginning of the 'Event-Data' files exported from Tobii before the actual data
EVENTSHEADERLINES = 27

# number of lines at the beginning of the external log files before the actual data
ACTIONHEADERLINES = 0

# ### SMI-specific parameters
# the line number of the first data row in Events file
EVENTS_FIRST_DATA_LINE = 22

# the line number of the row that contains the table header for fixations
FIXATION_HEADER_LINE = 11

# the line number of the row that contains the table header for fixations
SACCADE_HEADER_LINE = 14

# the line number of the row that contains the table header for user events
USER_EVENT_HEADER_LINE = 20

# the line number of the first data row in Raw file
RAW_HEADER_LINE = 1

#L or R for using left/right eye event when averaging both eyes measures is not possible
MONOCULAR_EYE = "L"



# ####################### Features generation ##############################################################

# the coordinates of the top left corner of the window showing the interface under study.
# (0,0) if the interface was in full screen (default value).
MEDIA_OFFSET = (0, 0)


#Overall gaze features to generate and export
featurelist = ['numsegments','length','numsamples','numfixations','fixationrate','meanabspathangles',
               'meanfixationduration','meanpathdistance','meanrelpathangles','stddevabspathangles',
               'stddevfixationduration','stddevpathdistance','stddevrelpathangles',
			   'eyemovementvelocity', 'abspathanglesrate', 'relpathanglesrate',
			   'sumabspathangles','sumfixationduration','sumpathdistance','sumrelpathangles']

# Blink features to generate and export
featurelist.extend(['blinknum', 'blinkdurationtotal', 'blinkdurationmean', 'blinkdurationstd', 'blinkdurationmin',
                    'blinkdurationmax', 'blinkrate', 'blinktimedistancemean', 'blinktimedistancestd',
                    'blinktimedistancemax', 'blinktimedistancemin'])

# Pupil features to generate and export
featurelist.extend(['meanpupilsize', 'stddevpupilsize', 'maxpupilsize', 'minpupilsize', 'startpupilsize','endpupilsize',
               'meanpupilvelocity', 'stddevpupilvelocity', 'maxpupilvelocity', 'minpupilvelocity'])

# Head distance features to generate and export
featurelist.extend(['meandistance', 'stddevdistance', 'maxdistance', 'mindistance', 'startdistance', 'enddistance'])

# Saccade features to generate and export
featurelist.extend(['numsaccades', 'sumsaccadedistance', 'meansaccadedistance', 'stddevsaccadedistance', 'longestsaccadedistance',
               'sumsaccadeduration','meansaccadeduration', 'stddevsaccadeduration', 'longestsaccadeduration',
               'meansaccadespeed', 'stddevsaccadespeed','minsaccadespeed', 'maxsaccadespeed',
			   'fixationsaccadetimeratio'])

# Events features to generate and export
featurelist.extend(['numevents', 'numleftclic', 'numrightclic', 'numdoubleclic', 'numkeypressed', 'leftclicrate', 'rightclicrate', 'doubleclicrate', 'keypressedrate',
               'timetofirstleftclic', 'timetofirstrightclic', 'timetofirstdoubleclic', 'timetofirstkeypressed'])

# Generate AOI-sequence
aoisequencefeat = ['aoisequence']

# AOI features to generate and export
aoigeneralfeat = ['fixationrate','numfixations','totaltimespent','proportionnum',
                  'proportiontime','longestfixation', 'meanfixationduration', 'stddevfixationduration', 'timetofirstfixation','timetolastfixation',
				  'numevents', 'numleftclic', 'numrightclic', 'numdoubleclic', 'leftclicrate', 'rightclicrate', 'doubleclicrate',
                  'timetofirstleftclic', 'timetofirstrightclic', 'timetofirstdoubleclic', 'timetolastleftclic', 'timetolastrightclic', 'timetolastdoubleclic']

# Pupil features to generate and export
aoigeneralfeat.extend(['meanpupilsize', 'stddevpupilsize', 'maxpupilsize', 'minpupilsize', 'startpupilsize','endpupilsize',
               'meanpupilvelocity', 'stddevpupilvelocity', 'maxpupilvelocity', 'minpupilvelocity'])

# Head distance for AIO features to generate and export
aoigeneralfeat.extend(['meandistance', 'stddevdistance', 'maxdistance', 'mindistance', 'startdistance', 'enddistance'])

#list of the AOI names
aoinames = ['Top','Bottom','Graph','Toolbar']

#list of transition-based AOI features (count)
aoitransfrom = map(lambda x:'numtransfrom_'+x, aoinames)

#list of transition-based AOI features (proportion)
aoiproportion = map(lambda x:'proptransfrom_'+x, aoinames)

# lower and  upper bound on size of invalid data gaps to be treated as blinks
blink_threshold = (100, 300)

# Generating a list of all AOI-based features (including transitions)
aoifeaturelist =[]
for aoin in aoinames:
    aoifeaturelist.extend(map(lambda x:aoin+'_'+x, aoigeneralfeat))
    aoifeaturelist.extend(map(lambda x:aoin+'_'+x, aoitransfrom))
    aoifeaturelist.extend(map(lambda x:aoin+'_'+x, aoiproportion))


# ####################### Data processing, restoration and validation ##############################################################

"""
Validity method to control for data quality:
 1 = Proportion of valid gaze samples
 2 = No gap size abvoe a given threshold
 3 =  Proportion of valid gaze samples (including restored samples, see below)

Methods 1 and 3 use VALID_PROP_THRESH and method 2 uses VALID_TIME_THRESH as validity threshold

Restored samples are the samples which are not valid but they are part of a Fixation.
The idea is that if the user was looking at a certain point and then we loose the eye data for
a short period of time and afterwards the user is looking at the same point we can assume that user
was looking at that same point during that period.
"""
VALIDITY_METHOD = 3

# Validity Threshold for segments (the minimum proportion of valid samples for a Segment or Scene to be considered valid)
VALID_PROP_THRESH = 0.8

#the maximum gap size (ms) allowable in samples for a Segment or Scene to be considered valid
VALID_TIME_THRESH = 3000


"""
Maximum gap size (ms) allowable in a segment with auto-partition option

Auto-partition option is when EMDAT automatically splits the "Segment"s which have low sample
quality, into two new sub "Segment"s discarding the largest gap of invalid samples for
a "Segment". EMDAT will continue to perform the splitting on the Segments until there is not
any gap larger than MAX_SEG_TIMEGAP left in the data.
"""
MAX_SEG_TIMEGAP = 10


#proportion of valid gaze samples required per saccade. If less than 1, missing gaze sample will be extrapolated.
VALID_SAMPLES_PROP_SACCADE = 1

#minimum segment size in ms that is considered meaningful for this experiment
MINSEGSIZE = 0

#A boolean value determining if a Fixation extends between two consecutive Segments, should it be
#included in those Segments or not
INCLUDE_HALF_FIXATIONS = False

#Pupil adjustment to minimize the pupil size differences among individual users, if Rest Pupil Size (RPS) is provided. Possible values:
#PUPIL_ADJUSTMENT = None 		#no adjustment;
PUPIL_ADJUSTMENT = "rpscenter"	#Rps-centering (substraction of the rps from the raw pupil size)
#PUPIL_ADJUSTMENT = "PCPS" 		#Normalization of pupil size based on the rsp following [Iqbal et al., 2005, doi>10.1145/1054972.1055016]


# ####################### Verbose/Debug mode ##############################################################

#Enable/disable debug mode. In debug mode warnings are treated as errors, and the verbosity level is automatically set to "VERBOSE" (see below)
#DEBUG = True
DEBUG = True

#Verbosity level
#VERBOSE = "QUIET"		#prints nothing except errors and warnings
VERBOSE = "NORMAL"		#prints essential information
#VERBOSE = "VERBOSE"	#prints information useful for debugging
