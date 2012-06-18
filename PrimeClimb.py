'''
UBC Eye Movement Data Analysys Toolkit
Created on Sep 23, 2011

@author: MaryMuir
'''
from data_structures import *
import Recording
params=__import__('params')
import Participant
from AOI import AOI
from Mountain import Mountain
from Scene import Scene
from utils import *
from math import ceil, floor


class Participant_PC(Participant.Participant):
    def __init__(self, pid, eventfile, datafile, fixfile, actionsfile = None, log_time_offset = None, aoifiles = None, prune_length= None, 
                 require_valid_segs = True, auto_partition_low_quality_segements = False):
        '''
        pid, eventfile, datafile, fixfile, actionsfile = None, log_time_offset = None, aoifiles = None, prune_length= None
        '''
        
        print "reading the files"
        self.features={}
        rec = Recording.Recording(datafile, fixfile, params.MEDIA_OFFSET)
        print "Done!"
        mountains, scenelist,self.numofsegments = partition_PC(eventfile,actionsfile,log_time_offset)
        print "partition done!"
        if aoifiles != None:
            aois = read_aois_Tobii_PC(mountains, aoifiles)
        else:
            aois = None
        self.features['numofsegments']= self.numofsegments
        #print "numSegments: ", self.numofsegments
        self.id = pid
        self.segments, self.scenes = rec.process_rec(scenelist = scenelist,aoilist = aois,prune_length = prune_length, require_valid_segs = require_valid_segs, 
                                                     auto_partition_low_quality_segments = auto_partition_low_quality_segements)
        
        self.whole_scene = Scene('P'+str(pid),[],rec.all_data,rec.fix_data, Segments = self.segments, aoilist = aois,prune_length = prune_length, require_valid = require_valid_segs )
        self.scenes.insert(0,self.whole_scene)       
               
    def is_valid(self,threshold=None):
        if threshold == None:
            return self.whole_scene.is_valid
        else:
            return self.whole_scene.proportion_valid_fix >= threshold               
class Dynamic_Participant_PC(Participant_PC):
    def __init__(self, pid, eventfile, datafile, fixfile, aoifiles = None, prune_length= None):
        
        self.features={}
        rec = Recording.Recording(datafile, fixfile, params.MEDIA_OFFSET)
        self.mountains, self.scenes,self.numofsegments = partition_PC(eventfile)
        if aoifiles != None:
            aois = read_aois_Tobii_PC(self.mountains, aoifiles)
        else:
            aois = None
        self.features['numofsegments']= self.numofsegments
        self.id = pid
        self.Dynamic_segments = rec.process_dynamic(scenes = self.scenes,aoilist= aois,prune_length = prune_length, media_offset = params.MEDIA_OFFSET)

def read_participants_PC(datadir, user_list, pids, prune_length = None, aoifiles = None, log_time_offsets=None,
                          use_actions = False, require_valid_segs = True, auto_partition_low_quality_segements = False):
    
    participants = []
    if log_time_offsets == None: #setting the default offset to 1 sec.
        log_time_offsets = [1]*len(pids)
        
    for rec,pid, offset in zip(user_list,pids, log_time_offsets):
        print "pid:", pid
        if rec<10:
            allfile = datadir+'/Pilot0'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Pilot0'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Pilot0'+str(rec)+'-Event-Data.tsv'
        else:
            allfile = datadir+'/Pilot'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Pilot'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Pilot'+str(rec)+'-Event-Data.tsv'
        print allfile
        import os.path
        if os.path.exists(allfile):
            actfile = None
            if(use_actions):
                actfile = datadir+'/actions/Log_'+str(pid)+'.m'
            print aoifiles, " in read_participants_PC"
            p = Participant_PC(pid, evefile, allfile, fixfile, actionsfile = actfile, log_time_offset = offset,
                               aoifiles=aoifiles, prune_length = prune_length, require_valid_segs = require_valid_segs,
                                auto_partition_low_quality_segements = auto_partition_low_quality_segements)
            participants.append(p)
        pid += 1
    return participants

#    def __init__(self, pid, eventfile, datafile, fixfile, actionsfile = None, log_time_offset = None, aoifiles = None, prune_length= None, 
#                 require_valid_segs = True, auto_partition_low_quality_segements = False):


