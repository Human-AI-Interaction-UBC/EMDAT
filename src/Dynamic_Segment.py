'''
UBC Eye Movement Data Analysys Toolkit
Created on 2011-09-23

@author: skardan
'''
from utils import *
import math, geometry
from AOI import *
from Segment import *


class Dynamic_Segment(Segment):
    def __init__(self, segid, all_data, fixation_data, aois = None, prune_length = None):
        """
        @type segid: str
        @param segid: The id of the segment.
        @type all_data: array of L{Datapoints<Datapoint.Datapoint>}
        @param all_data: The datapoints which make up this Trial.
        @type fixation_data: array of L{Fixations<Datapoint.Fixation>}
        @param fixation_data: The fixations which make up this Trial.
        @type aois: array of L{AOIs<AOI.AOI>}
        @param aois: The AOIs relevant to this trial
        @type prune_length: int
        @param prune_length: If not None, this variable specifies the time
        interval (in ms) in which to consider data. This can be used if, for example,
        you only wish to consider data in the first 1000 ms of a trial. In this
        case (prune_length = 1000), all data beyond the first 1000ms of the
        start of the trial will be disregarded.
        """
        Segment.__init__(self, segid, all_data, fixation_data, aois, prune_length)
        self.segid = segid
        self.sampleData = all_data
        
   
        
