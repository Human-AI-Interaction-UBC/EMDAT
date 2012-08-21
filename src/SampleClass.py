'''
UBC Eye Movement Data Analysys Toolkit
Created on 2011-08-26

@author: skardan
'''
from data_structures import *
import Recording
params=__import__('params')
import Participant
from AOI import AOI
from Scene import Scene
from utils import *
from math import ceil, floor


class Participant_CSP(Participant.Participant):
    def __init__(self, pid, eventfile, datafile, fixfile, actionsfile = None, log_time_offset = None, aoifiles = None, prune_length= None, 
                 require_valid_segs = True, auto_partition_low_quality_segments = False):
        '''
        pid, eventfile, datafile, fixfile, actionsfile = None, log_time_offset = None, aoifiles = None, prune_length= None
        '''
        
        print "reading the files"
        self.features={}
        rec = Recording.Recording(datafile, fixfile, params.MEDIA_OFFSET)
        print "Done!"
        scenelist,self.numofsegments,aoi_seqs = partition_CSP(eventfile,actionsfile,log_time_offset)
        print "partition done!"
        if aoifiles != None:
            aoi_seqs.append(aoi_seqs[0]+aoi_seqs[1])
            aois = read_aois_Tobii_CSP(aoifiles,aoi_seqs)
        else:
            aois = None
        self.features['numofsegments']= self.numofsegments
        self.id = pid
        self.segments, self.scenes = rec.process_rec(scenelist = scenelist,aoilist = aois,prune_length = prune_length, require_valid_segs = require_valid_segs, 
                                                     auto_partition_low_quality_segments = auto_partition_low_quality_segments)
        
        self.whole_scene = Scene('P'+str(pid),[],rec.all_data,rec.fix_data, Segments = self.segments, aoilist = aois,prune_length = prune_length, require_valid = require_valid_segs )
        self.scenes.insert(0,self.whole_scene)
        
    def is_valid(self,threshold=None):
        if threshold == None:
            return self.whole_scene.is_valid
        else:
            return self.whole_scene.proportion_valid_fix >= threshold

               
#class Dydnamic_Participant_CSP(Participant_CSP):
#    def __init__(self, pid, eventfile, datafile, fixfile, aoifiles = None, prune_length= None):
#        
#        self.features={}
#        rec = Recording.Recording(datafile, fixfile, params.MEDIA_OFFSET)
#        scenelist,self.numofsegments,aoi_seqs = partition_CSP(eventfile)
#        if aoifiles != None:
#            aois = read_aois_Tobii_CSP(aoifiles,aoi_seqs)
#        else:
#            aois = None
#        self.features['numofsegments']= self.numofsegments
#        self.id = pid
#        self.Dynamic_segments, self.scenes = rec.process_dynamic(scenes = scenelist,aoilist= aois,prune_length = prune_length, media_offset = params.MEDIA_OFFSET)

def read_participants_CSP(datadir, user_list ,pids, prune_length = None, aoifiles = None, log_time_offsets=None, 
                          externaldatadir="", use_actions = True, require_valid_segs = True, auto_partition_low_quality_segments = False):
    
    participants = []
    if log_time_offsets == None:    #setting the default offset which is 1 sec
        log_time_offsets = [1]*len(pids) 
        
    for rec,pid,offset in zip(user_list,pids,log_time_offsets):
        print "pid:", pid
        if rec<10:
            allfile = datadir+'/P0'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/P0'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/P0'+str(rec)+'-Event-Data.tsv'
        else:
            allfile = datadir+'/P'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/P'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/P'+str(rec)+'-Event-Data.tsv'
        print allfile
        import os.path
        if os.path.exists(allfile):
            actfile = None
            if use_actions:
                actfile = externaldatadir+'/Log_'+str(pid)+'.m'
            p = Participant_CSP(rec, evefile, allfile, fixfile, actionsfile = actfile, log_time_offset = offset, 
                                aoifiles=aoifiles, prune_length = prune_length, require_valid_segs = require_valid_segs,
                                auto_partition_low_quality_segments = auto_partition_low_quality_segments)
            participants.append(p)
        else:
            print "Error reading participant files for: "+pid
    return participants

