'''
UBC Eye Movement Data Analysys Toolkit
Created on 2011-09-30

@author: skardan
'''

import math, geometry
from utils import *
from Segment import *
from copy import deepcopy


class Scene(Segment):
    '''
    A class that combines multiple segments and calculates the aggregated statistics for this new entity as a whole
    '''

                
    def __init__(self, scid, seglist, all_data, fixation_data, Segments = None, aoilist = None, prune_length= None, require_valid = True, auto_partition = False):

        '''
        @type scid: str
        @param scid: The id of the scene.
        @type segements: List of Segment.Segement
        @param scid: The segments belonging to this scene
        @type all_data: array of L{Datapoints<Datapoint.Datapoint>}
        @param all_data: The datapoints which make up this Trial.
        @type fixation_data: array of L{Fixations<Datapoint.Fixation>}
        @param fixation_data: The fixations which make up this Trial.
        @type aois: array of L{AOIs<AOI.AOI>}
        @param aois: The AOIs relevant to this trial
        @type prune_length: int
        '''
        
        def partition_segement(new_seg, seg_start,seg_end):
            timegaps = new_seg.getgaps()
            subsegments = []
            sub_segid=0
            samp_inds = []
            fix_inds = []
            last_samp_idx = 0
            last_fix_idx = 0
            sub_seg_time_start = seg_start
            for timebounds in timegaps:
                sub_seg_time_end = timebounds[0] #end of this sub_seg is start of this gap
                last_samp_idx, all_start,all_end = get_chunk(all_data, last_samp_idx, sub_seg_time_start, sub_seg_time_end)
                last_fix_idx, fix_start, fix_end = get_chunk(fixation_data, last_fix_idx, sub_seg_time_start, sub_seg_time_end)
                sub_seg_time_start = timebounds[1] #beginning of the next sub_seg is end of this gap
                if fix_end - fix_start>0:
                    new_sub_seg = Segment(segid, all_data[all_start:all_end],
                                      fixation_data[fix_start:fix_end], aois=aoilist, prune_length=prune_length)
                else:
                    continue
                subsegments.append(new_sub_seg)
                samp_inds.append((all_start,all_end))
                fix_inds.append((fix_start, fix_end))
                sub_segid +=1
            # handling the last sub_seg
            sub_seg_time_end = seg_end #end of last sub_seg is the end of seg
            last_samp_idx, all_start,all_end = get_chunk(all_data, last_samp_idx, sub_seg_time_start, sub_seg_time_end)
            last_fix_idx, fix_start, fix_end = get_chunk(fixation_data, last_fix_idx, sub_seg_time_start, sub_seg_time_end)
            if fix_end - fix_start>0: #add the last sub_seg
                new_sub_seg = Segment(segid, all_data[all_start:all_end],
                                  fixation_data[fix_start:fix_end], aois=aoilist, prune_length=prune_length)
                subsegments.append(new_sub_seg)
                samp_inds.append((all_start,all_end))
                fix_inds.append((fix_start, fix_end))
            #end of handling the last sub_seg
                
            return subsegments, samp_inds, fix_inds
        
        if len(all_data)<=0:
            raise Exception('A scene with no sample data!')
        if Segments == None:
            self.segments = []
