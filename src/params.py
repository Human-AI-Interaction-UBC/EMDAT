'''
Created on 2011-09-22

@author: skardan
'''
EXPERIMENT ='CSP'
if EXPERIMENT == 'CSP':
    EYELOGDATAFOLDER = "./sampledata"
    EXTERNALLOGDATAFOLDER = "./sampledata/external logs"

    NUMBEROFPROBLEMS = 2
    
    NUMBEROFEXTRAHEADERLINES = 8 #specific to study
    
    FIXATIONHEADERLINES = 19
    ALLDATAHEADERLINES = 26
    EVENTSHEADERLINES = 19
    
    ACTIONHEADERLINES = 0
    MEDIA_OFFSET = (0, 0)
    
    featurelist = ['numsegments','length','numfixations','fixationrate','meanabspathangles','meanfixationduration','meanpathdistance','meanrelpathangles','stddevabspathangles','stddevfixationduration','stddevpathdistance','stddevrelpathangles']#'numsamples','sumabspathangles','sumfixationduration','sumpathdistance','sumrelpathangles']
    aoigeneralfeat = ['_fixationrate','_numfixations','_totaltimespent','_proportionnum','_proportiontime','_longestfixation']#'_timetofirstfixation','_timetolastfixation',
    aoitransfrom = ['_numtransfrom_Bottom','_numtransfrom_Graph','_numtransfrom_Toolbar','_numtransfrom_Top']
    #aoitransto = ['_numtransto_Bottom','_numtransto_Graph','_numtransto_Toolbar','_numtransto_Top']
    aoiproportion = ['_proptransfrom_Bottom','_proptransfrom_Graph','_proptransfrom_Toolbar','_proptransfrom_Top']
    #,'_proptransto_Bottom','_proptransto_Graph','_proptransto_Toolbar','_proptransto_Top']
    aoinames = ['Top','Bottom','Graph','Toolbar']
    aoifeaturelist =[]
    for aoin in aoinames:
        aoifeaturelist.extend(map(lambda x:aoin+x, aoigeneralfeat))
        aoifeaturelist.extend(map(lambda x:aoin+x, aoitransfrom))
        #aoifeaturelist.extend(map(lambda x:aoin+x, aoitransto))
        aoifeaturelist.extend(map(lambda x:aoin+x, aoiproportion))
        
    
    # Validity Threshold for segments
    VALID_PROP_THRESH = 0.85
    VALID_TIME_THRESH = 3000
    MAX_SEG_TIMEGAP = 300 #maximum gap size (ms) allowable in a segment with auto-partition option
    VALIDITY_METHOD = 3 #1: porportion; 2:time gap; 3: fixation based porportion
    
    MINSEGSIZE = 300 #minimum segment size in ms
    
    INCLUDE_HALF_FIXATIONS = False
    
    DEBUG = False
    DEBUG = True
    
    
    ACTIIONS = [1,2,3,4,5,6,7,8,9,10,11,12,13]
    #Features
    
    NONTEMP_FEATURES_SEG = ['meanfixationduration', 'stddevfixationduration',
    'fixationrate', 'meanpathdistance', 'stddevpathdistance', 'meanabspathangles', 'stddevabspathangles',
    'meanrelpathangles', 'stddevabspathangles'] 
    
    NONTEMP_FEATURES_AOI = ['longestfixation', 'proportionnum', 'proportiontime',
    'proptransto', 'proptransfrom']
elif EXPERIMENT == 'PC':
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
