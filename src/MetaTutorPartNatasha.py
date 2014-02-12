"""
UBC Eye Movement Data Analysys Toolkit
Created on 2012-08-23

@author: skardan
"""

from data_structures import *
import Recording
#params=__import__('params')
import params as params
import Participant
from AOI import AOI
from Scene import Scene
from utils import *
from math import ceil, floor


class MetaTutorPart(Participant.Participant):
    """
    This is a sample child class based on the Participant class that implements all the 
    placeholder methods in the Participant class for a basic project
    """
    def __init__(self, pid, datafile, fixfile, segfile, log_time_offset = None, aoifile = None, prune_length= None, 
                 require_valid_segs = True, auto_partition_low_quality_segments = False):
        """Inits MetaTutorPart class
        Args:
            pid: Participant id
            
            eventfile: a string containing the name of the "Event-Data.tsv" file for this participant
            
            datafile: a string containing the name of the "all-Data.tsv" file for this participant
            
            fixfile: a string containing the name of the "Fixation-Data.tsv" file for this participant
            
            segfile: a string containing the name of the '.seg' file for this participant
            
            log_time_offset: If not None, an integer indicating the time offset between the 
                external log file and eye tracking logs
            
            aoifile: If not None, a string conatining the name of the '.aoi' file 
                with definitions of the "AOI"s.
            
            prune_length: If not None, an integer that specifies the time 
                interval (in ms) from the begining of each Segment in which
                samples are considered in calculations.  This can be used if, 
                for example, you only wish to consider data in the first 
                1000 ms of each Segment. In this case (prune_length = 1000),
                all data beyond the first 1000ms of the start of the "Segment"s
                will be disregarded.
                
            auto_partition_low_quality_segments: a boolean indicating whether EMDAT should 
                split the "Segment"s which have low sample quality, into two new 
                sub "Segment"s discarding the largest gap of invalid samples.
            
        Yields:
            a MetaTutorPart object
        """

        # missing a call to Participant.__init__ ????
        
        print "reading the files"
        self.features={}
        rec = Recording.Recording(datafile, fixfile, params.MEDIA_OFFSET)
        print "Done!"
        
        scenelist,self.numofsegments = partition_Basic(segfile)
        print "partition done!"
        if aoifile != None:
            aois = Recording.read_aois_Tobii(aoifile)
        else:
            aois = None
        self.features['numofsegments']= self.numofsegments
        
        self.pid = pid #added by Daria
        
        self.segments, self.scenes = rec.process_rec(scenelist = scenelist,aoilist = aois,prune_length = prune_length, require_valid_segs = require_valid_segs, 
                                                     auto_partition_low_quality_segments = auto_partition_low_quality_segments)

        #added by Daria
        print "Check scenes before calculating overall"
        for sc in self.scenes:
            print sc.scid
            print sc.is_valid
            
        self.whole_scene = Scene('P'+str(pid),[],rec.all_data,rec.fix_data, Segments = self.segments, aoilist = aois,prune_length = prune_length, require_valid = require_valid_segs )
        self.scenes.insert(0,self.whole_scene)

    #added by Daria    
    def is_valid(self,threshold=None):
        """Determines if the samples for this Participant meets the validity threshold
        
        Args:
            threshold: if not None, the threshold value that should be used for the 
                validity criterion
                
        Returns:
            True or False
        """
        if threshold == None:
            return self.whole_scene.is_valid
        else:
            return self.whole_scene.proportion_valid_fix >= threshold

               
def read_participants_Basic(datadir, segdir, list_of_participants, prune_length = None, aoidir = None, log_time_offsets=None, 
                          require_valid_segs = True, auto_partition_low_quality_segments = False):
    #user_list
    #pids 
    participants = []

    #missing something about log_time_offsets

    #basicParticipant loops through log_time_offsets and user_list and pids
    
    for pid in list_of_participants: #for all participants from list_of_participants
        allfile = datadir + pid + '-All-Data.tsv' #All-data file for current participant
        fixfile = datadir + pid + '-Fixation-Data.tsv' #Fixation-data file for current participant
        segfile = segdir + pid + '.segs' #file with segments for current participant
        if aoidir is not None:
            aoifile = aoidir+pid+".aoi"
        else:
            aoifile = None
        import os.path
        #for McGill: offset is already taken into account when creating seg files
        if os.path.exists(allfile):
            print pid + ":"
            p = MetaTutorPart(pid, allfile, fixfile, segfile, log_time_offset = 0, 
                                aoifile=aoifile, prune_length = prune_length, require_valid_segs = require_valid_segs,
                                auto_partition_low_quality_segments = auto_partition_low_quality_segments)
            participants.append(p)
        else:
            print "Error reading participant files for: "+pid
    return participants

def partition_Basic(segfile):
    """Generates the scenelist based on a .seg file
    
    Args:
        segfile: a string containing the name of the '.seg' file
    
    Returns:
        a dict with scid as the key and tuples of (segid, start , end) for segments that belong to
            that scene as value
        an integer determining the number of segments
    """
    scenelist = Recording.read_segs(segfile)
    segcount = 0
    for l in scenelist.itervalues():
        segcount += len(l)
    return scenelist, segcount 

    

def read_events(evfile):
    """Returns a list of Event objects read from an 'Event-Data.tsv' file.

    Args:
        evfile: a string containing the name of the 'Event-Data.tsv' file exported by 
            Tobii software
    
    Returns:
        a list of Event objects
    """
    with open(evfile, 'r') as f:
        lines = f.readlines()

    return map(Event, lines[(params.EVENTSHEADERLINES+params.NUMBEROFEXTRAHEADERLINES):])