#            print "seglist",seglist
            for (segid, start, end) in seglist:
                print "segid, start, end:",segid, start, end
                _, all_start, all_end = get_chunk(all_data, 0, start, end)
                _, fix_start, fix_end = get_chunk(fixation_data, 0, start, end)
                if fix_end - fix_start>0:
                    new_seg = Segment(segid, all_data[all_start:all_end],
                                      fixation_data[fix_start:fix_end], aois=aoilist, prune_length=prune_length)
                else:
                    continue
                
                if (new_seg.largest_data_gap > params.MAX_SEG_TIMEGAP) and auto_partition: #low quality segment that needs to be partitioned!
                    new_segs, samp_inds, fix_inds = partition_segement(new_seg, start, end) 
                    for nseg,samp,fix in zip(new_segs, samp_inds, fix_inds):
                            nseg.set_indices(samp[0],samp[1],fix[0],fix[1])
                            self.segments.append(nseg)
                else:   #good quality segment OR no auto_partition
                    new_seg.set_indices(all_start,all_end,fix_start,fix_end)
                    self.segments.append(new_seg)
        else:
            self.segments = Segments #segments are already generated
        
        if require_valid:
            segments = filter(lambda x:x.is_valid,self.segments)
        else:
            segments = self.segments
        if len(segments)==0:
            raise Exception('no segments in scene %s!' %(scid))
        
        fixationlist = []
        sample_list = []
        totalfixations = 0
        firstsegtime = float('infinity')
        firstseg = None 
        for seg in segments:
            sample_st,sample_end,fix_start,fix_end = seg.get_indices()
            if params.DEBUG:
                print "sample_st,sample_end,fix_start,fix_end",sample_st,sample_end,fix_start,fix_end
            sample_list.append(all_data[sample_st:sample_end])
            fixationlist.append(fixation_data[fix_start:fix_end])
            totalfixations += len(fixationlist[-1])
            if seg.start < firstsegtime:
                firstsegtime = seg.start
                firstseg = seg
        
        self.firstseg = firstseg
        self.scid = scid
        self.features = {}
        self.largest_data_gap = maxfeat(self.segments,'largest_data_gap')   #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.proportion_valid = weightedmeanfeat(self.segments,'numsamples','proportion_valid') #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.proportion_valid_fix = weightedmeanfeat(self.segments,'numsamples','proportion_valid_fix') #self.segments is used to calculate validity of the scenes instead of segments which is only valid segments
        self.validity1 = self.calc_validity1()
        self.validity2 = self.calc_validity2()
        self.validity3 = self.calc_validity3()
        self.is_valid = self.get_validity()

        self.length = sumfeat(segments,'length')
        if self.length == 0:
            raise Exception('Zero length segments!')
        self.features['numsegments'] = len(segments)
        self.features['length'] = self.length
        self.start = minfeat(segments,'start')
        self.numfixations = sumfeat(segments,'numfixations')
        self.end = maxfeat(segments,'end')
        self.numsamples = sumfeat(segments, 'numsamples')
        self.features['numsamples'] = self.numsamples
        
        self.numfixations = sumfeat(segments, 'numfixations')
        self.features['numfixations'] = self.numfixations
        if self.numfixations != totalfixations:
            raise Exception('error in fixation count for scene:'+self.scid)
            #warn ('error in fixation count for scene:'+self.scid)
        self.features['fixationrate'] = float(self.numfixations) / self.length
        if self.numfixations > 0:
            self.features['meanfixationduration'] = weightedmeanfeat(segments,'numfixations',"features['meanfixationduration']")
            self.features['stddevfixationduration'] = stddev(map(lambda x: float(x.fixationduration), reduce(lambda x,y: x+y ,fixationlist)))##
            self.features['sumfixationduration'] = sumfeat(segments, "features['sumfixationduration']")
            self.features['fixationrate'] = float(self.numfixations)/self.length
            distances = self.calc_distances(fixationlist)
            abs_angles = self.calc_abs_angles(fixationlist)
            rel_angles = self.calc_rel_angles(fixationlist)
        else:
            self.features['meanfixationduration'] = 0
            self.features['stddevfixationduration'] = 0
            self.features['sumfixationduration'] = 0
            self.features['fixationrate'] = 0
            distances = []
        if len(distances) > 0:
            self.features['meanpathdistance'] = mean(distances)
            self.features['sumpathdistance'] = sum(distances)
            self.features['stddevpathdistance'] = stddev(distances)
            self.features['sumabspathangles'] = sum(abs_angles)
            self.features['meanabspathangles'] = mean(abs_angles)
            self.features['stddevabspathangles'] = stddev(abs_angles)
            self.features['sumrelpathangles'] = sum(rel_angles)
            self.features['meanrelpathangles'] = mean(rel_angles)
            self.features['stddevrelpathangles'] = stddev(rel_angles)
        else:
            self.features['meanpathdistance'] = 0
            self.features['sumpathdistance'] = 0
            self.features['stddevpathdistance'] = 0
            self.features['sumabspathangles'] = 0
            self.features['meanabspathangles']= 0
            self.features['stddevabspathangles']= 0
            self.features['sumrelpathangles'] = 0
            self.features['meanrelpathangles']= 0
            self.features['stddevrelpathangles'] = 0
        self.has_aois = False
        if aoilist:
            self.set_aois(segments, aoilist,fixationlist)
            
    def getid(self):
        return self.scid
    
    def set_aois(self, segments, aois, fixationlist):
        """
        @type fixation_data: array of L{Fixations<Datapoint.Fixation>}
        @param fixation_data: The fixations which make up this segement.
        @type aois: array of L{AOIs<AOI.AOI>}
        @param aois: The AOIs relevant to this segement
        """
        if len(aois) == 0:
            print "no AOI:",self.segid
        self.aoi_data={}
        for seg in segments:
            for aid in seg.aoi_data.keys():
                if aid in self.aoi_data:
                    self.aoi_data[aid] = merge_aoistats(self.aoi_data[aid],seg.aoi_data[aid], self.features['length'],self.numfixations)
                else:
                    self.aoi_data[aid] = deepcopy(seg.aoi_data[aid])
        
        firstsegaois = self.firstseg.aoi_data.keys()            
        for aid in self.aoi_data.keys():
            if aid in firstsegaois:
                self.aoi_data[aid].features['timetofirstfixation'] = deepcopy(self.firstseg.aoi_data[aid].features['timetofirstfixation'])
            else:
                self.aoi_data[aid].features['timetofirstfixation'] = float('inf')
                
        #maois.features['averagetimetofirstfixation'] = ?
        #maois.features['averagettimetolastfixation'] = ?
            self.has_aois = True

    def calc_distances(self, fixdatalists):
        """
        Calculate the Euclidean distances between subsequent L{Fixations<Fixation.Fixation>}.
    
        @type fixdata: Array of L{Fixations<Fixation.Fixation>}.
        @param fixdata: The array of L{Fixations<Fixation.Fixation>}.
        """
        distances = []
        for fixdata in fixdatalists:
            #print "fixdata", fixdata
            if not(fixdata):
                continue
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
    
    def calc_abs_angles(self, fixdatalists):
        abs_angles = []
        for fixdata in fixdatalists:
            if not(fixdata):
                continue
            lastx = fixdata[0].mappedfixationpointx
            lasty = fixdata[0].mappedfixationpointy
    
            for i in xrange(1,len(fixdata)):
                x = fixdata[i].mappedfixationpointx
                y = fixdata[i].mappedfixationpointy
                (_, theta) = geometry.vector_difference((lastx,lasty), (x, y))
                abs_angles.append(abs(theta))
                lastx=x
                lasty=y

        return abs_angles

    def calc_rel_angles(self, fixdatalists):
        rel_angles = []
        
        for fixdata in fixdatalists:
            if not(fixdata):
                continue
            lastx = fixdata[0].mappedfixationpointx
            lasty = fixdata[0].mappedfixationpointy
    
            for i in xrange(1, len(fixdata)-1):
                x = fixdata[i].mappedfixationpointx
                y = fixdata[i].mappedfixationpointy
                nextx = fixdata[i+1].mappedfixationpointx
                nexty = fixdata[i+1].mappedfixationpointy
                (_, theta) = geometry.vector_difference((x,y), (lastx, lasty))
                (_, nextheta) = geometry.vector_difference((x,y), (nextx, nexty))
                theta = abs(theta-nextheta)
                rel_angles.append(theta)
                lastx=x
                lasty=y

        return rel_angles   

