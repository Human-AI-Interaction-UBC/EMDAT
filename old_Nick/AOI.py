from utils import *

class AOI():
    def __init__(self, aid, polyin, polyout, fixation_data, starttime, endtime,
    aois):
        self.aid = aid
        self.polyin = polyin
        self.polyout = polyout
        
        fixation_indices = filter(lambda i: fixation_in_aoi(fixation_data[i],
        polyin, polyout), range(len(fixation_data)))

        fixations = map(lambda i: fixation_data[i], fixation_indices)

        self.numfixations = len(fixations)
        self.longestfixation = -1
        self.timetofirstfixation = -1
        self.timetolastfixation = -1
        self.proportionnum = 0
        self.totaltimespent = sum(map(lambda x: x.fixationduration, fixations))
        self.proportiontime = float(self.totaltimespent)/(endtime - starttime)
        if self.numfixations > 0:
            self.longestfixation = max(map(lambda x: x.fixationduration,
            fixations))
            self.timetofirstfixation = fixations[0].timestamp - starttime
            self.timetolastfixation = fixations[-1].timestamp - starttime
            self.proportionnum = float(self.numfixations)/len(fixation_data)

        self.numtransto = {}
        self.numtransfrom = {}

        for (aid, x, y) in aois:
            self.numtransto[aid] = 0
            self.numtransfrom[aid] = 0

        for i in fixation_indices:
            if i > 0:
                for (aid, polyin, polyout) in aois:
                    if fixation_in_aoi(fixation_data[i-1], polyin, polyout):
                        self.numtransfrom[aid]+=1
            if i < len(fixation_data)-2:
                for (aid, polyin, polyout) in aois:
                    if fixation_in_aoi(fixation_data[i+1], polyin, polyout):
                        self.numtransto[aid]+=1

        self.proptransto = {}
        self.proptransfrom = {}
        sumtransto = sum(self.numtransto.values())
        sumtransfrom = sum(self.numtransfrom.values())

        for key, val in self.numtransto.items():
            if sumtransto > 0:
                self.proptransto[key] = float(self.numtransto[key]) / sumtransto
            else:
                self.proptransto[key] = 0
            
        for key, val in self.numtransfrom.items():
            if sumtransfrom > 0:
                self.proptransfrom[key] = float(self.numtransfrom[key]) / sumtransfrom
            else:
                self.proptransfrom[key] = 0
            

def fixation_in_aoi(fixation, polyin, polyout):
        return point_inside_polygon(fixation.mappedfixationpointx,
        fixation.mappedfixationpointy, polyin) and not point_inside_polygon(fixation.mappedfixationpointx,
        fixation.mappedfixationpointy, polyout)
            
