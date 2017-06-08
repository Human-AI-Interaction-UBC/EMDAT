"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2012-08-23

Sample code showing how to instantiate the "Participant" class for a given experiment. 

Authors: Samad Kardan (creator), Sebastien Lalle. 
Institution: The University of British Columbia.
"""
from math import ceil, floor
import os.path

params=__import__('params')
from EMDAT_core.data_structures import *
from EMDAT_core.Participant import *
from EMDAT_core.Recording import *
from EMDAT_core.AOI import AOI
from EMDAT_core.Scene import Scene
from EMDAT_core.utils import *

from EMDAT_eyetracker.TobiiV2Recording import TobiiV2Recording
from EMDAT_eyetracker.TobiiV3Recording import TobiiV3Recording
from EMDAT_eyetracker.SMIRecording import SMIRecording

class BasicParticipant(Participant):
    """
    This is a sample child class based on the Participant class that implements all the 
    placeholder methods in the Participant class for a basic project
    """
    def __init__(self, pid, eventfile, datafile, fixfile, saccfile, segfile, log_time_offset = None, aoifile = None, prune_length= None, 
                 require_valid_segs = True, auto_partition_low_quality_segments = False, rpsdata = None, export_pupilinfo = False):
        """Inits BasicParticipant class
        Args:
            pid: Participant id
            
            eventfile: a string containing the name of the event file for this participant (None if no event)
            
            datafile: a string containing the name of the gaze sample file for this participant
            
            fixfile: a string containing the name of the fixation file for this participant
            
			saccfile: a string containing the name of the saccade file for this participant (None if no saccades)
            
            segfile: a string containing the name of the '.seg' file for this participant
            
            log_time_offset: If not None, an integer indicating the time offset between the 
                external log file and eye tracking logs
            
            aoifile: If not None, a string containing the name of the '.aoi' file 
                with definitions of the "AOI"s.
            
            prune_length: If not None, an integer that specifies the time 
                interval (in ms) from the beginning of each Segment in which
                samples are considered in calculations.  This can be used if, 
                for example, you only wish to consider data in the first 
                1000 ms of each Segment. In this case (prune_length = 1000),
                all data beyond the first 1000ms of the start of the "Segment"s
                will be disregarded.
                
            auto_partition_low_quality_segments: a boolean indicating whether EMDAT should 
                split the "Segment"s which have low sample quality, into two new 
                sub "Segment"s discarding the largest gap of invalid samples.
            
            rpsdata: rest pupil sizes for all scenes if available
            
        Yields:
            a BasicParticipant object
        """
        

        Participant.__init__(self, pid, eventfile, datafile, fixfile, saccfile, segfile, log_time_offset, aoifile, prune_length, 
                 require_valid_segs, auto_partition_low_quality_segments, rpsdata)   #calling the Participant's constructor
        
        print "Participant \""+str(pid)+"\"..."
        if params.VERBOSE != "QUIET":
            print "Reading input files:"
            print "--Scenes/Segments file: "+segfile
            print "--Eye tracking samples file: "+datafile
            print "--Fixations file: "+fixfile
            print "--Saccades file: "+saccfile if saccfile is not None else "--No saccades file"
            print "--Events file: "+eventfile if eventfile is not None else "--No events file"
            print "--AOIs file: "+aoifile if aoifile is not None else "--No AOIs file"
            print 
		    
			
        self.features={}
        if params.EYETRACKERTYPE == "TobiiV2":
            rec = TobiiRecording(datafile, fixfile, event_file=eventfile, media_offset=params.MEDIA_OFFSET)
        elif params.EYETRACKERTYPE == "TobiiV3":
            rec = TobiiV3Recording(datafile, fixfile, saccade_file=saccfile, event_file=eventfile, media_offset=params.MEDIA_OFFSET)
        elif params.EYETRACKERTYPE == "SMI":
            rec = SMIRecording(datafile, fixfile, saccade_file=saccfile, event_file=eventfile, media_offset=params.MEDIA_OFFSET)
        else:
            raise Exception("Unknown eye tracker type.")

        if params.VERBOSE != "QUIET":
            print "Creating partition..."
        
        scenelist,self.numofsegments = partition(segfile)
        if self.numofsegments == 0:
            raise Exception("No segments found.")
			
        if aoifile is not None:
            aois = read_aois(aoifile)
        else:
            aois = None
        
        self.features['numofsegments'] = self.numofsegments
        
        if params.VERBOSE != "QUIET":
            print "Generating features..."
			
        self.segments, self.scenes = rec.process_rec(scenelist = scenelist,aoilist = aois,prune_length = prune_length, require_valid_segs = require_valid_segs, 
                                                     auto_partition_low_quality_segments = auto_partition_low_quality_segments, rpsdata = rpsdata, export_pupilinfo=export_pupilinfo)
        
        all_segs = sorted(self.segments, key=lambda x: x.start)
        self.whole_scene = Scene(str(pid)+'_allsc',[],rec.all_data,rec.fix_data, saccade_data = rec.sac_data, event_data = rec.event_data, Segments = all_segs, aoilist = aois,prune_length = prune_length, require_valid = require_valid_segs, export_pupilinfo=export_pupilinfo )
        self.scenes.insert(0,self.whole_scene)

        #Clean memory
        for sc in self.scenes:
            sc.clean_memory()
        rec.clean_memory()
		
        if params.VERBOSE != "QUIET":
            print "Done!"
            print

               
def read_participants_Basic(datadir, user_list, pids, prune_length = None, aoifile = None, log_time_offsets=None, 
                          require_valid_segs = True, auto_partition_low_quality_segments = False, rpsfile = None):
    """Generates list of Participant objects. Relevant information is read from input files
    
    Args:
        datadir: directory with user data (including "All-Data.tsv", "Fixation-Data.tsv", "Event-Data.tsv" files) 
        for all participants
        
        user_list: list of user recordings (files extracted for one participant from Tobii studio)
        
        pids: User ID that is used in the external logs (can be different from above but there should be a 1-1 mapping)
        
        prune_length: If not None, an integer that specifies the time 
            interval (in ms) from the beginning of each Segment in which
            samples are considered in calculations.  This can be used if, 
            for example, you only wish to consider data in the first 
            1000 ms of each Segment. In this case (prune_length = 1000),
            all data beyond the first 1000ms of the start of the "Segment"s
            will be disregarded.
        
        aoifile: If not None, a string containing the name of the '.aoi' file 
            with definitions of the "AOI"s.
        
        log_time_offset: If not None, an integer indicating the time offset between the 
            external log file and eye tracking logs
    
        require_valid_segs: a boolean determining whether invalid "Segment"s
            will be ignored when calculating the features or not. default = True 
        
        auto_partition_low_quality_segments: a boolean indicating whether EMDAT should 
            split the "Segment"s which have low sample quality, into two new 
            sub "Segment"s discarding the largest gap of invalid samples.
        
        rpsfile: If not None, a string containing the name of the '.tsv' file 
            with rest pupil sizes for all scenes and for each user. 
        
    Returns:
        a list Participant objects
    """
    participants = []
    if log_time_offsets == None:    #setting the default offset which is 1 sec
        log_time_offsets = [1]*len(pids) 
    
    # read rest pupil sizes (rpsvalues) from rpsfile
    rpsdata = read_rest_pupil_sizes(rpsfile)
    
    for rec,pid,offset in zip(user_list,pids,log_time_offsets):
        #extract pupil sizes for the current user. Set to None if not available
        if rpsdata != None:
            currpsdata = rpsdata[pid]
        else:
            currpsdata = None

        if params.EYETRACKERTYPE == "TobiiV2":
            allfile = datadir+'/P'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/P'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/P'+str(rec)+'-Event-Data.tsv'
            sacfile = None
            segfile = datadir+'/P'+str(rec)+'.seg'
        elif params.EYETRACKERTYPE == "TobiiV3":
            allfile = "{dir}/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            fixfile = "{dir}/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            sacfile = "{dir}/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            evefile = "{dir}/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            segfile = "{dir}/P{rec}.seg".format(dir=datadir, rec=rec)
            aoifile = "{dir}/single_aoi.aoi".format(dir=datadir, rec=rec)
        elif params.EYETRACKERTYPE == "SMI":
            allfile = "{dir}/SMI_Sample_{rec}_Samples.txt".format(dir=datadir, rec=rec)
            fixfile = "{dir}/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            sacfile = "{dir}/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            evefile = "{dir}/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            segfile = "{dir}/SMI_Sample_{rec}.seg".format(dir=datadir, rec=rec)
		
        if os.path.exists(allfile):
            p = BasicParticipant(rec, evefile, allfile, fixfile, sacfile, segfile, log_time_offset = offset, 
                                aoifile=aoifile, prune_length = prune_length, require_valid_segs = require_valid_segs,
                                auto_partition_low_quality_segments = auto_partition_low_quality_segments, rpsdata = currpsdata)
            participants.append(p)
        else:
            warn( "Error reading participant files for: "+str(pid) )
    return participants

