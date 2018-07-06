"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Generic Participant Class
Created on 2011-09-25

Generic class to handle eye tracking and events data for one Participant in the experiment.

@author: Samad Kardan (creator), Sebastien Lalle
Institution: The University of British Columbia.
"""

import string
import params
import EMDAT_core
from EMDAT_core.data_structures import *
from EMDAT_core.Scene import Scene
from EMDAT_core.Recording import *


class Participant():
    """
    A class that holds the information for one Participant in the experiment
    """

    def __init__(self, pid, eventfile, datafile, fixfile, segfile, saccfile, log_time_offset = None, aoifile = None, prune_length= None,
                 require_valid_segs = True, auto_partition_low_quality_segments = False, rpsdata = None):
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

            require_valid_segs: a boolean determining whether invalid "Segment"s
                will be ignored when calculating the features or not. default = True

            auto_partition_low_quality_segments: a boolean indicating whether EMDAT should
                split the "Segment"s which have low sample quality, into two new
                sub "Segment"s discarding the largest gap of invalid samples.

            rpsdata: rest pupil sizes for all scenes if available

        Yields:
            a Participant object
        """
        self.pid = pid
        self.require_valid_segments = require_valid_segs


    def is_valid(self, method = None, threshold=None, ):
        """Determines if the samples for this Participant meets the validity threshold

        Args:
            threshold: if not None, the threshold value that should be used for the
                validity criterion

        Returns:
            True or False
        """
        if threshold == None:
            return self.whole_scene.is_valid
        elif method == None:
            method = params.VALIDITY_METHOD

        if method == 1:
            return self.whole_scene.calc_validity1(threshold)
        elif method == 2:
            return self.whole_scene.calc_validity2(threshold)
        elif method == 3:
            return self.whole_scene.calc_validity3(threshold)

    def invalid_segments(self):
        """Returns a list of invalid segments in this particiapnt's eye gaze data

        Returns:
            a list of "Segment ids" of invalid Segments in this particiapnt's eye gaze data
        """
        return map(lambda y: y.segid, filter(lambda x: not x.is_valid, self.segments))

    def valid_segments(self):
        """Returns a list of valid segments in this particiapnt's eye gaze data

        Returns:
            a list of "Segment ids" of invalid Segments in this particiapnt's eye gaze data
        """
        return map(lambda y: y.segid, filter(lambda x: x.is_valid, self.segments))


    def export_features(self, featurelist=None, aoifeaturelist=None, aoifeaturelabels = None,
                        id_prefix = True, require_valid = True):
        """Returns feature names and their values for this Participant

        Args:
            featurelist: if not None, a list of strings containing the name of the features to be
                returned

            aoifeaturelist: if not None, a list of features to be returned for each of the "AOI"s.
            aoifeaturelabels: if not None, a list of AOI related features to be returned.
            *Note: while aoifeaturelist is a subset of features that will be returned for all
            "AOI"s, aoifeaturelabels contains the exact AOI feature name, i.e., a feature
            of the form: [AOI name]_[feature name]
            For example for an AOI called 'graph', aoifeaturelabels may contain 'graph_fixationrate'

            id_prefix: a boolean determining if the method should also export the participant id

            require_valid: a boolean determining if only valid segments should be used when
            calculating the features. default = True

        Returns:
            featnames: a list of feature names sorted alphabetically
            featvals: a corresponding list of feature values
            e.g.
            featnames = ['fixationrate', 'length', 'meanabspathangles']
            featvals  = [0.00268522882294', '1529851', '1.60354714212']
        """
        data = []
        featnames = []
        if id_prefix:
            featnames.append('Part_id')
        featnames.append('Sc_id')
        first = True
        for sc in self.scenes:
            if not sc.is_valid and require_valid:
                warn( "User %s:Scene %s dropped because of 'require_valid'" %(self.pid,sc.scid) )
                continue
            sc_feats = []
            if id_prefix:
                sc_feats.append(self.pid)
            sc_feats.append(sc.scid)
            fnames, fvals = sc.get_features(featurelist = featurelist,
                                           aoifeaturelist = aoifeaturelist,
                                           aoifeaturelabels = aoifeaturelabels)
            if first: featnames += fnames
            sc_feats += fvals
            first = False
            data.append(sc_feats)

        return featnames, data

    def export_features_tsv(self, featurelist=None, aoifeaturelist=None, id_prefix = False,
                            require_valid = True):
        """Returns feature names and their values for this Participant in a tab separated format

        Args:
            featurelist: if not None, a list of strings containing the name of the features to be
                returned

            aoifeaturelist: if not None, a list of features to be returned for each of the "AOI"s.

            id_prefix: a boolean determining if the method should also export the participant id.


            require_valid: a boolean determining if only valid segments should be used when
            calculating the features. default = True

        Returns:
            A two-line string with the first line having the feature names sorted alphabetically
            and separated by a tab '/t', and the second line containing the corresponding values
            separated by a tab '/t'
            For example:
            fixationrate    length    meanabspathangles
            0.00268522882294    1529851    1.60354714212
        """
        featnames, data  = self.export_features(featurelist, aoifeaturelist = aoifeaturelist,
                                                id_prefix = id_prefix, require_valid = require_valid)

        ret = string.join(featnames, '\t') + '\n'
        for t in data:
            ret += (string.join(map(str, t), '\t') + '\n')
        return ret

    def print_(self):
        """Outputs all feature names and their values for this Participant to the console
        """
        def format_list(list,leng=None):
            """
            """
            out=''
            if leng == None:
                maxlen=0
                for j in list:
                    st = repr(j)
                    if len(st) > maxlen:
                        maxlen = len(st)
                for j in list:
                    out+= repr(j).rjust(maxlen+1)
                return out,maxlen+1
            else:
                for j in list:
                    st = repr(j)
                    out+= st.rjust(leng)
                return out,leng

        print("PID:", self.pid)

        for seg in self.segments:
            featnames = []
            if not seg.is_valid:
                continue
            seg_feats = []
            featnames.append('seg_id')
            seg_feats.append(seg.segid)
            fnames, fvals = seg.get_features()
            featnames += fnames
            seg_feats += fvals
            o,l= format_list(featnames)
            print(o)
            print(format_list(seg_feats,l))

        for sc in self.scenes:
            featnames = []
            if not sc.is_valid:
                continue
            sc_feats = []
            featnames.append('sc_id')
            sc_feats.append(sc.scid)
            fnames, fvals = sc.get_features()
            featnames += fnames
            sc_feats += fvals
            o,l= format_list(featnames)
            print(o)
            print(format_list(sc_feats,l))


    def write_raw_data(self, filename_all, filename_fix, filename_sac, filename_ev):
        f_all = open(filename_all, 'wb')
        f_fix = open(filename_fix, 'wb')
        f_sac = open(filename_sac, 'wb')
        f_ev = open(filename_ev, 'wb')
        sep='\t'
        f_all.write("scene"+sep+"timestamp"+sep+"rawpupilsize"+sep+"pupilvelocity"+sep+"headdistance"+sep+"is_valid"+sep+"stimuliname"+sep+
		"fixationindex"+"\n")

        f_fix.write("scene"+sep+"fixationindex"+sep+"timestamp"+sep+"fixationduration"+sep+"mappedfixationpointx"+sep+"mappedfixationpointy"+"\n")

        f_sac.write("scene"+sep+"saccadeindex"+sep+"timestamp"+sep+"saccadeduration"+sep+"saccadedistance"+sep+"saccadespeed"+sep+"saccadeacceleration"+sep+
		"saccadestartpointx"+sep+"saccadestartpointy"+sep+"saccadeendpointx"+sep+"saccadeendpointy"+sep+"saccadequality"+"\n")

        f_ev.write("scene"+sep+"timestamp"+sep+"event"+sep+"event_key"+sep+"x_coord"+sep+"y_coord"+sep+"key_code"+sep+"key_name"+sep+"description"+sep+"\n")


        for sc in self.scenes:
            for sg in sc.segments:

                for ad in sg.all_data:
                    f_all.write(str(sc.scid)+str(sg.segid)+sep+ad.get_string()+'\n')
                for af in sg.fixation_data:
                    f_fix.write(str(sc.scid)+str(sg.segid)+sep+af.get_string()+'\n')
                for asa in sg.saccade_data:
                    f_sac.write(str(sc.scid)+str(sg.segid)+sep+asa.get_string()+'\n')
                for ae in sg.event_data:
                    f_ev.write(str(sc.scid)+str(sg.segid)+sep+ae.get_string()+'\n')

        f_all.close()
        f_fix.close()


