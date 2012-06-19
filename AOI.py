'''
UBC Eye Movement Data Analysys Toolkit
The Generic Area of Interest Class
Created on 2011-08-26  

@author: skardan
'''
from utils import *




class AOI():

    def __init__(self, aid, polyin, polyout, timeseq=[], time_coordinate_seq =[]):
        '''
        time_coordinate_seq:[((strat1,end1),polyin1,polyout1),(...),...]
        '''
        self.aid = aid
        self.polyin = polyin
        self.polyout = polyout
        self.timeseq = timeseq
        self.time_coordinate_seq = time_coordinate_seq
        if time_coordinate_seq:
            raise Exception ("not implemented yet! Samad")
        print "timeseq", timeseq
#            self.partial = True
    def set_coordinates(self, polyin, polyout):
            self.polyin = polyin
            self.polyout = polyout
            
    def is_active(self,start,end):
        if start == -1:
            return False
        if self.timeseq:
            for intr in self.timeseq:
                if (start>=intr[0] and start<intr[1])or(end>intr[0] and end<=intr[1]):
                    return True
            return False #not active
        else:
            return True #global AOI
        
    def is_active_partition(self,start,end):
        #if (end - start)== 0:
        if start == -1:
            return False, []
        if params.DEBUG:
            print "in:",self.aid
        ovelap_part = []
        if self.timeseq:
            for intr in self.timeseq:
                if (start>=intr[0] and start<intr[1])or(end>intr[0] and end<=intr[1]):
                    if (start>=intr[0] and end<=intr[1]):
                        ovelap_part=[]
                    else:
                        print "partial:",start,end,":",intr[0],intr[1]
                        ovstart = max(start,intr[0])
                        ovend  = min(end,intr[1])
                        ovelap_part = [ovstart,ovend]
                    return True, ovelap_part
            return False, [] #not active
        else:
            return True, [] #global AOI
    
                   
