'''
UBC Eye Movement Data Analysys Toolkit
Recording class
Nicholas FitzGerald - nicholas.fitzgerald@gmail.com

Class to hold all the data from a given recording
Modified by Samad Kardan to a general class independent of the study
'''


from data_structures import *
from Scene import *
from Dynamic_Segment import *
from AOI import *
import AIspace
from utils import *


class Recording():
    def __init__(self, all_file, fixation_file, media_offset = (0,0)):
        """
        @type all_file: str
        @type fixation_file: str
        @param all_file: The filename of the 'All-Data.tsv' file output by the
        Tobii software.
        @param fixation_file: The filename of the 'Fixation-Data.tsv' file output by the
        Tobii software.
        """
        self.all_data = read_all_data(all_file)
        self.fix_data = read_fixation_data(fixation_file, media_offset = params.MEDIA_OFFSET)

    def process_rec(self, segfile = None, scenelist = None,  aoifile = None, aoilist = None , prune_length = None,
                     require_valid_segs = True, auto_partition_low_quality_segments = False):
        """
        @type segfile: 
        @param segfile: Filename containing segment definitions in format:
            <Scene_ID>\t<Segment_ID>\t<start time>\t<end time>
            e.g.:
            s1    seg1    0    5988013
        @type aoifile: string
        @param aoifile: the filename of a file defining the Areas of Interest.
        """        

        if segfile != None:
            scenelist = read_segs(segfile)
            print "Done reading the segments!"
        elif scenelist == None:
            print "Error in scene file"
        
        if aoifile!= None:
            aoilist = read_aois_Tobii(aoifile)
            print "Done reading the AOIs!"
        elif aoilist == None:
            aoilist = []
            print "No AOIs defined!"

#        all_ind = 0
#        fix_ind = 0
        scenes = []
        for scid,sc in scenelist.iteritems():
            print "Preparing scene:"+str(scid)
            if params.DEBUG:
                print "len(all_data)",len(self.all_data)
            try:
                newSc = Scene(scid, sc, self.all_data,self.fix_data, aoilist=aoilist, 
                              prune_length=prune_length, require_valid = require_valid_segs,
                               auto_partition = auto_partition_low_quality_segments)               
            except Exception as e:
                warn(e)
                newSc = None 
                pass 
#                raise         
            if newSc:
                scenes.append(newSc)
        segs = []
        for sc in scenes:
            segs.extend(sc.segments)
#            for (segid, start, end) in sc:
#                print "segid, start, end:",segid, start, end
#                _, all_start, all_end = get_chunk(self.all_data, 0, start, end)
#                _, fix_start, fix_end = get_chunk(self.fix_data, 0, start, end)
#                new_seg = Segment(segid, self.all_data[all_start:all_end],
#                                  self.fix_data[fix_start:fix_end], aois=aoilist, prune_length=prune_length)
#                new_seg.set_indices(all_start,all_end,fix_start,fix_end)
#                ret.append(new_seg)
        return segs , scenes
     
    def process_dynamic(self, segfile = None, scenes = None,  aoifile = None, aoilist = None , prune_length = None, media_offset = (0,0)):
        """

        @type segfile: 
        @param segfile: Filename containing segment definitions in format:
            pid\t[<starttime>, <endtime>]

        @type aoifile: string
        @param aoifile: the filename of a file defining the Areas of Interest.
        """
        if segfile != None:
            scenes = read_segs(segfile)
            print "Done reading the segments!"
        elif scenes == None:
            print "Error in scene file"
            
        ret = []
        
        if aoifile!= None:
            aoilist = read_aois_Tobii(aoifile)
            print "Done reading the AOIs!"
        elif aoilist == None:
            aoilist = []
            print "No AOIs defined!"

#        all_ind = 0
#        fix_ind = 0
        for sc in scenes.values():
            for (segid, start, end) in sc:
                print "segid, start, end:",segid, start, end
                _, all_start, all_end = get_chunk(self.all_data, 0, start, end)
                _, fix_start, fix_end = get_chunk(self.fix_data, 0, start, end)
                ret.append(Dynamic_Segment(segid, self.all_data[all_start:all_end],
                self.fix_data[fix_start:fix_end], aois=aoilist,
                prune_length=prune_length))
        return ret
           
            



def read_all_data(all_file):
    """
    Returns an array of L{Datapoints<Datapoint.Datapoint>} read from the data
    file.

    @type all_file: str
    @param all_file: The filename of the 'All-Data.tsv' file output by the
    Tobii software.
    """
    with open(all_file, 'r') as f:
        lines = f.readlines()

    alld = map(Datapoint, lines[(params.ALLDATAHEADERLINES+params.NUMBEROFEXTRAHEADERLINES):])
    return filter(lambda x: x.number!=None,alld)

# read_fixation_data(all_file)
# pre:
#      fixation_file = filename for the "Fixation-Data.tsv" file holding the data
# post:
#      returns an array of Fixationss corresponding to the lines of the datafile
def read_fixation_data(fixation_file, media_offset = (0,0)):
    """
    Returns an array of L{Fixations<Datapoint.Fixation>} read from the fixation
    file.

    @type fixation_file: str
    @param fixation_file: The filename of the 'Fixation-Data.tsv' file output
    by the Tobii software.
    """
    with open(fixation_file, 'r') as f:
        lines = f.readlines()

    return map(lambda x: Fixation(x, media_offset=media_offset), lines[params.FIXATIONHEADERLINES:])


def read_aois(aoifile):
    aoidict = {}
    with open(aoifile, 'r') as f:
        aoilines = f.readlines()

    aids = aoilines[0].strip().split('t')
   
    for l in aoilines[1:]:
        l = l.strip()
        chunks = l.split('\t')
        chart_type = chunks[0][:9]
        #join the aids to the ploys
        polys = map(lambda x, (y,z): (x,y,z), aids, map(eval, chunks[1:]))
        aoidict[chart_type] = polys

    return aoidict

def read_aois_Tobii(aoifile):
    '''
    aoiname[\t]point1x,point1y[\t]point2x,point2y[\t]...[\n]
    #[\t]start1,end1[\t]...[\n]
    '''
    aoilist = []
    with open(aoifile, 'r') as f:
        aoilines = f.readlines()

   
    polyin=[]
    last_aid = ''
    for l in aoilines:
        l = l.strip()
        chunks = l.split('\t')
        if chunks[0].startswith('#'): #second line
            if polyin:
                seq=[]
                for v in chunks[1:]:
                    seq.append((eval(v)))
                aoi=AOI(last_aid, polyin, [],seq)
                aoilist.append(aoi)
                polyin=[]
            else:
                raise Exception('error in the AOI file')
        else:
            if polyin: #a global AOI
                aoi=AOI(last_aid, polyin, [],[])
                aoilist.append(aoi)
                polyin=[]
            print "AOIs",chunks #first line
            last_aid = chunks[0]
            for v in chunks[1:]:
                polyin.append((eval(v)))
    if polyin: #the last (global) AOI            
        aoi=AOI(last_aid, polyin, [],[])
        aoilist.append(aoi)
    
    return aoilist


def read_segs(segfile):
    scenes = {}
    with open(segfile, 'r') as f:
        seglines = f.readlines() 
 
    for l in seglines:
        l = l.strip()
        l = l.split('\t')
        if l[0] in scenes:
            scenes[l[0]].append((l[1], int(l[2]), int(l[3]) ))
        else:
            scenes[l[0]]=[(l[1], int(l[2]), int(l[3]) )]
    return scenes




