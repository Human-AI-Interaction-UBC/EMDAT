"""
UBC Eye Movement Data Analysys Toolkit
Created on 2012-08-23

@author: skardan
"""

from data_structures import *
import Recording
params=__import__('params')
from Participant import *
from AOI import AOI
from Scene import Scene
from utils import *
from math import ceil, floor


class BasicParticipant(Participant):
    """
    This is a sample child class based on the Participant class that implements all the 
    placeholder methods in the Participant class for a basic project
    """
    def __init__(self, pid, eventfile, datafile, fixfile, segfile, log_time_offset = None, aoifile = None, prune_length= None, 
                 require_valid_segs = True, auto_partition_low_quality_segments = False):
        """Inits BasicParticipant class
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
            a BasicParticipant object
        """
        

        Participant.__init__(self, pid, eventfile, datafile, fixfile, segfile, log_time_offset, aoifile, prune_length, 
                 require_valid_segs, auto_partition_low_quality_segments)   #calling the Participan's constructor
        
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
        
        self.segments, self.scenes = rec.process_rec(scenelist = scenelist,aoilist = aois,prune_length = prune_length, require_valid_segs = require_valid_segs, 
                                                     auto_partition_low_quality_segments = auto_partition_low_quality_segments)
        
        self.whole_scene = Scene('P'+str(pid),[],rec.all_data,rec.fix_data, Segments = self.segments, aoilist = aois,prune_length = prune_length, require_valid = require_valid_segs )
        self.scenes.insert(0,self.whole_scene)
        
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

               
def read_participants_Basic(datadir, user_list ,pids, prune_length = None, aoifile = None, log_time_offsets=None, 
                          require_valid_segs = True, auto_partition_low_quality_segments = False):
    
    participants = []
    if log_time_offsets == None:    #setting the default offset which is 1 sec
        log_time_offsets = [1]*len(pids) 
        
    for rec,pid,offset in zip(user_list,pids,log_time_offsets):
        print "pid:", pid
        if rec<10:
            allfile = datadir+'/P0'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/P0'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/P0'+str(rec)+'-Event-Data.tsv'
            segfile = datadir+'/P0'+str(rec)+'.seg'
        else:
            allfile = datadir+'/P'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/P'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/P'+str(rec)+'-Event-Data.tsv'
            segfile = datadir+'/P'+str(rec)+'.seg'
        print allfile
        import os.path
        if os.path.exists(allfile):
            p = BasicParticipant(rec, evefile, allfile, fixfile, segfile, log_time_offset = offset, 
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
