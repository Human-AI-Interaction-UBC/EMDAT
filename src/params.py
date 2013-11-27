"""
UBC Eye Movement Data Analysis Toolkit

Module that contains all global parameters. Values of parameters are specific to the project.

Author: skardan

"""
DIR = "C:/Users/bondaria/Documents/UAI/GENOVA/PupilDilation/src/"
#EYELOGDATAFOLDER = "./sampledata"
EYELOGDATAFOLDER = DIR + "sampledata"
# the folder that has the files exported from Tobii

#EXTERNALLOGDATAFOLDER = "./sampledata/external logs"
EXTERNALLOGDATAFOLDER = DIR + "sampledata/external logs"
# the folder that has the external log files

NUMBEROFEXTRAHEADERLINES = 8 
#number of extra lines at the beginning of the files exported from Tobii 
#this is specific to study and is based on the number of variables defined in Tobii
# studio for the experiment

FIXATIONHEADERLINES = 19
#number of lines at the beginning of the 'Fixation-Data' files exported from Tobii before 
#the actual data 

ALLDATAHEADERLINES = 26
#number of lines at the beginning of the 'All-Data' files exported from Tobii before 
#the actual data 

EVENTSHEADERLINES = 19
#number of lines at the beginning of the 'Event-Data' files exported from Tobii before 
#the actual data 

ACTIONHEADERLINES = 0
#number of lines at the beginning of the external log files before the actual data 

MEDIA_OFFSET = (0, 0)   
# the coordinates of the top left corner of the window
# showing the interface under study. (0,0) if the interface was
# in full screen (default value)

featurelist = ['numsegments','length','numfixations','fixationrate','meanabspathangles',
               'meanfixationduration','meanpathdistance','meanrelpathangles','stddevabspathangles',
               'stddevfixationduration','stddevpathdistance','stddevrelpathangles']#'numsamples','sumabspathangles','sumfixationduration','sumpathdistance','sumrelpathangles']
                #'meanpupilsize', 'stddevpupilsize', 'maxpupilsize', 'minpupilsize', 'startpupilsize','endpupilsize'
#add pupil dilation 
featurelist.extend(['meanpupilsize', 'stddevpupilsize', 'maxpupilsize', 'minpupilsize', 'startpupilsize','endpupilsize'])
# list of non-AOI feature names 

aoigeneralfeat = ['fixationrate','numfixations','totaltimespent','proportionnum',
                  'proportiontime','longestfixation']#'timetofirstfixation','timetolastfixation',
#list of general AOI features

aoinames = ['Top','Bottom','Graph','Toolbar','Test']
#list of the AOI names

aoitransfrom = map(lambda x:'numtransfrom_'+x, aoinames) 
#['numtransfromBottom','numtransfromGraph','numtransfromToolbar','numtransfromTop']
#list of transition-based AOI features

#aoitransto = ['numtranstoBottom','numtranstoGraph','numtranstoToolbar','numtranstoTop']


aoiproportion = map(lambda x:'proptransfrom_'+x, aoinames) 
#['proptransfromBottom','proptransfromGraph','proptransfromToolbar','proptransfromTop']
#list of transition-based AOI features

##,'_proptransto_Bottom','_proptransto_Graph','_proptransto_Toolbar','_proptransto_Top']



#generating a list of all AOI-based features
aoifeaturelist =[]
for aoin in aoinames:
    aoifeaturelist.extend(map(lambda x:aoin+'_'+x, aoigeneralfeat))
    aoifeaturelist.extend(map(lambda x:aoin+'_'+x, aoitransfrom))
    #aoifeaturelist.extend(map(lambda x:aoin+x, aoitransto))
    aoifeaturelist.extend(map(lambda x:aoin+'_'+x, aoiproportion))
    

# Validity Threshold for segments
VALID_PROP_THRESH = 0.85
#the minimum proportion of valid samples for a Segment or Scene to be considered valid

VALID_TIME_THRESH = 3000
#the maximum gap size (ms) allowable in samples for a Segment or Scene to be considered valid

MAX_SEG_TIMEGAP = 300 #maximum gap size (ms) allowable in a segment with auto-partition option
"""
Auto-partition option is when EMDAT automatically splits the "Segment"s which have low sample 
quality, into two new sub "Segment"s discarding the largest gap of invalid samples for 
a "Segment". EMDAT will continue to perform the splitting on the Segments until there is not
any gap larger than MAX_SEG_TIMEGAP left in the data.
"""

VALIDITY_METHOD = 3 #1: porportion; 2:time gap; 3: porportion with (valid + restored) samples
"""
Methods 1 and 3 use VALID_PROP_THRESH and method 2 uses VALID_TIME_THRESH as validity threshold
 
Restored samples are the samples which are not valid but they are part of a Fixation.
The idea is that if the user was looking at a certain point and then we loose the eye data for 
a short period of time and afterwards the user is looking at the same point we can assume that user
was looking at that same point during that period. 
"""

MINSEGSIZE = 300 #minimum segment size in ms that is considered meaningful for this experiment

INCLUDE_HALF_FIXATIONS = False
#A boolean value determining if a Fixation extends between two consecutive Segments, should it be 
#included in those Segments or not

DEBUG = False
#DEBUG = True
#Enable/disable verbose mode which prints out more information for debugging purposes

#Predefined lists of features that are not calculated using time
NONTEMP_FEATURES_SEG = ['meanfixationduration', 'stddevfixationduration',
'fixationrate', 'meanpathdistance', 'stddevpathdistance', 'meanabspathangles', 'stddevabspathangles',
'meanrelpathangles', 'stddevabspathangles'] 

NONTEMP_FEATURES_AOI = ['longestfixation', 'proportionnum', 'proportiontime',
'proptransto', 'proptransfrom']

""" list of features related based on pupil dilation """
NONTEMP_FEATUES_PUPIL = ['meanpupilsize', 'stddevpupilsize', 'maxpupilsize', 'minpupilsize', 'startpupilsize','endpupilsize']
