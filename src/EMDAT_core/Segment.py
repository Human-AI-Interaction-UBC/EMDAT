"""
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3
Created on 2011-08-26

Segment class: smallest unit of aggregated eye data samples that has conceptual meaning.
A segment is always assigned to a scene.

Authors: Samad Kardan (creator), Sebastien Lalle.
Institution: The University of British Columbia.
"""

import params
from EMDAT_core import geometry
from EMDAT_core.AOI import *
from warnings import warn
from math import isnan
from EMDAT_core.AOI import _fixation_inside_aoi

class Segment():
    """A Segment is a class that represents the smallest unit of aggregated eye data samples with a conceptual meaning.

    A segment is the smallest unit of aggregated eye data samples that has conceptual meaning. This class is the equivalent
    of segments as defined in Tobii studio.

    Attributes:
        segid: A string containing the id of the Segment.
        alldata: A list of "Datapoint"s for this Segment
        features: A dict with feature names as its keys and feature values as its values
        completion_time: An integer indicating total duration of the Segment in milliseconds
            minimum is 16 ms (length of one sample with 60Hz sampling rate (ms))
        start: An integer indicating the Segment's start time in milliseconds
        end: An integer indicating the Segment's end time in milliseconds
        sample_start_ind: An integer indicating the index of the first Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
        sample_end_ind: An integer indicating the index of the last Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
        fixation_start_ind: An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
        fixation_end_ind: An integer indicating the index of the last Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
        numfixations: An integer indicating the number of "Fixation"s in this Segment
        time_gaps: a list of tuples of the form (start, end) indicating the start and end of the gaps of invalid samples in the Segment's samples
        all_invalid_gaps: a list of tuples of the form (start, end) indicating the start and the end of all the gaps of invalid samples
        largest_data_gap: An integer indicating the length of largest invalid gap for this Segment in milliseconds
        proportion_valid: A float indicating the proportion of valid samples over all the samples in this Segment
        proportion_valid_fix: A float indicating the proportion of (valid + restored) samples over all the samples in this Segment
        validity1: a boolean indicating whether this Segment is valid using proportion of valid samples threshold
        validity2: a boolean indicating whether this Segment is valid using largest acceptable gap threshold
        validity3: a boolean indicating whether this Segment is valid using proportion of (valid + restored) samples threshold
        is_valid: a boolean indicating whether this Segment is considered valid by the validity method indicated by params.VALIDITY_METHOD
        length_invalid: An integer indicating total duration of invalid gaps in the segment in milliseconds
        length: An integer indicating total duration of the Segment in milliseconds
        numsamples: An integer indicating total number of samples in the Segment
        fixation_data: A list of "Fixation"s for this Segment
        fixation_start: timestamp of the first entry from list of "Fixation"s for this Segment
        fixation_end: timestamp of the last entry from list of "Fixation"s for this Segment
        aoi_data: A list of AOI_Stat objects for relevant "AOI"s for this Segment
        has_aois: A boolean indicating if this Segment has AOI features calculated for it
    """
    def __init__(self, segid, all_data, fixation_data, saccade_data = None, event_data = None, aois = None, prune_length = None, rest_pupil_size = 0, export_pupilinfo = False):
        """
        Args:
            segid: A string containing the id of the Segment.

            all_data: a list of "Datapoint"s which make up this Segment.

            fixation_data: a list of "Fixation"s which make up this Segment.

            saccade_data: a list of "Saccade"s which make up this Segment (None if no saccades).

            event_data: a list of "Event"s which make up this Segment (None if no events).

            aois: a list of "AOI"s relevant to this Segment.

            prune_length: If not None, an integer that specifies the time interval (in ms) from the beginning of each segment in which
                samples are considered in calculations.  This can be used if, for example, you only wish to consider data in the first
                1000 ms of each segment. In this case (prune_length = 1000), all data beyond the first 1000ms of the start of the segments
                will be disregarded.

            rest_pupil_size: rest pupil size for this segment, used to adjust pupil size.

            export_pupilinfo: True to export raw pupil data in EMDAT output (False by default).

        Yields:
            a Segment object
        """
        self.segid = segid
        #self.all_data = all_data
        #self.fixation_data = fixation_data
        #self.saccade_data = saccade_data
        #self.event_data = event_data
        self.features = {}

        """ If prune_length specified, keep only data from start to start + prune_length
            of the segment
        """
        if prune_length:
            all_data = filter(lambda x: x.timestamp <= self.start + prune_length, all_data)
            fixation_data = filter(lambda x: x.timestamp <= self.start + prune_length, fixation_data)
            if event_data != None:
                event_data = filter(lambda x: x.timestamp <= self.start + prune_length, event_data)
            if saccade_data != None:
                saccade_data = filter(lambda x: x.timestamp <= self.start + prune_length, saccade_data)
                
        self.completion_time = all_data[-1].timestamp - all_data[0].timestamp
        if self.completion_time == 0:
            raise Exception("Zero length segment")

        self.features['completion_time'] = self.completion_time
        self.start = all_data[0].timestamp
        self.numfixations = len(fixation_data)

        """ Validity-related features, determining if the segment is valid """
        self.time_gaps = []
        self.all_invalid_gaps = []
        self.largest_data_gap = self.calc_largest_validity_gap(all_data)
        self.proportion_valid = self.calc_validity_proportion(all_data)
        self.proportion_valid_fix = self.calc_validity_fixation(all_data)
        self.validity1 = self.calc_validity1()
        self.validity2 = self.calc_validity2()
        self.validity3 = self.calc_validity3()
        self.is_valid = self.get_validity()
        self.length_invalid = self.get_length_invalid()

        self.end = all_data[-1].timestamp
        self.length = self.end - self.start
        self.features['length'] = self.end - self.start
        self.features['length_invalid'] = self.length_invalid
        self.numsamples = self.calc_num_samples(all_data)
        self.features['numsamples'] = self.numsamples
        self.numfixations = len(fixation_data)
        self.features['numfixations'] = self.numfixations
        self.features['fixationrate'] = float(self.numfixations) / (self.length - self.length_invalid)

        """ calculate blink features (no rest pupil size adjustments yet)"""
        self.calc_blink_features(all_data)

        """ calculate pupil dilation features (no rest pupil size adjustments yet)"""
        self.calc_pupil_features(all_data, export_pupilinfo, rest_pupil_size)

        """ calculate distance from screen features"""
        self.calc_distance_features(all_data)

        """ calculate fixations, angles and path features"""
        self.calc_fix_ang_path_features(fixation_data)

        """ calculate saccades features if available """
        self.calc_saccade_features(saccade_data)

        """ calculate event features if available """
        self.calc_event_features(event_data)

        """ calculate AOIs features """
        self.has_aois = False
        if aois:
            self.set_aois(aois, all_data, fixation_data, event_data, rest_pupil_size, export_pupilinfo)
            self.features['aoisequence'] = self.generate_aoi_sequence(fixation_data, aois)


    def set_indices(self,sample_st,sample_end,fix_st,fix_end,sac_st=None,sac_end=None,event_st=None,event_end=None):
        """Sets the index features

        Args:
            sample_st: An integer indicating the index of the first Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
            sample_end: An integer indicating the index of the last Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
            fix_st: An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
            fix_end: An integer indicating the index of the last Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
            sac_st: An integer indicating the index of the first Saccade for this Segment in the Participant's list of all "Saccade"s (saccade_data)
            sac_end: An integer indicating the index of the last Saccade for this Segment in the Participant's list of all "Saccade"s (saccade_data)
            event_st: An integer indicating the index of the first Event for this Segment in the Participant's list of all "Event"s (event_data)
            event_end: An integer indicating the index of the last Event for this Segment in the Participant's list of all "Event"s (event_data)
        """
        self.sample_start_ind = sample_st
        self.sample_end_ind = sample_end
        self.fixation_start_ind = fix_st
        self.fixation_end_ind = fix_end
        self.saccade_start_ind = sac_st
        self.saccade_end_ind = sac_end
        self.event_start_ind = event_st
        self.event_end_ind = event_end


    def get_indices(self):
        """Returns the index features

        Returns:
            An integer indicating the index of the first Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
            An integer indicating the index of the last Datapoint for this Segment in the Participant's list of all "Datapoint"s (all_data)
            An integer indicating the index of the first Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
            An integer indicating the index of the last Fixation for this Segment in the Participant's list of all "Fixation"s (fixation_data)
            An integer indicating the index of the first Saccade for this Segment in the Participant's list of all "Saccade"s (saccade_data). None if no saccade.
            An integer indicating the index of the last Saccade for this Segment in the Participant's list of all "Saccade"s (saccade_data). None if no saccade.
            An integer indicating the index of the first Event for this Segment in the Participant's list of all "Event"s (event_data). None if no saccade.
            An integer indicating the index of the last Event for this Segment in the Participant's list of all "Event"s (event_data). None if no saccade.
        Raises:
            Exception: An exception is thrown if the values are read before initialization
        """
        if self.sample_start_ind != None:
            return self.sample_start_ind, self.sample_end_ind, self.fixation_start_ind, \
                self.fixation_end_ind, self.saccade_start_ind, self.saccade_end_ind, self.event_start_ind, self.event_end_ind
        raise Exception ('The indices values are accessed before setting the initial value in segement:'+self.segid+'!')


    def set_aois(self, aois, all_data, fixation_data, event_data = None, rest_pupil_size = 0, export_pupilinfo = False):
        """Sets the relevant "AOI"s for this Segment

        Args:
            all_data: a list of "Datapoint"s which make up this Segment
            fixation_data: The list of "Fixation"s which make up this Segment
            aois: a list of "AOI"s relevant to this Segment
            rest_pupil_size:
        """

        if len(aois) == 0:
            warn("No AOIs passed to segment:"+self.segid)
        active_aois=[]
        self.aoi_data = {}
        for aoi in aois:
            #print "checking:",aoi.aid
            print("Generating features for %s AOI in segment %s" % (aoi.aid, self.segid))
            aoistat = AOI_Stat(aoi, all_data, fixation_data, self.start, self.end, self.length_invalid, aois, event_data, rest_pupil_size, export_pupilinfo)
            self.aoi_data[aoi.aid] = aoistat

            act, _ = aoi.is_active_partition(self.fixation_start, self.fixation_end)
            if act:
                active_aois.append(aoi)
                self.has_aois = True
        print("SEGMENT: active aois in this segment: %d" % len(active_aois))
        if not(active_aois):
            msg = "No active AOIs passed to segment:%s start:%d end:%d" %(self.segid,self.start,self.end)
            warn(msg)

    def calc_blink_features(self, all_data):
        """ Calculates blink features such as
                blink_num:                 number of blinks on the in the segment
                blink_duration_total:       sum of the blink durations for this segment
                blink_duration_mean:        mean of the blink durations for this segment
                blink_duration_std:         standard deviation of blink durations for this segment
                blink_duration_max:         maximal blink duration for this segment
                blink_duration_min:         minimal blink duration for this segment
                blink_rate:                 rate of blinks for this segment
                blink_time_distance_mean:   mean time difference between consequtive blinks
                blink_time_distance_std:    std time difference between consequtive blinks
                blink_time_distance_min:    minimal time difference between consequtive blinks
                blink_time_distance_max:    maximal time difference between consequtive blinks
            Args:
                all_data: The list of "Datapoint"s which make up this Segment
        """
        blink_durations = []
        blink_intervals = []
        last_blink_detected = -1
        self.features['blinknum']               = 0
        self.features['blinkdurationtotal']     = 0
        self.features['blinkdurationmean']      = 0
        self.features['blinkdurationstd']       = 0
        self.features['blinkdurationmin']       = -1
        self.features['blinkdurationmax']       = -1
        self.features['blinkrate']              = -1
        self.features['blinktimedistancemean']  = -1
        self.features['blinktimedistancestd']   = -1
        self.features['blinktimedistancemin']   = -1
        self.features['blinktimedistancemax']   = -1
        lower_bound, upper_bould = params.blink_threshold
        ### File operations are for testing
        #file = open('outputfolder/blinks/blinks_%s.txt' % all_data[0].participant_name, 'w
        blinks_validity_gaps = self.calc_blink_validity_gaps(all_data)
        if params.EYETRACKERTYPE == "SMI":
            for i in range(len(blinks_validity_gaps)):
                blink_length = blinks_validity_gaps[i][1] - blinks_validity_gaps[i][0]
                blink_durations.append(blink_length)
                #file.write('Blink start, end: %d %d\n' % (self.time_gaps[i][0], self.time_gaps[i][1]))
                if last_blink_detected != -1:
                    # Calculate time difference between start of current blink and end of previous blink
                    blink_intervals.append(blinks_validity_gaps[i][0] - blinks_validity_gaps[last_blink_detected][1])
                last_blink_detected = i
        else:
            for i in range(len(blinks_validity_gaps)):
                blink_length = blinks_validity_gaps[i][1] - blinks_validity_gaps[i][0]
                if blink_length <= upper_bould and blink_length >= lower_bound:
                    blink_durations.append(blink_length)
                    #file.write('Blink start, end: %d %d\n' % (self.time_gaps[i][0], self.time_gaps[i][1]))
                    if last_blink_detected != -1:
                        # Calculate time difference between start of current blink and end of previous blink
                        blink_intervals.append(blinks_validity_gaps[i][0] - blinks_validity_gaps[last_blink_detected][1])
                    last_blink_detected = i

        #file.close()
        if len(blink_durations) > 0:
            self.features['blinknum']               = len(blink_durations)
            self.features['blinkdurationtotal']     = sum(blink_durations)
            self.features['blinkdurationmean']      = mean(blink_durations)
            self.features['blinkdurationstd']       = stddev(blink_durations)
            self.features['blinkdurationmin']       = min(blink_durations)
            self.features['blinkdurationmax']       = max(blink_durations)
            self.features['blinkrate']              = float(self.features['blinknum']) / (self.length - self.length_invalid)
        if len(blink_intervals) > 0:
            self.features['blinktimedistancemean']  = mean(blink_intervals)
            self.features['blinktimedistancestd']   = stddev(blink_intervals)
            self.features['blinktimedistancemin']   = min(blink_intervals)
            self.features['blinktimedistancemax']   = max(blink_intervals)


    def calc_pupil_features(self, all_data, export_pupilinfo, rest_pupil_size):
        """ Calculates pupil features such as
                mean_pupil_size:            mean of pupil sizes
                stddev_pupil_size:          standard deviation of pupil sizes
                min_pupil_size:             smallest pupil size in this segment
                max_pupil_size:             largest pupil size in this segment
                mean_pupil_velocity:        mean of pupil velocities
                stddev_pupil_velocity:      standard deviation of pupil velocities
                min_pupil_velocity:         smallest pupil velocity in this segment
                max_pupil_velocity:         largest pupil velocity in this segment

            Args:
                all_data: The list of "Datapoint"s which make up this Segment
        """
        # check if pupil sizes are available for all missing points
        pupil_invalid_data = filter(lambda x: x.pupilsize == -1 and x.gazepointx > 0, all_data)
        if len(pupil_invalid_data) > 0:
            if params.DEBUG:
                raise Exception("Pupil size is unavailable for a valid data sample. \
                        Number of missing points: " + str(len(pupil_invalid_data)))
            else:
                warn("Pupil size is unavailable for a valid data sample. Number of missing points: " + str(len(pupil_invalid_data)) )

		#get all pupil sizes (valid + invalid)
        #pupilsizes = map(lambda x: x.pupilsize, all_data)
        #get all datapoints where pupil size is available
        valid_pupil_data = filter(lambda x: x.pupilsize > 0, all_data)
        valid_pupil_velocity = filter(lambda x: x.pupilvelocity != -1, all_data)

        #number of valid pupil sizes
        self.features['meanpupilsize']       = -1
        self.features['stddevpupilsize']     = -1
        self.features['maxpupilsize']        = -1
        self.features['minpupilsize']        = -1
        self.features['startpupilsize']      = -1
        self.features['endpupilsize']        = -1
        self.features['meanpupilvelocity']   = -1
        self.features['stddevpupilvelocity'] = -1
        self.features['maxpupilvelocity']    = -1
        self.features['minpupilvelocity']    = -1
        self.numpupilsizes                   = len(valid_pupil_data)
        self.numpupilvelocity                = len(valid_pupil_velocity)

        if self.numpupilsizes > 0: #check if the current segment has pupil data available
            if params.PUPIL_ADJUSTMENT == "rpscenter":
                adjvalidpupilsizes = map(lambda x: x.pupilsize - rest_pupil_size, valid_pupil_data)
            elif params.PUPIL_ADJUSTMENT == "PCPS":
                adjvalidpupilsizes = map(lambda x: (x.pupilsize - rest_pupil_size) / (1.0 * rest_pupil_size), valid_pupil_data)
            else:
                adjvalidpupilsizes = map(lambda x: x.pupilsize, valid_pupil_data)#valid_pupil_data

            valid_pupil_velocity = map(lambda x: x.pupilvelocity, valid_pupil_velocity)#valid_pupil_data

            if export_pupilinfo:
                self.pupilinfo_for_export = map(lambda x: [x.timestamp, x.pupilsize, rest_pupil_size], valid_pupil_data)
            self.features['meanpupilsize']           = mean(adjvalidpupilsizes)
            self.features['stddevpupilsize']         = stddev(adjvalidpupilsizes)
            self.features['maxpupilsize']            = max(adjvalidpupilsizes)
            self.features['minpupilsize']            = min(adjvalidpupilsizes)
            self.features['startpupilsize']          = adjvalidpupilsizes[0]
            self.features['endpupilsize']            = adjvalidpupilsizes[-1]

            if len(valid_pupil_velocity) > 0:
                self.features['meanpupilvelocity']   = mean(valid_pupil_velocity)
                self.features['stddevpupilvelocity'] = stddev(valid_pupil_velocity)
                self.features['maxpupilvelocity']    = max(valid_pupil_velocity)
                self.features['minpupilvelocity']    = min(valid_pupil_velocity)

    def calc_distance_features(self, all_data):
        """ Calculates distance features such as
                mean_distance:            mean of distances from the screen
                stddev_distance:          standard deviation of distances from the screen
                min_distance:             smallest distance from the screen in this segment
                max_distance:             largest distance from the screen in this segment
                start_distance:           distance from the screen in the beginning of this segment
                end_distance:             distance from the screen in the end of this segment

            Args:
                all_data: The list of "Datapoint"s which make up this Segment
        """
        # check if distances are available for all missing points
        invalid_distance_data = filter(lambda x: x.distance <= 0 and x.gazepointx >= 0, all_data)
        if len(invalid_distance_data) > 0:
            warn("Distance from screen is unavailable for a valid data sample. \
                        Number of missing points: " + str(len(invalid_distance_data)))

        #get all datapoints where distance is available
        valid_distance_data = filter(lambda x: x.distance > 0, all_data)

        #number of valid distance datapoints
        self.numdistancedata = len(valid_distance_data)
        if self.numdistancedata > 0: #check if the current segment has pupil data available
            distances_from_screen               = map(lambda x: x.distance, valid_distance_data)
            self.features['meandistance']       = mean(distances_from_screen)
            self.features['stddevdistance']     = stddev(distances_from_screen)
            self.features['maxdistance']        = max(distances_from_screen)
            self.features['mindistance']        = min(distances_from_screen)
            self.features['startdistance']      = distances_from_screen[0]
            self.features['enddistance']        = distances_from_screen[-1]
        else:
            self.features['meandistance']       = -1
            self.features['stddevdistance']     = -1
            self.features['maxdistance']        = -1
            self.features['mindistance']        = -1
            self.features['startdistance']      = -1
            self.features['enddistance']        = -1


    def calc_saccade_features(self, saccade_data):
        """ Calculates saccade features such as
                numsaccades:              number of saccades in the segment
                sumsaccadedistance:       sum of distances during each saccade
                meansaccadedistance:      mean of distances during each saccade
                stddevsaccadedistance:    standard deviation of distances during each saccade
                longestsaccadedistance:   distance of longest saccade
                sumsaccadeduration:       total time spent on saccades in this segment
                meansaccadeduration:      average saccade duration
                stddevsaccadeduration:    standard deviation of saccade durations
                longestsaccadeduration:   longest duration of saccades in this segment
                meansaccadespeed:         average speed of saccades in this segment
                stddevsaccadespeed:       standard deviation of speed of saccades in this segment
                maxsaccadespeed:          highest saccade speed in this segment
                minsaccadespeed:          lowest saccade speed in this  segment
                fixationsaccadetimeratio: fixation to saccade time ratio for this segment
            Args:
                saccade_data: The list of saccade datapoints for this Segment
        """
        if saccade_data != None and len(saccade_data) > 0:
            self.numsaccades = len(saccade_data)
            self.features['numsaccades'] = self.numsaccades
            self.features['sumsaccadedistance'] = sum(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['meansaccadedistance'] = mean(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['stddevsaccadedistance'] = stddev(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['longestsaccadedistance'] = max(map(lambda x: float(x.saccadedistance), saccade_data))
            self.features['sumsaccadeduration'] = sum(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['meansaccadeduration'] = mean(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['stddevsaccadeduration'] = stddev(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['longestsaccadeduration'] = max(map(lambda x: float(x.saccadeduration), saccade_data))
            self.features['meansaccadespeed'] = mean(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['stddevsaccadespeed'] = stddev(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['maxsaccadespeed'] = max(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['minsaccadespeed'] = min(map(lambda x: float(x.saccadespeed), saccade_data))
            self.features['fixationsaccadetimeratio'] = float(self.features['sumfixationduration']) / self.features['sumsaccadeduration']
        else:
            self.numsaccades = 0
            self.features['numsaccades'] = 0
            self.features['sumsaccadedistance'] = -1
            self.features['meansaccadedistance'] = -1
            self.features['stddevsaccadedistance'] = -1
            self.features['longestsaccadedistance'] = -1
            self.features['sumsaccadeduration'] = -1
            self.features['meansaccadeduration'] = -1
            self.features['stddevsaccadeduration'] = -1
            self.features['longestsaccadeduration'] = -1
            self.features['meansaccadespeed'] = -1
            self.features['stddevsaccadespeed'] = -1
            self.features['maxsaccadespeed'] = -1
            self.features['minsaccadespeed'] = -1
            self.features['fixationsaccadetimeratio'] = -1


    def calc_fix_ang_path_features(self, fixation_data):
        """ Calculates fixation, angle and path features such as
                meanfixationduration:     mean duration of fixations in the segment
                stddevfixationduration    standard deviation of duration of fixations in the segment
                sumfixationduration:      sum of durations of fixations in the segment
                fixationrate:             rate of fixation datapoints relative to all datapoints in this segment
                meanpathdistance:         mean of path distances for this segment
                sumpathdistance:          sum of path distances for this segment
                eyemovementvelocity:      average eye movement velocity for this segment
                sumabspathangles:         sum of absolute path angles for this segment
                abspathanglesrate:        ratio of absolute path angles relative to all datapoints in this segment
                stddevabspathangles:      standard deviation of absolute path angles for this segment
                sumrelpathangles:         sum of relative path angles for this segment
                relpathanglesrate:        ratio of relative path angles relative to all datapoints in this segment
                stddevrelpathangles:      standard deviation of relative path angles for this segment
            Args:
                saccade_data: The list of saccade datapoints for this Segment
        """
        if self.numfixations > 0:
            self.fixation_start = fixation_data[0].timestamp
            self.fixation_end = fixation_data[-1].timestamp
            self.features['meanfixationduration'] = mean(map(lambda x: float(x.fixationduration), fixation_data))
            self.features['stddevfixationduration'] = stddev(map(lambda x: float(x.fixationduration), fixation_data))
            self.features['sumfixationduration'] = sum(map(lambda x: x.fixationduration, fixation_data))
            self.features['fixationrate'] = float(self.numfixations) / (self.length - self.length_invalid)
            distances = self.calc_distances(fixation_data)
            abs_angles = self.calc_abs_angles(fixation_data)
            rel_angles = self.calc_rel_angles(fixation_data)
        else:
            self.fixation_start = -1
            self.fixation_end = -1
            self.features['meanfixationduration'] = -1
            self.features['stddevfixationduration'] = -1
            self.features['sumfixationduration'] = -1
            self.features['fixationrate'] = -1

        self.numfixdistances = len(distances)
        self.numabsangles = len(abs_angles)
        self.numrelangles = len(rel_angles)
        if len(distances) > 0:
            self.features['meanpathdistance'] = mean(distances)
            self.features['sumpathdistance'] = sum(distances)
            self.features['stddevpathdistance'] = stddev(distances)
            self.features['eyemovementvelocity'] = self.features['sumpathdistance']/(self.length - self.length_invalid)
            self.features['sumabspathangles'] = sum(abs_angles)
            self.features['abspathanglesrate'] = sum(abs_angles)/(self.length - self.length_invalid)
            self.features['meanabspathangles'] = mean(abs_angles)
            self.features['stddevabspathangles'] = stddev(abs_angles)
            self.features['sumrelpathangles'] = sum(rel_angles)
            self.features['relpathanglesrate'] = sum(rel_angles)/(self.length - self.length_invalid)
            self.features['meanrelpathangles'] = mean(rel_angles)
            self.features['stddevrelpathangles'] = stddev(rel_angles)
        else:
            self.features['meanpathdistance'] = -1
            self.features['sumpathdistance'] = -1
            self.features['stddevpathdistance'] = -1
            self.features['eyemovementvelocity'] = -1
            self.features['sumabspathangles'] = -1
            self.features['abspathanglesrate'] = -1
            self.features['meanabspathangles'] = -1
            self.features['stddevabspathangles'] = -1
            self.features['sumrelpathangles'] = -1
            self.features['relpathanglesrate'] = -1
            self.features['meanrelpathangles'] = -1
            self.features['stddevrelpathangles'] = -1


    def calc_event_features(self, event_data):
        """ Calculates event features such as
                numevents:                number of events in the segment
                numleftclic:              number of left clinks in the segment
                numrightclic:             number of right clinks in the segment
                numdoubleclic:            number of double clinks in the segment
                numkeypressed:            number of times a key was pressed in the segment
                leftclicrate:             the rate of left clicks (relative to all datapoints) in this segment
                rightclicrate:            the rate of right clicks (relative to all datapoints) in this segment
                doubleclicrate:           the rate of double clicks (relative to all datapoints) in this segment
                keypressedrate:           the rate of key presses (relative to all datapoints) in this segment
                timetofirstleftclic:      time until the first left click in this segment
                timetofirstrightclic:     time until the first right click in this segment
                timetofirstdoubleclic:    time until the first double click in this segment
                timetofirstkeypressed:    time until the first key pressed in this segment
            Args:
                event_data: The list of events for this Segment
        """
        if event_data != None:
            (leftc, rightc, doublec, keyp) = generate_event_lists(event_data)

            self.numevents = len(leftc)+len(rightc)+len(doublec)+len(keyp)
            self.features['numevents'] = self.numevents
            self.features['numleftclic'] = len(leftc)
            self.features['numrightclic'] = len(rightc)
            self.features['numdoubleclic'] = len(doublec)
            self.features['numkeypressed'] = len(keyp)
            self.features['leftclicrate'] = float(len(leftc))/(self.length - self.length_invalid)
            self.features['rightclicrate'] = float(len(rightc))/(self.length - self.length_invalid)
            self.features['doubleclicrate'] = float(len(doublec))/(self.length - self.length_invalid)
            self.features['keypressedrate'] = float(len(keyp))/(self.length - self.length_invalid)
            self.features['timetofirstleftclic'] = leftc[0].timestamp if len(leftc) > 0 else -1
            self.features['timetofirstrightclic'] = rightc[0].timestamp if len(rightc) > 0 else -1
            self.features['timetofirstdoubleclic'] = doublec[0].timestamp if len(doublec) > 0 else -1
            self.features['timetofirstkeypressed'] = keyp[0].timestamp if len(keyp) > 0 else -1
        else:
            self.features['numevents'] = 0
            self.features['numleftclic'] = 0
            self.features['numrightclic'] = 0
            self.features['numdoubleclic'] = 0
            self.features['numkeypressed'] = 0
            self.features['leftclicrate'] = -1
            self.features['rightclicrate'] = -1
            self.features['doubleclicrate'] = -1
            self.features['keypressedrate'] = -1
            self.features['timetofirstleftclic'] = -1
            self.features['timetofirstrightclic'] = -1
            self.features['timetofirstdoubleclic'] = -1
            self.features['timetofirstkeypressed'] = -1


    def calc_validity_proportion(self, all_data):
        """Calculates the proportion of "Datapoint"s which are valid.

        Args:
            all_data: The list of "Datapoint"s which make up this Segment

        Returns:
            A float indicating the proportion of valid samples over all the samples in this Segment
        """
        num_valid = float(0)
        num = 0

        for d in all_data:
            #if d.stimuliname == 'ScreenRec':
            #if d.stimuliname == 'Screen Recordings (1)'
            if d.stimuliname != '':
                num += 1
                if d.is_valid:
                    num_valid += 1
#            else:
#                print "###",d.event, d.data1
        if num == 0:
            return 0.0
        else:
            return num_valid / num


    def calc_largest_validity_gap(self, all_data):
        """Calculates the largest gap of invalid samples in the "Datapoint"s for this Segment.

        Args:
            all_data: The list of "Datapoint"s which make up this Segement

        Returns:
            An integer indicating the length of largest invalid gap for this Segment in milliseconds
        """
        if self.numfixations == 0:
            return all_data[-1].timestamp - all_data[0].timestamp
        self.time_gaps = []
        self.all_invalid_gaps = []
        max_size = 0
        dindex = 0
        datalen = len(all_data)
        while dindex < datalen:
            d = all_data[dindex]
            while d.is_valid and (dindex < datalen - 1):
                dindex += 1
                d = all_data[dindex]
            if not (d.is_valid):
                gap_start = d.timestamp
                while not (d.is_valid) and (dindex < datalen - 1):
                    dindex += 1
                    d = all_data[dindex]
                if d.timestamp - gap_start > max_size:
                    max_size = d.timestamp - gap_start
                if d.timestamp - gap_start > params.MAX_SEG_TIMEGAP:
                    self.time_gaps.append((gap_start, d.timestamp))
            dindex += 1
        return max_size


    def calc_blink_validity_gaps(self, all_data):
        """Calculates the blink validity gaps for this segment

        Args:
            all_data: The list of "Datapoint"s which make up this Segement

        Returns:
            An array for tuples (int, int) indicating beginning and end timestamps for each contiguous invalid group of rows
        """

        blinks_validity_gaps = []
        dindex = 0
        datalen = len(all_data)
        while dindex < datalen:
            d = all_data[dindex]
            while d.is_valid_blink and (dindex < datalen - 1):
                dindex += 1
                d = all_data[dindex]
            if not (d.is_valid_blink):
                gap_start = d.timestamp
                while not (d.is_valid_blink) and (dindex < datalen - 1):
                    dindex += 1
                    d = all_data[dindex]
                blinks_validity_gaps.append((gap_start, d.timestamp))
            dindex += 1
        return blinks_validity_gaps

    def getgaps(self):
        """Returns the list of invalid gaps > params.MAX_SEG_TIMEGAP for this Segment

        Args:
            a list of invalid gaps for this Segment
        """
        return self.time_gaps

    def getallgaps(self):
        """Returns the total length of all invalid gaps for this Segment

        Args:
            an integer: the length in ms of invalid points for this Segment
        """
        return self.all_invalid_gaps

    def get_length_invalid(self):
        """Returns the sum of the length of the invalid gaps > params.MAX_SEG_TIMEGAP

        Args:
            an integer, the length in milliseconds
        """
        length = 0
        for gap in self.getgaps():
            length += gap[1] - gap[0]
        return length

    def calc_validity_fixation(self, all_data):
        """Calculates the proportion of (valid + restored) "Datapoint"s over all "Datapoint"s of the Segment.

        Restored samples are the samples which are not valid but they are part of a Fixation.
        The idea is that if the user was looking at a certain point and then we loose the eye data for
        a short period of time and afterwards the user is looking at the same point we can assume that user
        was looking at that same point during that period.

        Args:
            all_data: The list of "Datapoint"s which make up this Segement

        Returns:
            A float indicating the proportion of (valid + restored) samples over all the samples in this Segment
        """
        if self.numfixations == 0:
            return 0.0
        num_valid = float(0)
        num = 0

        for d in all_data:
            #if d.stimuliname == 'ScreenRec':
            if d.stimuliname != '':
                num += 1
                if d.is_valid or d.fixationindex!=None:
                    num_valid += 1.0
#            else:
#                print "###",d.event, d.data1
        if num == 0:
            return 0.0
        else:
            return num_valid / num

    def calc_validity1(self, threshold = params.VALID_PROP_THRESH):
        """Returns a boolean indicating whether this Segment is valid using proportion of valid samples threshold

        Args:
            threshold: the minimum proportion of valid samples for a Segment or Scene to be
                considered valid. By default set to value VALID_PROP_THRESH from module params.py
        """
        return self.proportion_valid > threshold

    def calc_validity2(self, threshold = params.VALID_TIME_THRESH):
        """Returns a boolean indicating whether this Segment is valid using largest acceptable gap threshold
        """
        return self.largest_data_gap <= threshold


    def calc_validity3(self, threshold = params.VALID_PROP_THRESH):
        """Returns a boolean indicating whether this Segment is valid using proportion of (valid + restored) samples threshold
        """
        return self.proportion_valid_fix > threshold

    def get_validity(self):
        """Determines if this Segment is valid with the given validity method set in params.VALIDITY_METHOD

        Returns:
            A boolean indicating whether this Segment is valid
        """
        if params.VALIDITY_METHOD == 1:
            return self.validity1
        elif params.VALIDITY_METHOD == 2:
            return self.validity2
        elif params.VALIDITY_METHOD == 3:
            return self.validity3

    def calc_distances(self, fixdata):
        """returns the Euclidean distances between a sequence of "Fixation"s

        Args:
            fixdata: a list of "Fixation"s
        """
        distances = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1, len(fixdata)):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            dist = math.sqrt((x - lastx)**2 + (y - lasty)**2)
            distances.append(dist)
            lastx = x
            lasty = y

        return distances

    def calc_abs_angles(self, fixdata):
        """returns the absolute angles between a sequence of "Fixation"s that build a scan path.

        Abosolute angle for each saccade is the angle between that saccade and the horizental axis

        Args:
            fixdata: a list of "Fixation"s

        Returns:
            a list of absolute angles for the saccades formed by the given sequence of "Fixation"s in Radiant
        """
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
        """returns the relative angles between a sequence of "Fixation"s that build a scan path in Radiant

        Relative angle for each saccade is the angle between that saccade and the previous saccade.

        Defined as: angle = acos(v1 dot v2)  such that v1 and v2 are normalized vector2coord

        Args:
            fixdata: a list of "Fixation"s

        Returns:
            a list of relative angles for the saccades formed by the given sequence of "Fixation"s in Radiant
        """
        rel_angles = []
        lastx = fixdata[0].mappedfixationpointx
        lasty = fixdata[0].mappedfixationpointy

        for i in xrange(1, len(fixdata) - 1):
            x = fixdata[i].mappedfixationpointx
            y = fixdata[i].mappedfixationpointy
            nextx = fixdata[i + 1].mappedfixationpointx
            nexty = fixdata[i + 1].mappedfixationpointy
            v1 = (lastx - x, lasty - y)
            v2 = (nextx - x, nexty - y)

            if v1 != (0.0, 0.0) and v2 != (0.0, 0.0):
                v1_dot = math.sqrt(geometry.simpledotproduct(v1, v1))
                v2_dot = math.sqrt(geometry.simpledotproduct(v2, v2))
                normv1 = ((lastx - x) / v1_dot, (lasty - y) / v1_dot)
                normv2 = ((nextx - x) / v2_dot, (nexty - y) / v2_dot)
                dotproduct = geometry.simpledotproduct(normv1, normv2)
                if dotproduct < -1:
                    dotproduct = -1.0
                if dotproduct > 1:
                    dotproduct = 1.0
                theta = math.acos(dotproduct)
                rel_angles.append(theta)
            else:
                rel_angles.append(0.0)
            lastx = x
            lasty = y

        return rel_angles

    def calc_num_samples(self, all_data):
        """Returns the number of samples in the Segment

        Args:
            all_data: a list of "Datapoint"s which make up this Segment.

        Returns:
            An integer determining the number of samples in the Segment

        """
        num = 0
        for d in all_data:
            if d.stimuliname != '':
                num += 1
        return num

    def generate_aoi_sequence(self, fixdata, aois):
        """returns the sequence of AOI's where "Fixation"s occurred
        Args:
            fixdata: a list of "Fixation"s
        Returns:
            a list of AOI names that correspond to the sequence of "Fixation" locations
        """
        sequence = []
        for fix in fixdata:
            for aoi in aois:
                if _fixation_inside_aoi(fix, aoi.polyin, aoi.polyout) and aoi.is_active(fix.timestamp, fix.timestamp) :
                    sequence.append(aoi.aid)
        return sequence

    def getid(self):
        """Returns the segid for this Segment

        Returns: a string conataining the segid for this Segment
        """
        return self.segid

    def get_features(self, featurelist = None, aoifeaturelist = None, aoifeaturelabels = None):
        """Returns feature names and their values for this Segment

        Args:
            featurelist: if not None, a list containing the name of features to be returned. If this is None all features will be returned
            aoifeaturelist: if not None, a list of features to be returned for each of the "AOI"s relevant to this Segment.
            aoifeaturelabels: if not None, a list of AOI related features to be returned.
            *Note: while aoifeaturelist is a subset of features that will be returned for all relevant "AOI"s, aoifeaturelabels contains
            the exact AOI feature name, i.e., a feature of the form: [AOI name]_[feature name]
            For example if an AOI called 'graph' is releveant to this Segment, aoifeaturelabels may contain 'graph_fixationrate'

        Returns:
            featnames: a list of feature names sorted alphabetically
            featvals: a corrsponding list of feature values
            e.g.
            featnames = ['fixationrate', 'length', 'meanabspathangles']
            featvals  = [0.00268522882294', '1529851', '1.60354714212']

        """
        if featurelist == []:
            featnames = []
        elif not featurelist:       #include all features
            featnames = self.features.keys()
        else:                       #a list of features was given
            featnames = []
            for name in featurelist:
                if name in self.features.keys():
                    featnames.append(name)
                else:
                    raise Exception('Segment %s has no such feature: %s'%(self.getid(),name))

        featnames.sort()

        featvals = map(lambda x: self.features[x], featnames)

        if self.has_aois:
            for aid, aoi in self.aoi_data.iteritems():
                if aoifeaturelabels:    #an exact list of aoifeatures was given
                    anames, avals = aoi.get_features()
                    anames = map(lambda x: '%s_%s'%(aid, x), anames)
                    featval = zip(anames,avals)
                    newfeatval = filter(lambda x: x[0] in aoifeaturelabels,featval)
                    anames = []
                    avals = []
                    for fn,fv in newfeatval:
                        anames.append(fn)
                        avals.append(fv)
                    if featnames:
                        featnames += anames
                        featvals += avals
                else:                   #a list of features for each AIO was given
                    anames, avals = aoi.get_features(aoifeaturelist)
                    anames = map(lambda x: '%s_%s'%(aid, x), anames)

                    featnames += anames
                    featvals += avals

        return featnames, featvals

    def print_(self):
        """Ourputs all feature names and their values for this Segment on the console
        """
        print("ID", self.getid())
        print("start",self.start)
        print("end",self.end)
        print("is_valid",self.is_valid)
        print
#        featurelist =["completion_time","numfixations","length","numsamples"]
#        if self.features['numfixations'] > 0:
#            featurelist.extend(["meanfixationduration","stddevfixationduration","sumfixationduration","fixationrate"])
#
#        featurelist.extend(["meanpathdistance","sumpathdistance","stddevpathdistance","sumabspathangles","meanabspathangles","stddevabspathangles","sumrelpathangles","meanrelpathangles","stddevrelpathangles"])

        fn,fv = self.get_features()
        for i in xrange(len(fn)):
            print(fn[i],':',fv[i])
        print