def test_validityA(datadir, prune_length = None, user_list = xrange(7,19),
                  aoifiles = None ,auto_partition_low_quality_segements = False):
    
    participants = []
    pid = 7
    seglen = 0
    segs = 0
    for rec in user_list:
        print "pid:", pid
        if rec<10:
            allfile = datadir+'Pilot0'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'Pilot0'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'Pilot0'+str(rec)+'-Event-Data.tsv'
        else:
            allfile = datadir+'Pilot'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'Pilot'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'Pilot'+str(rec)+'-Event-Data.tsv'
        print allfile
        import os.path
        if os.path.exists(allfile):
            p = Participant_PC(pid, evefile, allfile, fixfile, aoifiles=aoifiles, prune_length = prune_length,
                                require_valid_segs = False,
                                auto_partition_low_quality_segements = auto_partition_low_quality_segements)
            tvalidity = []
            
            for seg in p.segments:
                seglen += seg.completion_time
            segs += len(p.scenes)
#            for tresh in range(1,100,1):##proportion
#                invc = 0
#                invsegs=[]
#                for seg in segments:
#                    if seg.calc_validity1(tresh/100.0) == False:
#                        invc +=1
#            for tresh in range(1,21,1):##prop-gap
#                invc = 0
#                invsegs=[]
#                for seg in segments:
#                    if seg.calc_validity2(tresh*seg.completion_time/100.0) == False:
#                        invc +=1                        
#            for tresh in range(1,20000,100):##time-gap
#                invc = 0
#                invsegs=[]
#                for seg in segments:
#                    if seg.calc_validity2(tresh) == False:
#                        invc +=1

            for tresh in range(1,102,1):##proportion Fixation
                invc = 0
                invsegs=[]
                for seg in p.scenes:
                    if seg.calc_validity3(tresh/100.0) == False:
                        invc +=1                        
                        invsegs.append(seg.scid)
                        
                if len(invsegs)>0:
                    print "seg:",invsegs 
                        
                tvalidity.append((tresh, invc))
            participants.append( (pid,tvalidity, len(p.scenes) ) )
            print ( (tvalidity, len(p.scenes)) )
           
        pid += 1
        if(segs>0):
            print "average seg len",seglen/float(segs)
        else:
            print "seg Len = 1"
    return participants

def test_validity2(datadir, prune_length = None, user_list = xrange(7,38)):
    
    participants = []
    pid = 55
    seglen = 0
    segs = 0
    for rec in user_list:
        print "pid:", pid
        if rec<10:
            allfile = datadir+'/Pilot0'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Pilot0'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Pilot0'+str(rec)+'-Event-Data.tsv'
        else:
            allfile = datadir+'/Pilot'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Pilot'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Pilot'+str(rec)+'-Event-Data.tsv'
        print allfile
        import os.path
        if os.path.exists(allfile):
            p = Participant_PC(pid, evefile, allfile, fixfile, aoifiles=None, prune_length = prune_length)
            tvalidity = []
            
            for seg in p.segments:
                seglen += seg.completion_time
            segs += len(p.segments)
            
            for tresh in range(1,102,1):##proportion Fixation
                invc = 0
                if p.is_valid(tresh/100.0) == False:
                    invc +=1                        
                tvalidity.append((tresh, invc))
            participants.append( (pid,tvalidity, len(p.segments) ) )
            print ( (tvalidity, len(p.segments)) )
           
        pid += 1        
    return participants
                