def read_participants(segsdir, datadir, prune_length = None, aoifile = None):
    """Placeholder for a method that generates Participant objects for each participant
    in the experiment
    """
    participants = []
    raise Exception("You should override the default Participant.read_participants method!")
    return participants


def export_features_all(participants, featurelist = None, aoifeaturelist = None, aoifeaturelabels=None,
                         id_prefix = True, require_valid = True):
    """Returns feature names and their values for a list of "Participant"s

    Args:
        participants: a list of "Participant"s
        featurelist: if not None, a list of strings containing the name of the features to be
            returned

        aoifeaturelist: if not None, a list of features to be returned for each of the "AOI"s.
        aoifeaturelabels: if not None, a list of AOI related features to be returned.
        *Note: while aoifeaturelist is a subset of features that will be returned for all
        "AOI"s, aoifeaturelabels contains the exact AOI feature name, i.e., a feature
        of the form: [AOI name]_[feature name]
        For example for an AOI called 'graph', aoifeaturelabels may contain 'graph_fixationrate'

        id_prefix: a boolean determining if the method should also export the participant id

        require_valid: a boolean determining if only valid segments should be used when
        calculating the features. default = True

    Returns:
        featnames: a list of feature names sorted alphabetically
        featvals: a corrsponding list of feature values
        e.g.
        featnames = ['fixationrate', 'length', 'meanabspathangles']
        featvals  = [0.00268522882294', '1529851', '1.60354714212']
    """
    data = []
    featnames = []
    if participants:
        for p in participants:
            if not(p.is_valid()) and require_valid:
                warn( "User " + str(p.pid) + " was not valid." )
                continue
            fnames, fvals = p.export_features(featurelist=featurelist, aoifeaturelist=aoifeaturelist,
                                              aoifeaturelabels = aoifeaturelabels,
                                              id_prefix=id_prefix, require_valid = require_valid)
            featnames = fnames
            data += fvals
    else:
        raise NameError('No participants were passed to the function')

    return featnames, data


