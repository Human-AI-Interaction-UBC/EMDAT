"""
UBC Eye Movement Data Analysys Toolkit
Recording class

Author: Nicholas FitzGerald - nicholas.fitzgerald@gmail.com
Modified by: Samad Kardan to a general class independent of the study

Class to hold all the data from one recording (i.e, one complete experiment session)

"""


from data_structures import *
from Scene import *
#from Dynamic_Segment import *
from AOI import *
from utils import *


class Recording():
    def __init__(self, all_file, fixation_file, media_offset = (0,0)):
        """
        Args:
            all_file: a string containing the filename of the 'All-Data.tsv' 
                file output by the Tobii software.
                
            fixation_file: a string containing the filename of the 
                'Fixation-Data.tsv' file output by the Tobii software.
                
            media_offset: the coordinates of the top left corner of the window
                showing the interface under study. (0,0) if the interfacce was
                in full screen (default value)
            
        Yields:
            a Recording object
        """
        self.all_data = read_all_data(all_file)
        self.fix_data = read_fixation_data(fixation_file, 
                                           media_offset = params.MEDIA_OFFSET)

    def process_rec(self, segfile = None, scenelist = None,  aoifile = None, 
                    aoilist = None , prune_length = None, require_valid_segs = True, 
                    auto_partition_low_quality_segments = False):
        """Processes the data for one recording (i.e, one complete experiment session)
        
                
        Args:
            segfile: If not None, a string containing the name of the segfile 
                with segment definitions in following format:
                <Scene_ID>\t<Segment_ID>\t<start time>\t<end time>\n
                e.g.:
                s1    seg1    0    5988013
                With one segment definition per line
            scenelist: If not None, a list of Scene objects
            *Note: Both segfile and scenelist cannot be None
                
            aoifile: If not None, a string conatining the name of the aoifile 
                with definitions of the "AOI"s.
            aoilist: If not None, a list of "AOI"s.
            *Note: if aoifile is not None, aoilist will be ignored
             
            prune_length: If not None, an integer that specifies the time 
                interval (in ms) from the begining of each Segment in which
                samples are considered in calculations.  This can be used if, 
                for example, you only wish to consider data in the first 
                1000 ms of each Segment. In this case (prune_length = 1000),
                all data beyond the first 1000ms of the start of the "Segment"s
                will be disregarded.
            
            require_valid_segs: a boolean determining whether invalid "Segment"s
                will be ignored when calculating the features or not. default = True 
            
            auto_partition_low_quality_segments: a boolean flag determining whether
                EMDAT should automatically split the "Segment"s which have low sample quality
                into two new ssub "Segment"s discarding the largest invalid sample gap in 
                the "Segment". default = False
        Returns:
            a list of Scene objects for this Recording
            a list of Segment objects for this recording. This is an aggregated list
            of the "Segment"s of all "Scene"s in the Recording 
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
                              prune_length=prune_length, 
                              require_valid = require_valid_segs,
                              auto_partition = auto_partition_low_quality_segments)               
            except Exception as e:
                warn(e)
                newSc = None 
                if params.DEBUG:
                    raise
                else:
                    pass        
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
#                                  self.fix_data[fix_start:fix_end], aois=aoilist,
#                                  prune_length=prune_length)
#                new_seg.set_indices(all_start,all_end,fix_start,fix_end)
#                ret.append(new_seg)
        return segs , scenes
     
#    def process_dynamic(self, segfile = None, scenes = None,  aoifile = None, 
#                        aoilist = None , prune_length = None, media_offset = (0,0)):
#        """Processes the data for one recording (i.e, one complete experiment session)
#        
#                
#        Args:
#            segfile: If not None, a string containing the name of the segfile 
#                with segment definitions in following format:
#                <Scene_ID>\t<Segment_ID>\t<start time>\t<end time>\n
#                e.g.:
#                s1    seg1    0    5988013
#                With one segment definition per line
#            scenelist: If not None, a list of Scene objects
#            *Note: Both segfile and scenelist cannot be None
#                
#            aoifile: If not None, a string conatining the name of the aoifile 
#                with definitions of the "AOI"s.
#            aoilist: If not None, a list of "AOI"s.
#            *Note: if aoifile is not None, aoilist will be ignored
#             
#            prune_length: If not None, an integer that specifies the time 
#                interval (in ms) from the begining of each segment in which
#                samples are considered in calculations.  This can be used if, 
#                for example, you only wish to consider data in the first 
#                1000 ms of each segment. In this case (prune_length = 1000),
#                all data beyond the first 1000ms of the start of the "Segment"s
#                will be disregarded.
#            
#            require_valid_segs: a boolean flag determining whether invalid "Segment"s
#                will be ignored when calculating the features or not. default = True
#                 
#            auto_partition_low_quality_segments: a boolean flag determining whether
#                EMDAT should automatically split the "Segment"s which have low sample quality
#                into two new ssub "Segment"s discarding the largest invalid sample gap in 
#                the "Segment". default = False
#        Returns:
#            a list of Dynamic_Segment objects 
#        """   
#        if segfile != None:
#            scenes = read_segs(segfile)
#            print "Done reading the segments!"
#        elif scenes == None:
#            print "Error in scene file"
#            
#        ret = []
#        
#        if aoifile!= None:
#            aoilist = read_aois_Tobii(aoifile)
#            print "Done reading the AOIs!"
#        elif aoilist == None:
#            aoilist = []
#            print "No AOIs defined!"
#
##        all_ind = 0
##        fix_ind = 0
#        for sc in scenes.values():
#            for (segid, start, end) in sc:
#                print "segid, start, end:",segid, start, end
#                _, all_start, all_end = get_chunk(self.all_data, 0, start, end)
#                _, fix_start, fix_end = get_chunk(self.fix_data, 0, start, end)
#                ret.append(Dynamic_Segment(segid, self.all_data[all_start:all_end],
#                                           self.fix_data[fix_start:fix_end], aois=aoilist,
#                                           prune_length=prune_length))
#        return ret
           
            



