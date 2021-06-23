"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2014-09-16

Sample code showing how to instantiate the "Participant" class for a given experiment (multiprocessing version).

Authors: Sebastien Lalle (creator), Samad Kardan.
Institution: The University of British Columbia.
"""

from math import ceil, floor
from multiprocessing import Process, Queue
import os.path

params = __import__('params')
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
            rec = TobiiV2Recording(datafile, fixfile, event_file=eventfile, media_offset=params.MEDIA_OFFSET)
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


def read_participants_Basic(q, datadir, user_list, pids, prune_length = None, aoifile = None, log_time_offsets=None,
                          require_valid_segs = True, auto_partition_low_quality_segments = False, rpsfile = None, export_pupilinfo = False):
    """Generates list of Participant objects. Relevant information is read from input files

    Args:
        q: Queue to which all processes must add return values.

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
        a list Participant objects (in queue)
    """
    participants = []
    if log_time_offsets == None:    #setting the default offset which is 1 sec
        log_time_offsets = [0]*len(pids)

    # read rest pupil sizes (rpsvalues) from rpsfile
    rpsdata = read_rest_pupil_sizes(rpsfile)

    for rec,pid,offset in zip(user_list,pids,log_time_offsets):
        #extract pupil sizes for the current user. Set to None if not available
        if rpsdata != None:
            currpsdata = rpsdata[pid]
        else:
            currpsdata = None

        if params.EYETRACKERTYPE == "TobiiV2":
            allfile = datadir+'/TobiiV2/P'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/TobiiV2/P'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/TobiiV2/P'+str(rec)+'-Event-Data.tsv'
            sacfile = None
            segfile = datadir+'/TobiiV2/P'+str(rec)+'.seg'
        elif params.EYETRACKERTYPE == "TobiiV3":
            allfile = "{dir}/TobiiV3/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            fixfile = "{dir}/TobiiV3/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            sacfile = "{dir}/TobiiV3/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            evefile = "{dir}/TobiiV3/P{rec}_Data_Export.tsv".format(dir=datadir, rec=rec)
            segfile = "{dir}/TobiiV3/TobiiV3_sample_{rec}.seg".format(dir=datadir, rec=rec)
            #aoifile = "{dir}/TobiiV3/TobiiV3_sample_{rec}.aoi".format(dir=datadir, rec=rec)
        elif params.EYETRACKERTYPE == "SMI":
            allfile = "{dir}/SMI/SMI_Sample_{rec}_Samples.txt".format(dir=datadir, rec=rec)
            fixfile = "{dir}/SMI/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            sacfile = "{dir}/SMI/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            evefile = "{dir}/SMI/SMI_Sample_{rec}_Events.txt".format(dir=datadir, rec=rec)
            segfile = "{dir}/SMI/SMI_Sample_{rec}.seg".format(dir=datadir, rec=rec)

        if os.path.exists(allfile):
            p = BasicParticipant(rec, evefile, allfile, fixfile, sacfile, segfile, log_time_offset = offset,
                                aoifile=aoifile, prune_length = prune_length, require_valid_segs = require_valid_segs,
                                auto_partition_low_quality_segments = auto_partition_low_quality_segments, rpsdata = currpsdata)
            participants.append(p)
        else:
            print "Error reading participant files for: "+str(pid)
    q.put(participants)
    return

def read_participants_Basic_multiprocessing(nbprocesses, datadir, user_list, pids, prune_length = None, aoifile = None, log_time_offsets = None,
                          require_valid_segs = True, auto_partition_low_quality_segments = False, rpsfile = None, export_pupilinfo = False):
    """Generates list of Participant objects in parallel computing. Relevant information is read from input files

    Args:
        nbprocesses: number of processes to run in parallel (number of CPU cores is a good option).

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

    q = Queue()
    listprocess = []
    participants = []

    if nbprocesses < 1:
        nbprocesses = 1
    if nbprocesses > len(user_list):
        nbprocesses = len(user_list)

    for i in range(0, nbprocesses): #create a sublist of participants for each process
        user_listsplit = chunks(user_list, nbprocesses)
        pidssplit = chunks(pids, nbprocesses)
        log_time_offsets_list = chunks(log_time_offsets, nbprocesses) if log_time_offsets is not None else None

    print user_listsplit
    try:
        for i in range(0, nbprocesses):
            if log_time_offsets is None:
			    p = Process(target=read_participants_Basic, args=(q, datadir, user_listsplit[i], pidssplit[i], prune_length, aoifile, log_time_offsets,
                          require_valid_segs, auto_partition_low_quality_segments, rpsfile, export_pupilinfo))
            else:
			    p = Process(target=read_participants_Basic, args=(q, datadir, user_listsplit[i], pidssplit[i], prune_length, aoifile, log_time_offsets_list[i],
                          require_valid_segs, auto_partition_low_quality_segments, rpsfile, export_pupilinfo))

            listprocess.append(p)
            p.start() # start the process

        for i in range(0, nbprocesses):
            participants = participants + q.get(True) # wait for the results of all processes

        for pr in listprocess:
            pr.terminate()
            pr.join() #kill the process

    except  Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print "Exception", sys.exc_info()
        print "Line ", exc_tb.tb_lineno

    return participants

def chunks(l, n):
    """Split a list in balanced sub-lists. If equal sublits are not possible, remaining elements are distribute evenly among sublists.

    Args:
        l: the list to split.

        n: the number of sublists to generate.

    Returns:
        a list of n sublists
    """
    if n < 1:
        n = 1
    if len(l) < n:
        n = len(l)

    nsize = len(l)/n #number of elements in the sublists
    if len(l)%n == 0:
        return [l[i:i + nsize] for i in range(0, len(l), nsize)]
    else:
        l2 = [l[i:i + nsize] for i in range(0, len(l[0:nsize*n]), nsize)]
        i=0
        for j in l[nsize*n:len(l)]: #distribute remaining elements
            l2[i].append(j)
            i = (i+1) % n
        return l2

def partition_Basic(segfile):
    """Generates the scenelist based on a .seg file

    Args:
        segfile: a string containing the name of the '.seg' file

    Returns:
        a dict with scid as the key and tuples of (segid, start , end) for segments that belong to
            that scene as value
        an integer determining the number of segments
    """
    scenelist = read_segs(segfile)
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