def partition_PC(eventfile, actionfile = None, log_time_offset = None):
    """
    Generates the scenes based on the events log
    """
    events = read_events(eventfile)
    start_stamp = 0
    end_stamp = 0
    hintcount = 0
    mountain_start_stamp = 0
    mountain_end_stamp = 0
    
    def add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp, hintcount, seg_min_size = params.MINSEGSIZE): #adds the segment to the scene
        if end_stamp-start_stamp > seg_min_size:
            if current_scene in scenes:
                scenes[current_scene].append(('S'+str(seg_count), int(start_stamp), int(end_stamp) ))
            else:
                scenes[current_scene]=[('S'+str(seg_count), int(start_stamp), int(end_stamp) )]
                hintcount+=1
            seg_count+=1
        return scenes, seg_count, hintcount
    
    def add_mountain(mountains, current_mountain, mntnum, mountain_start_stamp, mountain_end_stamp):
        mount = Mountain("Mountain_"+str(mntnum), int(current_mountain), int(mountain_start_stamp), int(mountain_end_stamp))
        #mountains[current_mountain]=[("Mountain_"+str(mntnum), int(mountain_start_stamp), int(mountain_end_stamp))]
        mountains.append(mount)
        #print mount.print_()
        return mountains
         
    scenes = {}
    current_scene = ''
    seg_count = 0

    mountains = []
    current_mountain = ""
    mntnum = 0    
    
    openEv=False        
    for ev in events:
        if (ev.event == 'LogData'):
            # Code to deal with mountain data
            if (ev.data1 == "Mountain"):
                if mntnum == 0:
                    mountain_start_stamp = int(ev.timestamp)
                    mntnum = int(ev.data2)
                    current_mountain = ev.data2
                else:
                    mountain_end_stamp = int(ev.timestamp)-1
                    add_mountain(mountains, current_mountain, mntnum, mountain_start_stamp, mountain_end_stamp)
                    ### Break a hint into two parts if it spans a mountain
                    #print openEv
                    if openEv:
                        end_stamp = mountain_end_stamp
                        #print current_scene, ":", start_stamp
                        scenes, seg_count, hintcount = add_seg(scenes, current_scene, seg_count, start_stamp, end_stamp, hintcount)
                        start_stamp = ev.timestamp
                        #print start_stamp
                    ###
                    mountain_start_stamp = int(ev.timestamp)
                    mntnum = int(ev.data2)
                    current_mountain = ev.data2
            elif (ev.data1 == "GameEnd"):  
                    mountain_end_stamp = int(ev.timestamp)
                    add_mountain(mountains, current_mountain, mntnum, mountain_start_stamp, mountain_end_stamp) 
                    break       #finished all the processing so stop
            # Code to deal with hintstart / hintstop
            elif (ev.data1 == 'HintStart'):  #save the current segment and change the current_scene and start a new segment
                #print "HintStart-", ev.data2, "-", ev.timestamp
                seg_count = 0
                end_stamp = ev.timestamp
                start_stamp = ev.timestamp
                current_scene = ev.data2
                openEv=True                  
            elif (ev.data1 == 'HintEnd'): #save the current segment
                if (openEv==False):
                    print"ERROR in EVENT FILE, Seg:",seg_count
                    #print ev.event, "-", ev.timestamp, "-",ev.data1, "-",ev.data2, "-", ev.descriptor
                    exit()
                if ev.data2 != current_scene:
                    print"HintEnd not for HintStart", ev.data2
                    exit()
                end_stamp = ev.timestamp
                openEv=False
                scenes,seg_count, hintcount = add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp, hintcount)
                #seg_count = 0
                
    print "hint count = ", hintcount
    return mountains, scenes, seg_count-1  

def read_events(evfile):
    """
    Returns an array of L{Datapoints<Datapoint.Datapoint>} read from the event
    file.

    @type all_file: str
    @param all_file: The filename of the 'Event-Data.tsv' file output by the
    Tobii software.
    """
    with open(evfile, 'r') as f:
        lines = f.readlines()

    return map(Event, lines[(params.EVENTSHEADERLINES+params.NUMBEROFEXTRAHEADERLINES):])

def read_aois_Tobii_PC(mountains, aoifiles):
    '''
    aoiname[\t]point1x,point1y[\t]point2x,point2y[\t]...[\n]
    #[\t]start1,end1[\t]...[\n]
    '''
    aoilist = []

    
    f = open(aoifiles, 'r')
    aoilines = f.readlines()
    
    #print aoifiles
    #print aoilines
    for l in aoilines:
        l = l.strip()
        chunks = l.split('\t')
        polyin=[]
        print "AOIs",chunks #first line
        for v in chunks[1:]:
            polyin.append((eval(v)))
        AOIname = chunks[0]
        timeseqs = []
        polyout = []
        if (AOIname.startswith('Mountain_')):
            mountainNum = int(AOIname.strip('Mountain_'))
            
            for v in mountains:
                if int(v.mntNum)==mountainNum:
                    
                    timeseqs.append(v.mount_start)
                    timeseqs.append(v.mount_stop)
                    
            #    print v.print_    
            AOIname = AOIname.strip('_1234567890')
        
        aoi=AOI(AOIname, polyin, polyout, timeseqs)
        print aoi.aid,':',aoi.polyin,':',aoi.timeseq
        aoilist.append(aoi)

    return aoilist