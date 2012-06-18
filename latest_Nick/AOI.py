from util import *

NONTEMP_FEATURES = ['longestfixation', 'proportionnum', 'proportiontime',
'proptransto', 'proptransfrom']

class AOI():
    def __init__(self, aid, polyin, polyout, fixation_data, starttime, endtime,
    aois):
        self.aid = aid
        self.polyin = polyin
        self.polyout = polyout
        
        fixation_indices = filter(lambda i: fixation_in_aoi(fixation_data[i],
        polyin, polyout), range(len(fixation_data)))

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


        for (aid, x, y) in aois:
            self.features['numtransto_%s'%(aid)] =0
            self.features['numtransfrom_%s'%(aid)] = 0

        sumtransto = 0
        sumtransfrom = 0
        for i in fixation_indices:
            if i > 0:
                for (aid, polyin, polyout) in aois:
                    key = 'numtransfrom_%s'%(aid)
                    #self.features[key] = 0 #????? Samad
                    if fixation_in_aoi(fixation_data[i-1], polyin, polyout):
                        self.features[key] += 1
                        sumtransfrom += 1
            if i < len(fixation_data)-2:
                for (aid, polyin, polyout) in aois:
                    key = 'numtransto_%s'%(aid)
                    #self.features[key] = 0 #????? Samad
                    if fixation_in_aoi(fixation_data[i+1], polyin, polyout):
                        self.features[key] += 1
                        #sumtransfrom += 1 #????? Samad
                        sumtransto += 1

        for (aid, x, y) in aois:
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

    def get_features(self, featurelist = None):
        if featurelist == 'NONTEMP':
            featurelist = NONTEMP_FEATURES

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
                    raise Exception('AOI %s has no such feature: %s'%(self.aid,
                    name))

        featnames.sort()

        featvals = map(lambda x: self.features[x], featnames)

        return featnames, featvals
            

def fixation_in_aoi(fixation, polyin, polyout):
        return point_inside_polygon(fixation.mappedfixationpointx,
        fixation.mappedfixationpointy, polyin) and not point_inside_polygon(fixation.mappedfixationpointx,
        fixation.mappedfixationpointy, polyout)
            