def test_validity(datadir, prune_length = None, user_list = xrange(7,38),
                  auto_partition_low_quality_segments = False):
    
    participants = []
    pid = 55
    seglen = 0
    segs = 0
    for rec in user_list:
        print "pid:", pid
        if rec<10:
            allfile = datadir+'/Rec 0'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Rec 0'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Rec 0'+str(rec)+'-Event-Data.tsv'
        else:
            allfile = datadir+'/Rec '+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Rec '+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Rec '+str(rec)+'-Event-Data.tsv'
        print allfile
        import os.path
        if os.path.exists(allfile):
            p = Participant_CSP(pid, evefile, allfile, fixfile, aoifiles=None, prune_length = prune_length,
                                require_valid_segs = False,
                                auto_partition_low_quality_segments = auto_partition_low_quality_segments)
            tvalidity = []
            
            for seg in p.segments:
                seglen += seg.completion_time
            segs += len(p.segments)

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
                for seg in p.segments:
                    if seg.calc_validity3(tresh/100.0) == False:
                        invc +=1                        
                        invsegs.append(seg.segid)
                        
                if len(invsegs)>0:
                    print "seg:",invsegs 
                        
                tvalidity.append((tresh, invc))
            participants.append( (pid,tvalidity, len(p.segments) ) )
            print ( (tvalidity, len(p.segments)) )
           
        pid += 1
        print "average seg len",seglen/float(segs)
    return participants

def test_validity2(datadir, prune_length = None, user_list = xrange(7,38),
                   auto_partition_low_quality_segments = False):
    
    participants = []
    pid = 55
    seglen = 0
    segs = 0
    for rec in user_list:
        print "pid:", pid
        if rec<10:
            allfile = datadir+'/Rec 0'+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Rec 0'+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Rec 0'+str(rec)+'-Event-Data.tsv'
        else:
            allfile = datadir+'/Rec '+str(rec)+'-All-Data.tsv'
            fixfile = datadir+'/Rec '+str(rec)+'-Fixation-Data.tsv'
            evefile = datadir+'/Rec '+str(rec)+'-Event-Data.tsv'
        print allfile
        import os.path
        if os.path.exists(allfile):
            p = Participant_CSP(pid, evefile, allfile, fixfile, aoifiles=None, prune_length = prune_length,
                                auto_partition_low_quality_segments = auto_partition_low_quality_segments)
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

