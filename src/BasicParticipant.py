"""
UBC Eye Movement Data Analysys Toolkit
Created on 2012-08-23

@author: skardan
"""

from data_structures import *
from tobii import TobiiRecording
from smi import SMIRecording
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
                 require_valid_segs = True, auto_partition_low_quality_segments = False, rpsdata = None, export_pupilinfo = False):
        """Inits BasicParticipant class
        Args:
            pid: Participant id
            
            eventfile: a string containing the name of the "Event-Data.tsv" file for this participant
            
            datafile: a string containing the name of the "All-Data.tsv" file for this participant
            
            fixfile: a string containing the name of the "Fixation-Data.tsv" file for this participant
            
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
        

        Participant.__init__(self, pid, eventfile, datafile, fixfile, segfile, log_time_offset, aoifile, prune_length, 
                 require_valid_segs, auto_partition_low_quality_segments, rpsdata)   #calling the Participan's constructor
        
        print "reading the files"
        self.features={}
        if params.EYETRACKERTYPE == "Tobii":
            rec = TobiiRecording(datafile, fixfile, event_file=eventfile, media_offset=params.MEDIA_OFFSET)
        elif params.EYETRACKERTYPE == "SMI":
            rec = SMIRecording(datafile, fixfile, event_file=eventfile, media_offset=params.MEDIA_OFFSET)
        else:
            raise Exception("Unknown eye tracker type.")

        print "Done!"
        
        scenelist,self.numofsegments = partition_Basic(segfile)
        print "partition done!"
        if aoifile != None:
            aois = Recording.read_aois_Tobii(aoifile)
        else:
            aois = None
        
        self.features['numofsegments']= self.numofsegments
        
        self.segments, self.scenes = rec.process_rec(scenelist = scenelist,aoilist = aois,prune_length = prune_length, require_valid_segs = require_valid_segs, 
                                                     auto_partition_low_quality_segments = auto_partition_low_quality_segments, rpsdata = rpsdata, export_pupilinfo=export_pupilinfo)
        Segments = self.segments
        self.whole_scene = Scene('P'+str(pid),[],rec.all_data,rec.fix_data, event_data = rec.event_data, Segments = self.segments, aoilist = aois,prune_length = prune_length, require_valid = require_valid_segs, export_pupilinfo=export_pupilinfo )
        self.scenes.insert(0,self.whole_scene)

        for sc in self.scenes:
            sc.clean_memory()

               
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
        print "pid:", pid
        
        #extract pupil sizes for the current user. Set to None if not available
        if rpsdata != None:
            currpsdata = rpsdata[pid]
        else:
            currpsdata = None

        if params.EYETRACKERTYPE == "Tobii":
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
        elif params.EYETRACKERTYPE == "SMI":
            allfile = "{dir}/SMI_Sample_{rec}_Samples.txt".format(dir=datadir, rec=rec)
            fixfile = "{dir}/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            evefile = "{dir}/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            segfile = "{dir}/SMI_Sample_{rec}.seg".format(dir=datadir, rec=rec)
        print allfile
        import os.path
        if os.path.exists(allfile):
            p = BasicParticipant(rec, evefile, allfile, fixfile, segfile, log_time_offset = offset, 
                                aoifile=aoifile, prune_length = prune_length, require_valid_segs = require_valid_segs,
                                auto_partition_low_quality_segments = auto_partition_low_quality_segments, rpsdata = currpsdata)
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

def read_rest_pupil_sizes(rpsfile):
    """
    Returns a dictionary of rest pupil sizes for all scenes if rpsfile is provided. None otherwise
    The input file has the following format:
        pid\t<scene name 1>\t<scene name 2>....\n
        <pid 1>\t<rest pupil size 1>\t<rest pupil size 2>

    Args:
        rpsfile: a string containing the name of the '.tsv' file 
            with rest pupil sizes for all partiicpants and all scenes. 
    
    Returns:
        a dictionary of rest pupil sizes. None otherwise
    
    """
    if rpsfile != None:
        with open(rpsfile, 'r') as f:
            lines = f.readlines()
        rpsdic = {}
        import re
        scenelist = re.findall('\w+', lines[0])
        for line in lines[1:]:
            linelist = re.findall('\w+', line)
            pid = cast_int(linelist[0])
            if pid == None: #if casting didn't work
                pid = linelist[0]
            rpsdic[pid] = {}
            for scene, rpsvalue in zip(scenelist[1:], linelist[1:]):
                rpsdic[pid][scene] = cast_int(rpsvalue)
        
        return rpsdic
    else:
        return None

    
    
def plot_pupil_dilation_all(participants, outdir, scene):
    """
    Plots adjusted pupil dilations to 
    
    Args:
        participants: collection of Participant objects
        
        outdir: directory where files should be exported
        
        scene: name of scene to be exported  
    
    Returns:
    
    """
    lines = []
    for participant in participants:
        lines = export_pupil_dilation_from_scene(participant, scene, separator = "\t")
        with open(outdir + "pupildata" + "_" + str(participant.pid) + "_" + str(scene) + ".tsv", "w") as fout:
            if lines is not None:
                for line in lines:
                    fout.write(line)
            else:
                fout.write("There is no scene " + str(scene) + " in the participant " + str(participant.pid) + " record ")
    

def export_pupil_dilation_from_scene(participant, scene, separator = "\t"):
    """
    Exports pupil dilation information from  pupilinfo_for_export for a scene of a participant
    
    Args:
        participant: a Participant object 
        
        scene: name of scene to be exported
    
    Returns:
        a collection of lines to be written in the file
    """
    lines = []
    for sc in participant.scenes:
        if sc.scid == scene:
            lines.append("timestamp\tpupil size\tadjusted pupil size\n")
            for el in sc.pupilinfo_for_export:
                lines.append(list_to_string(el, "\t"))
            return lines

    return None

def list_to_string(list, separator = "\t"):
    """
    Converts a list of values to a string using SEPARATOR for joints
    
    Args:
        list: a list of values to be converted to a string 
        
        separator:  a separator to be used for joints
    
    Returns:
        a string 
        
    """
    return separator.join(map(str, list))+ "\n"