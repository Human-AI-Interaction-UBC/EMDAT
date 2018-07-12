    def calc_fix_ang_path_features(self):
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
        """
        fixation_data = self.tobii_controller.EndFixations[self.fix_idx:]
        numfixations = len(fixation_data)
        self.fix_idx = len(self.tobii_controller.EndFixations)
        distances = []
        abs_angles = []
        rel_angles = []
        if numfixations > 0:
            emdat_interval_features['meanfixationduration'] = mean(map(lambda x: float(x[2]), fixation_data))
            emdat_interval_features['stddevfixationduration'] = stddev(map(lambda x: float(x[2]), fixation_data))
            emdat_interval_features['sumfixationduration'] = sum(map(lambda x: x[2], fixation_data))

            emdat_interval_features['fixationrate'] = float(numfixations) / (self.length - self.length_invalid)
            distances = calc_distances(fixation_data)
            abs_angles = calc_abs_angles(fixation_data)
            rel_angles = calc_rel_angles(fixation_data)
        else:
            #self.fixation_start = -1
            #self.fixation_end = -1
            emdat_interval_features['meanfixationduration'] = -1
            emdat_interval_features['stddevfixationduration'] = -1
            emdat_interval_features['sumfixationduration'] = -1
            emdat_interval_features['fixationrate'] = -1
        emdat_interval_features['numfixations'] = numfixations

        numfixdistances = len(distances)
        numabsangles = len(abs_angles)
        numrelangles = len(rel_angles)
        if len(distances) > 0:
            emdat_interval_features['meanpathdistance'] = mean(distances)
            emdat_interval_features['sumpathdistance'] = sum(distances)
            emdat_interval_features['stddevpathdistance'] = stddev(distances)
            emdat_interval_features['eyemovementvelocity'] = emdat_interval_features['sumpathdistance']/ (self.length - self.length_invalid)
            emdat_interval_features['sumabspathangles'] = sum(abs_angles)
            emdat_interval_features['abspathanglesrate'] = sum(abs_angles)/(self.length - self.length_invalid)
            emdat_interval_features['meanabspathangles'] = mean(abs_angles)
            emdat_interval_features['stddevabspathangles'] = stddev(abs_angles)
            emdat_interval_features['sumrelpathangles'] = sum(rel_angles)
            emdat_interval_features['relpathanglesrate'] = sum(rel_angles)/(self.length - self.length_invalid)
            emdat_interval_features['meanrelpathangles'] = mean(rel_angles)
            emdat_interval_features['stddevrelpathangles'] = stddev(rel_angles)
            emdat_interval_features['numfixdistances'] = numfixdistances
            emdat_interval_features['numabsangles'] = numabsangles
            emdat_interval_features['numrelangles'] = numrelangles
        else:
            emdat_interval_features['meanpathdistance'] = -1
            emdat_interval_features['sumpathdistance'] = -1
            emdat_interval_features['stddevpathdistance'] = -1
            emdat_interval_features['eyemovementvelocity'] = -1
            emdat_interval_features['sumabspathangles'] = -1
            emdat_interval_features['abspathanglesrate'] = -1
            emdat_interval_features['meanabspathangles'] = -1
            emdat_interval_features['stddevabspathangles'] = -1
            emdat_interval_features['sumrelpathangles'] = -1
            emdat_interval_features['relpathanglesrate'] = -1
            emdat_interval_features['meanrelpathangles'] = -1
            emdat_interval_features['stddevrelpathangles'] = -1
            emdat_interval_features['numfixdistances'] = 0
            emdat_interval_features['numabsangles'] = 0
            emdat_interval_features['numrelangles'] = 0
        print("PATH DISTANCE FEATURES WHOLE SCENE")
        print "mean fixatiom duration %f" % emdat_interval_features['meanfixationduration']
        print "stddevfixationduration %f" %emdat_interval_features['stddevfixationduration']
        print "sumfixationduration %f" %emdat_interval_features['sumfixationduration']
        print "fixationrate %f" %emdat_interval_features['fixationrate']
        print "numfixations %f" %emdat_interval_features['numfixations']
        print "meanpathdistance %f" %emdat_interval_features['meanpathdistance']
        print "sumpathdistance %f" %emdat_interval_features['sumpathdistance']
        print "stddevpathdistance %f" %emdat_interval_features['stddevpathdistance']
        print "eyemovementvelocity %f" %emdat_interval_features['eyemovementvelocity']
        print "sumabspathangles %f" %emdat_interval_features['sumabspathangles']
        print "abspathanglesrate %f" %emdat_interval_features['abspathanglesrate']
        print "meanabspathangles %f" %emdat_interval_features['meanabspathangles']
        print "stddevabspathangles %f" %emdat_interval_features['stddevabspathangles']
        print "sumrelpathangles %f" %emdat_interval_features['sumrelpathangles']
        print "relpathanglesrate %f" %emdat_interval_features['relpathanglesrate']
        print "meanrelpathangles %f" %emdat_interval_features['meanrelpathangles']
        print "stddevrelpathangles %f" %emdat_interval_features['stddevrelpathangles']
        print "numfixdistances %f" %emdat_interval_features['numfixdistances']
        print "numabsangles %f" %emdat_interval_features['numabsangles']
        print "numrelangles %f" %emdat_interval_features['numrelangles']
        print