def merge_aoistats(main_AOI_Stat,new_AOI_Stat,total_time,total_numfixations):
        maois = main_AOI_Stat
        maois.features['numfixations'] += new_AOI_Stat.features['numfixations']
        maois.features['longestfixation'] = max(maois.features['longestfixation'],new_AOI_Stat.features['longestfixation'])
        maois.features['totaltimespent'] += + new_AOI_Stat.features['totaltimespent'] 
        maois.features['proportiontime'] = float(maois.features['totaltimespent'])/total_time
        maois.features['proportionnum'] = float(maois.features['numfixations'])/total_numfixations
        if maois.features['totaltimespent']>0: 
            maois.features['fixationrate'] = float(maois.features['numfixations'])/maois.features['totaltimespent']
        else:
            maois.features['fixationrate'] = 0.0
                
                
            
        #calculating the transitions to and from this AOI and other active AOIs at the moment
        transition_aois = filter(lambda x: x.startswith(('numtransto_','numtransfrom_')),new_AOI_Stat.features.keys())
        if params.DEBUG:
            print 'transition_aois',transition_aois
        sumtransto = 0
        sumtransfrom = 0
        for feat in transition_aois:
            if feat in maois.features:
                maois.features[feat] += new_AOI_Stat.features[feat]
            else:
                maois.features[feat] = new_AOI_Stat.features[feat]
            if feat.startswith('numtransto_'):
                sumtransto += maois.features[feat]
            else:
                sumtransfrom += maois.features[feat]
        
        for feat in transition_aois:
            if feat.startswith('numtransto_'):
                aid = feat.lstrip('numtransto_')
                if sumtransto > 0:

                    maois.features['proptransto_%s'%(aid)] = float(maois.features[feat]) / sumtransto
                else:
                    maois.features['proptransto_%s'%(aid)] = 0
            else:
                aid = feat.lstrip('numtransfrom_')
                if sumtransfrom > 0:
                    
                    maois.features['proptransto_%s'%(aid)] = float(maois.features[feat]) / sumtransfrom
                else:
                    maois.features['proptransfrom_%s'%(aid)] = 0
        ###endof trnsition calculation
        return maois

def weightedmeanfeat(obj_list, totalfeat,ratefeat):
    '''
    Calculates the weighted average of the ratefeat over the Segments
    @param obj_list: 
    @param totalfeat: 
    @param ratefeat: 
    '''
    num_valid = float(0)
    num = 0

    for obj in obj_list:
        t = eval('obj.'+totalfeat)
        num_valid += t * eval('obj.'+ratefeat)
        num += t
    if num != 0:
        return num_valid / num
    return 0
    

def sumfeat(obj_list, feat):
    sum = 0
    for obj in obj_list:
        sum += eval('obj.'+feat)
    return sum

def minfeat(obj_list, feat):
    min = float('+infinity')
    for obj in obj_list:
        val = eval('obj.'+feat)
        if min > val:
            min = val
    return min     
    
def maxfeat(obj_list, feat):
    max = float('-infinity')
    for obj in obj_list:
        val = eval('obj.'+feat)
        if max < val:
            max = val
    return max          