def write_features_tsv(participants, outfile, featurelist = None, aoifeaturelist =  None,
                       aoifeaturelabels=None, id_prefix = True):
    """Returns feature names and their values for a list of "Participant"s in a tsv-format file

    This method writes to a multi-line tab separated values (tsv) file with the first
    line having the feature names sorted alphabetically and separated by a tab '/t',
    and the rest of the lines containing the corresponding values for each participant
    separated by a tab '/t'
    For example:
    fixationrate    length    meanabspathangles
    0.0026852294    1529851    1.60354714212
    0.00456324344    453455    1.74324423

    Args:
        participants: a list of "Participant"s
        outfile: a string containing the name of the output file
        featurelist: if not None, a list of strings containing the name of the features to be
            returned

        aoifeaturelist: if not None, a list of features to be returned for each of the "AOI"s.

        id_prefix: a boolean determining if the method should also export the participant id

        require_valid: a boolean determining if only valid segments should be used when
        calculating the features. default = True
    """
    fnames, fvals = export_features_all(participants, featurelist =  featurelist,
                                        aoifeaturelabels = aoifeaturelabels,
                                        aoifeaturelist = aoifeaturelist, id_prefix=id_prefix)

    with open(outfile, 'w') as f:
        f.write(string.join(fnames, '\t') + '\n')
        for l in fvals:
            f.write(string.join(map(str, l), '\t') + '\n')


def partition(segfile):
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
    for l in scenelist.items():
        segcount += len(l)
    return scenelist, segcount


def test_validity():
    """
    Placeholder for a method that tests the quality of the eye data for each Participant
    """
    return


def read_events(evfile):
    """Returns a list of Event objects read from an 'Event-Data.tsv' file.

    Args:
        evfile: a string containing the name of the 'Event-Data.tsv' file exported from
            Tobii software

    Returns:
        a list of Event objects
    """
    with open(evfile, 'r') as f:
        lines = f.readlines()

    return map(Event, lines[(params.EVENTSHEADERLINES+params.NUMBEROFEXTRAHEADERLINES):])


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