def read_all_data(all_file):
    """Returns a list of "Datapoint"s read from an "All-Data" file.

    Args:
        all_file:A string containing the name of the 'All-Data.tsv' file output by the
            Tobii software.
    Returns:
        a list of "Datapoint"s
    """
    with open(all_file, 'r') as f:
        lines = f.readlines()

    alld = map(Datapoint, lines[(params.ALLDATAHEADERLINES+
                                 params.NUMBEROFEXTRAHEADERLINES):])
    return filter(lambda x: x.number!=None,alld)


def read_fixation_data(fixation_file, media_offset = (0,0)):
    """Returns a list of "Fixation"s read from an "Fixation-Data" file. 

    Args:
        fixation_file: A string containing the name of the 'Fixation-Data.tsv' file output by the
            Tobii software.
        media_offset: the coordinates of the top left corner of the window
                showing the interface under study. (0,0) if the interfacce was
                in full screen (default value) 
    Returns:
        a list of "Fixation"s
    """

    with open(fixation_file, 'r') as f:
        lines = f.readlines()

    return map(lambda x: Fixation(x, media_offset=media_offset), 
               lines[params.FIXATIONHEADERLINES:])


#def read_aois(aoifile):
#    """Returns a dict of 
#
#    Args:
#        aoifile: A string containing the name of the AOI file.
#        
#    Returns:
#        a dict of
#    """
#    aoidict = {}
#    with open(aoifile, 'r') as f:
#        aoilines = f.readlines()
#
#    aids = aoilines[0].strip().split('t')
#   
#    for l in aoilines[1:]:
#        l = l.strip()
#        chunks = l.split('\t')
#        chart_type = chunks[0][:9]
#        #join the aids to the ploys
#        polys = map(lambda x, (y,z): (x,y,z), aids, map(eval, chunks[1:]))
#        aoidict[chart_type] = polys
#
#    return aoidict

def read_aois_Tobii(aoifile):
    """Returns a list of "AOI"s read from a '.aoi' file.
    
    The '.aoi' files have pairs of lines of the form:
    aoiname[tab]point1x,point1y[tab]point2x,point2y[tab]...[new line]
    #[tab]start1,end1[tab]...[new line]
    
    The first line determines name of the AOI and the coordinates of each vertex of 
    the polygon that determines the boundaries of the AOI.
    The second line which starts with a '#' is optional and determines the time
    intervals when the AOI is active. If the second line does not exist the AOI will
    be active throughout the whole session (global AOI). 
    *Note: If the AOIs are exported from Tobii software the '.aoi' file will only have the 
    first line for each AOI and you need to override this method to generate AOIs that are
    active only at certain times (non-global AOI). 

    Args:
        aoifile: A string containing the name of the '.aoi' file
        
    Returns:
        a list of "AOI"s
    """
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
    """Returns a dict with scid as the key and segments as value from a '.seg' file.
    
    The '.seg' files have lines of the form:
    scene_name[\t]segment_name[\t]start_time[\t]end_time[\n]
    
    scene_name is the id of the Scene that this Segment belongs to,
    segment_name is the id of the Segement,
    and tart_time and end_time determines the time interval for the Segment

    Args:
        segfile: A string containing the name of the '.seg' file
        
    Returns:
        a dict with scid as the key and segments as value 
    """
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




