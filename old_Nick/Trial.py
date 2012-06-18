import math, geometry
from AOI import *

VALID_TIME_THRESH = 300
VALID_PROP_THRESH = 0.9


class Trial():
    def __init__(self, qid, all_data, fixation_data, aois = None, prune_length = None):
        """
        @type qid: str
        @param qid: The id of the trial.
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
        self.qid = qid
        self.completion_time = all_data[-1].timestamp - all_data[0].timestamp 
        self.start = all_data[0].timestamp
        self.numfixations = len(fixation_data)
        self.largest_data_gap = self.calc_largest_validity_gap(all_data)
        self.proportion_valid = self.calc_validity_proportion(all_data)
        self.validity1 = self.calc_validity1(all_data)
        self.validity2 = self.calc_validity2(all_data)
        self.is_valid = self.validity2
        if prune_length:
            all_data = filter(lambda x: x.timestamp <= self.start +
            prune_length, all_data)
            fixation_data = filter(lambda x: x.timestamp <= self.start +
            prune_length, fixation_data)
        self.end = all_data[-1].timestamp
        self.length = self.end - self.start
        self.numsamples = self.calc_num_samples(all_data)
        self.numfixations = len(fixation_data)
        self.fixationrate = float(self.numfixations) / self.length
        if self.numfixations > 0:
            self.meanfixationduration = mean(map(lambda x: float(x.fixationduration), fixation_data))
            self.stddevfixationduration = stddev(map(lambda x: float(x.fixationduration), fixation_data))
            self.sumfixationduration = sum(map(lambda x: x.fixationduration, fixation_data))
            self.fixationrate = float(self.numfixations)/self.length
            distances = self.calc_distances(fixation_data)
            abs_angles = self.calc_abs_angles(fixation_data)
            rel_angles = self.calc_rel_angles(fixation_data)
        else:
            self.meanfixationduration = 0
            self.stddevfixationduration = 0
            self.sumfixationduration = 0
            self.fixationrate = 0
            distances = []
        if len(distances) > 0:
            self.meanpathdistance = mean(distances)
            self.sumpathdistance = sum(distances)
            self.stddevpathdistance = stddev(distances)
            self.sumabspathangles = sum(abs_angles)
            self.meanabspathangles = mean(abs_angles)
            self.stddevabspathangles = stddev(abs_angles)
            self.sumrelpathangles = sum(rel_angles)
            self.meanrelpathangles = mean(rel_angles)
            self.stddevrelpathangles = stddev(rel_angles)
        else:
            self.meanpathdistance = 0
            self.sumpathdistance = 0
            self.stddevpathdistance = 0
            self.sumabspathangles = 0
            self.meanabspathangles= 0
            self.stddevabspathangles= 0
            self.sumrelpathangles = 0
            self.meanrelpathangles= 0
            self.stddevrelpathangles = 0
        if aois:
            self.set_aois(aois,fixation_data)

    def set_aois(self, aois, fixation_data):
        """
        @type fixation_data: array of L{Fixations<Datapoint.Fixation>}
        @param fixation_data: The fixations which make up this Trial.
        @type aois: array of L{AOIs<AOI.AOI>}
        @param aois: The AOIs relevant to this trial
        """
        if len(aois) == 0:
            print self.qid
        self.aoi_data = {}
        for (aid, polyin, polyout) in aois:
            aoi = AOI(aid, polyin, polyout, fixation_data, self.start,
            self.end, aois)
            self.aoi_data[aid] = aoi
        

    def calc_validity_proportion(self, all_data):
        """
        Calculate the proportion of datapoints which are valid.
        @type all_data: array of L{Datapoints<Datapoint.Datapoint>}
        @param all_data: The datapoints which make up this Trial.
        """
        num_valid = float(0)
        num = 0

        for d in all_data:
            if d.stimuliname == 'ScreenRec':
                num += 1
                if d.is_valid:
                    num_valid += 1

        return num_valid / num

    def calc_largest_validity_gap(self, all_data):
        if self.numfixations == 0:
            return float('inf')
        last_valid = self.start
        max = 0
        for d in all_data:
            if d.stimuliname == 'ScreenRec':
                if d.is_valid:
                    last_valid = d.timestamp
                else:
                    if d.timestamp - last_valid > max:
                        max = d.timestamp - last_valid

        return max

    def calc_validity1(self, all_data):
        return self.calc_validity_proportion(all_data) > VALID_PROP_THRESH

    def calc_validity2(self, all_data):
        return self.calc_largest_validity_gap(all_data) <= VALID_TIME_THRESH


    def calc_distances(self, fixdata):
        """
        Calculate the Euclidean distances between subsequent L{Fixations<Fixation.Fixation>}.
    
        @type fixdata: Array of L{Fixations<Fixation.Fixation>}.
        @param fixdata: The array of L{Fixations<Fixation.Fixation>}.
        """
        distances = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1, len(fixdata)):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            dist = math.sqrt((x-lastx)**2 + (y-lasty)**2)
            distances.append(dist)
            lastx = x
            lasty = y

        return distances

    def calc_abs_angles(self, fixdata):
        abs_angles = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1,len(fixdata)):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            (dist, theta) = geometry.vector_difference((lastx,lasty), (x, y))
            abs_angles.append(abs(theta))
            lastx=x
            lasty=y

        return abs_angles

    def calc_rel_angles(self, fixdata):
        rel_angles = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1, len(fixdata)-1):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            nextx = fixdata[i+1].mappedfixationpointx
            nexty = fixdata[i+1].mappedfixationpointy
            (dist, theta) = geometry.vector_difference((x,y), (lastx, lasty))
            (dist, nextheta) = geometry.vector_difference((x,y), (nextx, nexty))
            theta = abs(theta-nextheta)
            rel_angles.append(theta)
            lastx=x
            lasty=y

        return rel_angles

    def calc_num_samples(self, all_data):
        num = 0
        for d in all_data:
            if d.stimuliname == 'ScreenRec':
                num += 1
        return num

def stddev(data):
    m = mean(data)
    return math.sqrt(sum(map(lambda x: (x-m)**2, data)))
    
def mean(data):
    if len(data)==0:
        return 0
    return sum(data) / len(data)
        
