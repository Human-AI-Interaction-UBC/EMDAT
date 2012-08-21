"""
UBC Eye Movement Data Analysys Toolkit
Generic Participant Class
Created on 2011-09-25

@author: skardan
"""
import os, string
from data_structures import *
import params



class Participant():
    """
    A class that hold the information for one Participant in the experiment
    """
    def __init__(self, pid, eventfile, datafile, fixfile, aoifile = None, prune_length= None):
        """Inits Participant class
        Args:
            pid: Participant id
            
            eventfile: a string containing the name of the "Event-Data.tsv" file for this participant
            
            datafile: a string containing the name of the "all-Data.tsv" file for this participant
            
            fixfile: a string containing the name of the "Fixation-Data.tsv" file for this participant
            
            aoifile: If not None, a string conatining the name of the aoifile 
                with definitions of the "AOI"s.
            
            prune_length: If not None, an integer that specifies the time 
                interval (in ms) from the begining of each Segment in which
                samples are considered in calculations.  This can be used if, 
                for example, you only wish to consider data in the first 
                1000 ms of each Segment. In this case (prune_length = 1000),
                all data beyond the first 1000ms of the start of the "Segment"s
                will be disregarded.
            
        Yields:
            a Participant object
        """

        raise Exception("you must override this and read and process the datafile and create the scenes and segments here!")
        self.id = pid

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
                        id_prefix = False, require_valid = True):
        """
        """
        data = []
        featnames = []
        if id_prefix:
            featnames.append('Part_id')
        featnames.append('Sc_id')
        first = True
        for sc in self.scenes:
            if not sc.is_valid and require_valid:
                print "User %s:Scene %s dropped because of 'require_valid'" %(self.id,sc.scid)
                continue
            sc_feats = []
            if id_prefix:
                sc_feats.append(self.id)
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
        featnames, data  = self.export_features(featurelist, aoifeaturelist = aoifeaturelist, 
                                                id_prefix = id_prefix, require_valid = require_valid)
        """
        """

        ret = string.join(featnames, '\t') + '\n'
        for t in data:
            ret += (string.join(map(str, t), '\t') + '\n')
        return ret
    
    def print_(self):
        """
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
 
        print  "PID:",self.id
        
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
            print o
            print format_list(seg_feats,l)
            
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
            print o
            print format_list(sc_feats,l)
    

def read_participants(segsdir, datadir, prune_length = None, aoifile = None):
    """
    """
    participants = []
    raise Exception("override read_participants")
    return participants

def export_features_all(participants, featurelist = None, aoifeaturelist = None, aoifeaturelabels=None,
                         id_prefix = False, require_valid = True):
    """
    """
    data = []
    featnames = []
    if participants:
        for p in participants:
            if not(p.is_valid()):
                print "user",p.id,"was not valid"
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
                       aoifeaturelabels=None, id_prefix = False):
    """
    Args:
        participants:
        outfile:
        featurelist: If not None,
        aoifeaturelist: If not None,
        aoifeaturelabels: If not None,
        id_prefix:    default value = False
    """
    fnames, fvals = export_features_all(participants, featurelist =  featurelist, 
                                        aoifeaturelabels = aoifeaturelabels,
                                        aoifeaturelist = aoifeaturelist, id_prefix=id_prefix)
    
    with open(outfile, 'w') as f:
        f.write(string.join(fnames, '\t') + '\n')
        for l in fvals:
            f.write(string.join(map(str, l), '\t') + '\n')

def partition(eventfile):
    """
    Generates the scenes based on the events log
    """
    return

def test_validity():
    return

def read_events(evfile):
    """Returns a list Event objects read from 'Event-Data.tsv' file.

    @type all_file: str
    @param all_file: The filename of the 'Event-Data.tsv' file output by the
    Tobii software.
    """
    with open(evfile, 'r') as f:
        lines = f.readlines()

    return map(Event, lines[(params.EVENTSHEADERLINES+params.NUMBEROFEXTRAHEADERLINES):])