def partition_CSP(eventfile, actionfile = None, log_time_offset = None):
    """
    Generates the scenes based on the events log
    """
    events = read_events(eventfile)
    start_stamp = 0
    end_stamp = 0
    
    def add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp, seg_min_size = params.MINSEGSIZE): #adds the segment to the scene
        if end_stamp-start_stamp > seg_min_size:
            if current_scene in scenes:
                scenes[current_scene].append(('S'+str(seg_count), int(start_stamp), int(end_stamp) ))
            else:
                scenes[current_scene]=[('S'+str(seg_count), int(start_stamp), int(end_stamp) )]
            seg_count+=1
        return scenes,seg_count
    
    scenes = {}

    current_scene = ''
    seg_count = 0
    p1_seq=[]
    p1_start = -1
    p2_seq=[]
    p2_start = -1
    

    openEv=False        
    for ev in events:
        if (ev.event=='LogData'):
            if (ev.data1 == 'Load 1st Problem'):  #save the current segment and change the current_scene and start a new segment
                end_stamp = ev.timestamp
                
                if p2_start !=-1: #if there was a problem2 aoi setting before
                    p2_seq.append((p2_start,end_stamp))
                    p2_start = -1
                if p1_start == -1:    #if we are already in a problem1 aoi setting then ignore this, otherwise start the porblem1 setting
                    p1_start = end_stamp
                
                if len(scenes)>0:  #if this is the first time seeing this event there is no segment before this
                    scenes,seg_count = add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp)
                    

                start_stamp = ev.timestamp
                current_scene = 'problem1'
                
                
            elif (ev.data1 == 'Distracted Start'): #save the current segment
                if openEv:
                    print"ERROR in EVENT FILE, Seg:",seg_count
                    exit()
                end_stamp = ev.timestamp
                openEv=True
                
                scenes,seg_count = add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp)
                
            elif (ev.data1 == 'Distracted End'): #start a new segment
                start_stamp = ev.timestamp
                openEv= False
                
            elif (ev.data1 == 'Writing Start'): #save the current segment
                if openEv:
                    print"ERROR in  EVENT FILE, Seg:",seg_count
                    exit()
                end_stamp = ev.timestamp
                openEv=True
                
                scenes,seg_count = add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp)
                
            elif (ev.data1 == 'Writing End'): #start a new segment
                start_stamp = ev.timestamp
                openEv= False
                
            if (ev.data1 == 'Load 2nd Problem'):  #save the current segment and change the current_scene and start a new segment
                if openEv:
                    print"ERROR in EVENT FILE, Seg:",seg_count
                    exit()
                    
                end_stamp = ev.timestamp
                
                if p1_start !=-1: #if there was a problem1 aoi setting before
                    p1_seq.append((p1_start,end_stamp))
                    p1_start = -1
                if p2_start == -1:    #if we are already in a problem2 aoi setting then ignore this, otherwise start the porblem2 setting
                    p2_start = end_stamp                
                scenes,seg_count = add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp)
                
                start_stamp = ev.timestamp
                current_scene = 'problem2'
                
            elif (ev.data1 == 'End'): #save the last segment
                
                end_stamp = ev.timestamp
                
                if p2_start !=-1: #if there was a problem2 aoi setting before
                    p2_seq.append((p2_start,end_stamp))
                if p1_start !=-1: #if there was a problem1 aoi setting before
                    p1_seq.append((p1_start,end_stamp))
                
                scenes,seg_count = add_seg(scenes,current_scene,seg_count,start_stamp,end_stamp)
                break
    if actionfile != None:     #generate segments for actions
        seg_count = 0
        if log_time_offset == None:
            raise Exception("no time offset for actions!")
        uactions = read_actions_logs(actionfile);
        act_scenes = {}
        for sc in scenes.values():
            segs = sorted(sc, key=lambda seg: seg[1]) #sort by seg start
            print "segs",segs
            curr_ind = 0
            start_stamp = 0
            end_stamp = 0
            curr_action = 0
            for (_, start, end) in segs:
                start_stamp = 0
                end_stamp = 0
                curr_action = 0
                startsec = ceil(start/1000)
                endsec = floor(end/1000)
                curr_ind, start_ind, end_ind = get_chunk(uactions, curr_ind, startsec-log_time_offset, endsec-log_time_offset) #seg_time = (act_time+log_time_offset)*1000 
                for act in uactions[start_ind:end_ind]:
                    if start_stamp == 0:    # first action in this segemnt
                        start_stamp = (act.timestamp+log_time_offset)*1000
                        curr_action = act.action
                        continue
                    end_stamp = (act.timestamp+log_time_offset)*1000
                    if params.DEBUG:
                        print "curr_action",curr_action
                    if curr_action not in params.ACTIIONS:
                        raise Exception("Invalid action ID")
                    act_scenes, seg_count = add_seg(act_scenes,curr_action,seg_count,start_stamp,end_stamp, seg_min_size = 0) #create segment for the previous action
                    start_stamp = end_stamp
                    curr_action = act.action
                
        if params.DEBUG:
            if sum(map(lambda x:sum(map(lambda y:y[2]-y[1],x)),act_scenes.values())) > sum(map(lambda x:sum(map(lambda y:y[2]-y[1],x)),scenes.values())):
                raise Exception("Error in calculating the action sub-segments")
        return act_scenes, seg_count, [p1_seq,p2_seq]
       
    else:        
        return scenes, seg_count-1,[p1_seq,p2_seq]  #the scenes are tuples (segid, start , end), #segments, list of time sequences for each scene

    

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

def read_actions_logs(actionfile):
    """
    Returns an array of L{Actions<Datapoint.Datapoint>} read from the event
    file.

    @type all_file: str
    @param all_file: The filename of the 'Event-Data.tsv' file output by the
    Tobii software.
    """
    with open(actionfile, 'r') as f:
        lines = f.readlines()

    return map(Action, lines[(params.ACTIONHEADERLINES):])

def read_aois_Tobii_CSP(aoifiles,aoi_seqs):
    '''
    aoiname[\t]point1x,point1y[\t]point2x,point2y[\t]...[\n]
    #[\t]start1,end1[\t]...[\n]
    '''
    aoilist = []
    
    for problem in xrange(params.NUMBEROFPROBLEMS+1):
        with open(aoifiles[problem], 'r') as f:
            aoilines = f.readlines()
    
        for l in aoilines:
            l = l.strip()
            chunks = l.split('\t')
            polyin=[]
            print "AOIs",chunks #first line
            for v in chunks[1:]:
                polyin.append((eval(v)))
            aoi=AOI(chunks[0], polyin, [],aoi_seqs[problem])
            aoilist.append(aoi)

    return aoilist

class Action():
    """
    """
    def __init__(self, actstr):
        """
        """
        #Action TimeStartoffset
        #print eventstr.split('\t')
        [self.action, self.timestamp] = actstr.split('\t')
        self.timestamp = cast_int(self.timestamp)
        self.action = cast_int(self.action) #action is a nubmeric code!