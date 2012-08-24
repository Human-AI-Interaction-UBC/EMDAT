'''
UBC Eye Movement Data Analysis Toolkit

$$$Daria: Module that contains all global parameters. Values of parameters are specific to the project.

Author: skardan

'''
EXPERIMENT ='CSP'
#a work around for having multiple experiments in one params file
if EXPERIMENT == 'CSP':
    EYELOGDATAFOLDER = "./sampledata"
    # the folder that has the files exported from Tobii
    
    EXTERNALLOGDATAFOLDER = "./sampledata/external logs"
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
    # list of non-AOI feature names 
    
    aoigeneralfeat = ['_fixationrate','_numfixations','_totaltimespent','_proportionnum',
                      '_proportiontime','_longestfixation']#'_timetofirstfixation','_timetolastfixation',
    #list of general AOI features
    
    aoitransfrom = ['_numtransfrom_Bottom','_numtransfrom_Graph','_numtransfrom_Toolbar',
                    '_numtransfrom_Top']
    #list of transition-based AOI features
    
    #aoitransto = ['_numtransto_Bottom','_numtransto_Graph','_numtransto_Toolbar','_numtransto_Top']
    
    
    aoiproportion = ['_proptransfrom_Bottom','_proptransfrom_Graph','_proptransfrom_Toolbar',
                     '_proptransfrom_Top']
    #list of transition-based AOI features
    
    ##,'_proptransto_Bottom','_proptransto_Graph','_proptransto_Toolbar','_proptransto_Top']
    
    aoinames = ['Top','Bottom','Graph','Toolbar']
    #list of the AOI names
    
    #generating a list of all AOI-based features
    aoifeaturelist =[]
    for aoin in aoinames:
        aoifeaturelist.extend(map(lambda x:aoin+x, aoigeneralfeat))
        aoifeaturelist.extend(map(lambda x:aoin+x, aoitransfrom))
        #aoifeaturelist.extend(map(lambda x:aoin+x, aoitransto))
        aoifeaturelist.extend(map(lambda x:aoin+x, aoiproportion))
        


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
    #if a Fixation extends between two consecutive Segments, should it be included in those 
    #Segments or not
    
    DEBUG = False
    #DEBUG = True
    #Enable/disable verbose mode which prints out more information for debugging purposes
    
    

    #Predefined feature lists
    
    NONTEMP_FEATURES_SEG = ['meanfixationduration', 'stddevfixationduration',
    'fixationrate', 'meanpathdistance', 'stddevpathdistance', 'meanabspathangles', 'stddevabspathangles',
    'meanrelpathangles', 'stddevabspathangles'] 
    
    NONTEMP_FEATURES_AOI = ['longestfixation', 'proportionnum', 'proportiontime',
    'proptransto', 'proptransfrom']
    
    
    # Constants specific to AIspace CSP project
    NUMBEROFPROBLEMS = 2
    ACTIIONS = [1,2,3,4,5,6,7,8,9,10,11,12,13]
    
elif EXPERIMENT == 'PC':  #Prime Climb experiment
    NUMBEROFEXTRAHEADERLINES = 0 #specific to study
    
    FIXATIONHEADERLINES = 19
    ALLDATAHEADERLINES = 24
    EVENTSHEADERLINES = 17
    
    ACTIONHEADERLINES = 0
    MEDIA_OFFSET = (0, 0) #for rest (0,0) 
    #MEDIA_OFFSET = (-21,-97) # for subject 8-12
    #MEDIA_OFFSET = (-171, -104) #For subject 7
    
    # Validity Threshold for segments
    VALID_PROP_THRESH = 0.75 #(as we want to include 75%, then you need to have it one less)
    VALID_TIME_THRESH = 3000
    MAX_SEG_TIMEGAP = 300 #maximum gap size (ms) allowable in a segment with auto-partition option
    VALIDITY_METHOD = 3 #1: porportion; 2:time gap; 3: fixation based porportion
    
    MINSEGSIZE = 300 #minimum segment size in ms
    
    INCLUDE_HALF_FIXATIONS = True
    
    DEBUG = False
    
    featurelist = ['length','numfixations','fixationrate','meanabspathangles','meanfixationduration',
                   'meanpathdistance','meanrelpathangles','stddevabspathangles','stddevfixationduration',
                   'stddevpathdistance','stddevrelpathangles','numsamples','sumabspathangles',
                   'sumfixationduration','sumpathdistance','sumrelpathangles']
    aoigeneralfeat = ['_fixationrate','_numfixations','_totaltimespent','_proportionnum',
                      '_proportiontime','_longestfixation','_timetofirstfixation','_timetolastfixation']
    
    NONTEMP_FEATURES_AOI = ['longestfixation', 'proportionnum', 'proportiontime',
                            'proptransto', 'proptransfrom']
    NONTEMP_FEATURES_SEG = ['meanfixationduration', 'stddevfixationduration', 'fixationrate', 
                            'meanpathdistance', 'stddevpathdistance', 'meanabspathangles', 
                            'stddevabspathangles','meanrelpathangles', 'stddevabspathangles'] 
    
    aoitransfrom = ['_numtransfrom_Tool','_numtransfrom_Hint','_numtransfrom_HintClose','_numtransfrom_Mountain']
    aoitransto = ['_numtransto_Tool','_numtransto_Hint','_numtransto_HintClose','_numtransto_Mountain']
    aoiproportion = ['_proptransfrom_Tool','_proptransfrom_Hint','_proptransfrom_HintClose','_proptransfrom_Mountain',
                     '_proptransto_Tool','_proptransto_Hint','_proptransto_HintClose','_proptransto_Mountain']
    aoinames = ['Tool','Hint','HintClose','Mountain']
    aoifeaturelist =[]
    for aoin in aoinames:
        aoifeaturelist.extend(map(lambda x:aoin+x, aoigeneralfeat))
        aoifeaturelist.extend(map(lambda x:aoin+x, aoitransfrom))
        aoifeaturelist.extend(map(lambda x:aoin+x, aoitransto))
        aoifeaturelist.extend(map(lambda x:aoin+x, aoiproportion))