class AOI_Stat():
    def __init__(self,aoi,seg_fixation_data, starttime, endtime, active_aois):
        """
        @param aois:list of the AOIs used for calculating the transitions between this AOI and other AOIs, this is filled during the segmentation 
        """
        self.aoi = aoi
        self.isActive, partition = self.aoi.is_active_partition(starttime, endtime)
        self.aoi
        if not(self.isActive):
            return
        self.isActive = True
        
        if partition:
            print "partition",partition
            _,st,en = get_chunk(seg_fixation_data, 0, partition[0],partition[1])
            fixation_data = seg_fixation_data[st:en]
            if params.DEBUG:
                print "len(seg_fixation_data)",seg_fixation_data
                print "len(fixation_data)",fixation_data
        else:  #global AOI
            fixation_data = seg_fixation_data 
        fixation_indices = filter(lambda i: fixation_in_aoi(fixation_data[i],self.aoi.polyin, self.aoi.polyout), range(len(fixation_data)))

        fixations = map(lambda i: fixation_data[i], fixation_indices)
    
        self.features = {}

        numfixations = len(fixations)
        self.features['numfixations'] = numfixations
        self.features['longestfixation'] = -1
        self.features['timetofirstfixation'] = -1
        self.features['timetolastfixation'] = -1
        self.features['proportionnum'] = 0
        totaltimespent = sum(map(lambda x: x.fixationduration, fixations))
        self.features['totaltimespent'] = totaltimespent 
        
        self.features['proportiontime'] = float(totaltimespent)/(endtime - starttime)
        if numfixations > 0:
            self.features['longestfixation'] = max(map(lambda x: x.fixationduration,
            fixations))
            self.features['timetofirstfixation'] = fixations[0].timestamp - starttime
            self.features['timetolastfixation'] = fixations[-1].timestamp - starttime
            self.features['proportionnum'] = float(numfixations)/len(fixation_data)
            self.features['fixationrate'] = numfixations / float(totaltimespent)
        else:
            self.features['longestfixation'] = 0
            self.features['timetofirstfixation'] = 0
            self.features['timetolastfixation'] = 0
            self.features['proportionnum'] = 0
            self.features['fixationrate'] = 0
                
                
            
        #calculating the transitions to and from this AOI and other active AOIs at the moment
        for aoi in active_aois:
            aid = aoi.aid
            self.features['numtransto_%s'%(aid)] =0
            self.features['numtransfrom_%s'%(aid)] = 0

        sumtransto = 0
        sumtransfrom = 0
        for i in fixation_indices:
            if i > 0:
                for aoi in active_aois:
                    aid = aoi.aid
                    polyin = aoi.polyin
                    polyout = aoi.polyout
                    key = 'numtransfrom_%s'%(aid)
                    #self.features[key] = 0 #????? Samad
                    if fixation_in_aoi(fixation_data[i-1], polyin, polyout):
                        self.features[key] += 1
                        sumtransfrom += 1
            if i < len(fixation_data)-2:
                for aoi in active_aois:
                    aid = aoi.aid
                    polyin = aoi.polyin
                    polyout = aoi.polyout
                    key = 'numtransto_%s'%(aid)
                    #self.features[key] = 0 #????? Samad
                    if fixation_in_aoi(fixation_data[i+1], polyin, polyout):
                        self.features[key] += 1
                        sumtransto += 1

        for aoi in active_aois:
            aid = aoi.aid
            if sumtransto > 0:
                val = self.features['numtransto_%s'%(aid)]
                self.features['proptransto_%s'%(aid)] = float(val) / sumtransto
            else:
                self.features['proptransto_%s'%(aid)] = 0

            if sumtransfrom > 0:
                val = self.features['numtransfrom_%s'%(aid)]
                self.features['proptransfrom_%s'%(aid)] = float(val) / sumtransfrom
            else:
                self.features['proptransfrom_%s'%(aid)] = 0
        ###endof trnsition calculation


    def get_features(self, featurelist = None):
        if featurelist == 'NONTEMP':
            featurelist = params.NONTEMP_FEATURES_AOI

        if featurelist == []:
            return [], []
        elif not featurelist:
            featnames = self.features.keys()
        else:
            featnames = []
            for name in featurelist:
                if name == 'numtransto':
                    featnames += filter(lambda x: x[:10] == 'numtransto', self.features.keys())
                elif name == 'numtransfrom':
                    featnames += filter(lambda x: x[:12] == 'numtransfrom', self.features.keys())
                elif name == 'proptransfrom':
                    featnames += filter(lambda x: x[:11] == 'proptransto', self.features.keys())
                elif name == 'proptransto':
                    featnames += filter(lambda x: x[:13] == 'proptransfrom', self.features.keys())
                elif name in self.features.keys():
                    featnames.append(name)
                else:
                    raise Exception('AOI %s has no such feature: %s'%(self.aoi.aid,
                    name))

        featnames.sort()

        featvals = map(lambda x: self.features[x], featnames)

        return featnames, featvals

    def print_(self):
        """
            print  "AOI ID:",self.aoi.aid
            print  "numfixations:",self.numfixations
            print  "longestfixation",self.longestfixation
            print  "timetofirstfixation",self.timetofirstfixation
            print  "timetolastfixation",self.timetolastfixation
            print  "proportionnum",self.proportionnum
            print  "totaltimespent",self.totaltimespent 
            print  "proportiontime",self.proportiontime 
            if self.numfixations > 0:
                print  "longestfixation",self.longestfixation 
                print  "timetofirstfixation",self.timetofirstfixation 
                print  "timetolastfixation",self.timetolastfixation 
                print  "proportionnum",self.proportionnum 
        """
        print  "AOI ID:",self.aoi.aid
        fn,fv = self.get_features()
        for i in xrange(len(fn)):
            print fn[i],':',fv[i]
        print
            
def fixation_in_aoi(fixation, polyin, polyout):
        return point_inside_polygon(fixation.mappedfixationpointx,
        fixation.mappedfixationpointy, polyin) and not point_inside_polygon(fixation.mappedfixationpointx,
        fixation.mappedfixationpointy, polyout)
     
         
