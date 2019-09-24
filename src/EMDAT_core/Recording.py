"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2011-09-30

Regcording class: hold all the data from one recording (i.e, one complete experiment session)
for one participant

Authors: Nicholas FitzGerald (creator), Samad Kardan, Sebastien Lalle, Mike Wu.
Institution: The University of British Columbia.
"""

from abc import ABCMeta, abstractmethod
from EMDAT_core.data_structures import *
from EMDAT_core.Scene import *
from EMDAT_core.AOI import *
from EMDAT_core.utils import *


class Recording:
    __metaclass__ = ABCMeta

    def __init__(self, all_file, fixation_file, saccade_file=None, event_file=None, media_offset=(0, 0)):
        """
        :param all_file: path to file that contains all gaze points
        :param fixation_file :path to file that contains all gaze points
        :param event_file :path to file that contains all events
        :param media_offset: the coordinates of the top left corner of the window showing the interface under study.
        (0,0) if the interface was in full screen (default value).
        """
        self.media_offset = media_offset

        self.all_data = self.read_all_data(all_file)
        if len(self.all_data) == 0:
            raise Exception("The file '" + all_file + "' has no samples!")

        self.fix_data = self.read_fixation_data(fixation_file)
        if len(self.fix_data) == 0:
            raise Exception("The file '" + fixation_file + "' has no fixations!")

        if saccade_file is not None:
            self.sac_data = self.read_saccade_data(saccade_file)
            if len(self.sac_data) == 0:
                raise Exception("The file '" + saccade_file + "' has no saccades!")

        else:
            self.sac_data = None

        if event_file is not None:
            self.event_data = self.read_event_data(event_file)
            if len(self.event_data) == 0:
                raise Exception("The file '" + event_file + "' has no events!")
        else:
            self.event_data = None

    @abstractmethod
    def read_all_data(self, all_file):
        """ Read the data file that contains all gaze points.

        :param all_file: path to file that contains all gaze points
        :return: a list of Datapoints
        :rtype: list[Datapoint]
        """
        pass

    @abstractmethod
    def read_fixation_data(self, fixation_file):
        """ Read the data file that contains all fixations.

        :param fixation_file :path to file that contains all fixations points
        :return: a list of Fixations
        :rtype: list[Fixation]
        """
        pass

    @abstractmethod
    def read_saccade_data(self, saccade_file):
        """ Read the data file that contains all saccades.

        :param saccade_file :path to file that contains all saccade_file points
        :return: a list of Saccades
        :rtype: list[Saccade]
        """
        pass

    @abstractmethod
    def read_event_data(self, event_file):
        """ Read the data file that contains all events.

        :param event_file :path to file that contains all events
        :return: a list of Events
        :rtype: list[Event]
        """
        pass

    def process_rec(self, segfile=None, scenelist=None, aoifile=None,
                    aoilist=None, prune_length=None, require_valid_segs=True,
                    auto_partition_low_quality_segments=False, rpsdata=None, export_pupilinfo=False):
        """Processes the data for one recording (i.e, one complete experiment session)

        Args:
            segfile: If not None, a string containing the name of the segfile
                with segment definitions in following format:
                Scene_ID<tab>Segment_ID<tab>start time<tab>end time<newline>
                e.g.:
                s1    seg1    0    5988013
                With one segment definition per line
            scenelist: If not None, a list of Scene objects
            *Note: At least one of segfile and scenelist should be not None

            aoifile: If not None, a string containing the name of the aoifile
                with definitions of the "AOI"s.
            aoilist: If not None, a list of "AOI"s.
            *Note:  if aoifile is not None, aoilist will be ignored
                    if both aoifile and aoilist are none AOIs are ignored

            prune_length: If not None, an integer that specifies the time
                interval (in ms) from the beginning of each Segment in which
                samples are considered in calculations.  This can be used if,
                for example, you only wish to consider data in the first
                1000 ms of each Segment. In this case (prune_length = 1000),
                all data beyond the first 1000ms of the start of the "Segment"s
                will be disregarded.

            require_valid_segs: a boolean determining whether invalid "Segment"s
                will be ignored when calculating the features or not. default = True

            auto_partition_low_quality_segments: a boolean flag determining whether
                EMDAT should automatically split the "Segment"s which have low sample quality
                into two new sub "Segment"s discarding the largest invalid sample gap in
                the "Segment". default = False

            rpsdata: a dictionary with rest pupil sizes: (scene name is a key, rest pupil size is a value)
        Returns:
            a list of Scene objects for this Recording
            a list of Segment objects for this recording. This is an aggregated list
            of the "Segment"s of all "Scene"s in the Recording
        """

        if segfile is not None:
            scenelist = read_segs(segfile)
            if params.VERBOSE != "QUIET":
                print("Done reading the segments!")
        elif scenelist is None:
            print("Error in scene file.")

        if aoifile is not None:
            aoilist = read_aois(aoifile)
            if params.VERBOSE != "QUIET":
                print("Done reading the AOIs!")
        elif aoilist is None:
            aoilist = []
            print("Warning: No AOIs defined!")

        scenes = []
        for scid, sc in scenelist.items():
            if params.VERBOSE != "QUIET":
                print("Preparing scene:" + str(scid))
            if params.DEBUG or params.VERBOSE == "VERBOSE":
                print("len(all_data)", len(self.all_data))
            try:
                # get rest pupil size data
                if rpsdata is not None:
                    if scid in rpsdata.keys():
                        scrpsdata = rpsdata[scid]
                    else:
                        scrpsdata = 0
                        if params.DEBUG:
                            print(rpsdata.keys())
                            raise Exception("Scene ID " + scid + " is not in the dictionary with rest pupil sizes. rpsdata is set to 0")
                        else:
                            print("Warning: Scene ID " + scid + " is not in the dictionary with rest pupil sizes. rpsdata is set to 0")
                            pass
                else:
                    scrpsdata = 0
                new_scene = Scene(scid, sc, self.all_data, self.fix_data, saccade_data = self.sac_data, event_data=self.event_data, aoilist=aoilist,
                                  prune_length=prune_length,
                                  require_valid=require_valid_segs,
                                  auto_partition=auto_partition_low_quality_segments, rest_pupil_size=scrpsdata,
                                  export_pupilinfo=export_pupilinfo)
            except Exception as e:
                warn(str(e))
                new_scene = None
                if params.DEBUG:
                    raise
                else:
                    pass
            if new_scene:
                scenes.append(new_scene)
        segs = []
        for sc in scenes:
            segs.extend(sc.segments)
        return segs, scenes


    def clean_memory(self):
        self.all_data = []
        self.fix_data = []
        self.sac_data = []
        self.event_data = []

def read_segs(segfile):
    """Returns a dict with scid as the key and segments as value from a '.seg' file.

    A '.seg' file consists of a set of lines with the following format:
    scene_name[\t]segment_name[\t]start_time[\t]end_time[\n]

    scene_name is the id of the Scene that this Segment belongs to,
    segment_name is the id of the Segment,
    and start_time and end_time determines the time interval for the Segment

    Args:
        segfile: A string containing the name of the '.seg' file

    Returns:
        a dict with scid as the key and segments as value
    """
    scenes = {}
    with open(segfile, 'r') as f:
        seglines = f.readlines()

    for l in seglines:
        l = l.strip()
        l = l.split('\t')
        if l[0] in scenes:
            scenes[l[0]].append((l[1], int(l[2]), int(l[3])))
        else:
            scenes[l[0]] = [(l[1], int(l[2]), int(l[3]))]
    return scenes


def read_aois(aoifile):
    """Returns a list of "AOI"s read from a '.aoi' file.

    The '.aoi' files have pairs of lines of the form:
    aoiname[tab]point1x,point1y[tab]point2x,point2y[tab]...[new line]
    #[tab]start1,end1[tab]...[new line]

    The first line determines name of the AOI and the coordinates of each vertex of
    the polygon that determines the boundaries of the AOI.
    The second line which starts with a '#' is optional and determines the time
    intervals when the AOI is active. If the second line does not exist the AOI will
    be active throughout the whole session (global AOI).
    *Note: If the AOIs are exported from Tobii software the '.aoi' file will only have the
    first line for each AOI and you need to override this method to generate AOIs that are
    active only at certain times (non-global AOI).

    Args:
        aoifile: A string containing the name of the '.aoi' file

    Returns:
        a list of "AOI"s
    """
    with open(aoifile, 'r') as f:
        aoilines = f.readlines()

    return read_aoilines(aoilines)


def read_aoilines(aoilines):
    """
    Args:
        aoilines: List of lines from a '.aoi' file

    Returns:
        list of AOIs
    """
    aoilist = []
    polyin = []
    last_aid = ''

    for line in aoilines:
        chunks = line.strip().split('\t')
        if chunks[0].startswith('#'):  # second line
            if polyin:
                seq = []
                for v in chunks[1:]:
                    seq.append((eval(v)))

                existing_aoi = False
                # first we check if the AOI doesn't already exist (it would be a dynamic boundaries AOI)
                for exist_aoi in aoilist:
                    if last_aid == exist_aoi.aid:
                        existing_aoi = True
                        # dynamic boundaries AOI: we simply add the new shape in the list of polyin and seq
                        exist_aoi.polyin.append(polyin)
                        exist_aoi.polyout.append([])
                        exist_aoi.timeseq.append(seq)

                if not existing_aoi: # new AOI
                    aoi = AOI(last_aid, [polyin], [[]], [seq])
                    aoilist.append(aoi)
                polyin = []
            else:
                raise Exception('error in the AOI file')
        else:
            if polyin:  # global AOI

                existing_aoi = False
                # first we check if the AOI doesn't already exist (it would be a dynamic boundaries AOI)
                for exist_aoi in aoilist:
                    if last_aid == exist_aoi.aid:
                        existing_aoi = True
                        # dynamic boundaries AOI: we simply add the new shape in the list of polyin and seq
                        exist_aoi.polyin.append(polyin)
                        exist_aoi.polyout.append([])
                        exist_aoi.timeseq.append([])

                if not existing_aoi: # new AOI
                    aoi = AOI(last_aid, [polyin], [[]], [[]])
                    aoilist.append(aoi)
                polyin = []

            last_aid = chunks[0]  # first line
            for v in chunks[1:]:
                polyin.append((eval(v)))

    if polyin:  # last (global) AOI

        existing_aoi = False
        # first we check if the AOI doesn't already exist (it would be a dynamic boundaries AOI)
        for exist_aoi in aoilist:
            if last_aid == exist_aoi.aid:
                existing_aoi = True
                # dynamic boundaries AOI: we simply add the new shape in the list of polyin and seq
                exist_aoi.polyin.append(polyin)
                exist_aoi.polyout.append([])
                exist_aoi.timeseq.append([])

        if not existing_aoi: # new AOI
            aoi = AOI(last_aid, [polyin], [[]], [[]])
            aoilist.append(aoi)

    return aoilist


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


def get_pupil_size(pupilleft, pupilright):
    '''
    If recordings for both eyes are available, return their average,
    else return value for a recorded eye (if any)
    Args:
        pupilleft - recording of pupil size on left eye
        pupilright - recording of pupil size on right eye
    Returns:
        pupil size to generate pupil features with.
    '''
    if pupilleft is None and pupilright is None:
        return -1
    if pupilleft is None:
        return pupilright
    if pupilright is None:
        return pupilleft
    return (pupilleft + pupilright) / 2.0


def get_pupil_velocity(last_pupilleft, last_pupilright, pupilleft, pupilright, time):
    if (last_pupilleft is None or pupilleft is None) and (last_pupilright is None or pupilright is None):
        return -1
    if (last_pupilleft is None or pupilleft is None):
        return abs(pupilright - last_pupilright) / time
    if (last_pupilright is None or pupilright is None):
        return abs(pupilleft - last_pupilleft) / time
    return abs( (pupilleft + pupilright) / 2 - (last_pupilleft + last_pupilright) / 2 ) / time


def get_distance(distanceleft, distanceright):
    if distanceleft is None and distanceright is None:
        return -1
    if distanceleft is None:
        return distanceright
    if distanceright is None:
        return distanceleft
    return (distanceleft + distanceright) / 2.0


def get_saccade_distance(saccade_gaze_points):
    distance = 0.0
    try:
        for i in range(0, len(saccade_gaze_points)-1):
            (timestamp1, point1x, point1y) = saccade_gaze_points[i]
            (timestamp2, point2x, point2y) = saccade_gaze_points[i+1]
            distance += float(math.sqrt( float(math.pow(point1x - point2x, 2) + math.pow(point1y - point2y, 2)) ))
    except Exception as e:
        warn(str(e))

    return (distance)


def get_saccade_acceleration(saccade_gaze_points):
    mean_accel = 0
    prev_temp_speed = 0 #initial speed = 0
    try:
	    for i in range(0, len(saccade_gaze_points)-1):
	        (timestamp1, point1x, point1y) = saccade_gaze_points[i]
	        (timestamp2, point2x, point2y) = saccade_gaze_points[i+1]
	        if i+1 == len(saccade_gaze_points)-1:
	            temp_speed = 0
	        else:
	            temp_speed = math.sqrt(math.pow(point1x - point2x, 2) + math.pow(point1y - point2y, 2))
	        mean_accel += (temp_speed-prev_temp_speed) / (timestamp2-timestamp1)
	        prev_temp_speed = temp_speed
		#last gaze point
    except Exception as e:
	    warn(str(e))
    return (mean_accel / (float(len(saccade_gaze_points)-1)) )
