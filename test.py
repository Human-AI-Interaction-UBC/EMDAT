'''
Created on 2011-08-25

@author: skardan
'''
from AIspace import *
from Participant import export_features_all, write_features_tsv

ul =        [7 ,8 ,9 ,10,12,13,14,15,18,22,23,24,25,26,27,28,29,31,32,33,34,35,36,37,40,41,42,43,44,45,46,47,48,51,52,53,54,55, 56, 57, 58, 59, 60, 61, 62] #                    38,39                   49,50 should be merged
uids =      [55,57,58,59,61,62,63,64,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,85,86,87,88,89,90,91,92,93,95,96,97,98,99,100,101,102,103,104,105,106] #.m files: uid+27    83,84 no action file    94
alogoffset =[1 ,1 , 1, 1, 0, 0, 4, 1, 2, 1, 2, 1, 1, 1, 1,16, 2, 1, 2, 1, 0, 1, 2, 2, 2, 3, 5, 1, 3, 1, 3, 2, 1, 4, 2, 2, 4,  3,  2,  1,  2,  1, 4,  3,  2]

#uids = [62]
#alogoffset = [0]
#ul=[13]#, 57, 58, 59]
#ul=[8]
#uids=[57]
#alogoffset=[1]

########### Validuty of users
#pv = test_validity2(user_list=ul,datadir='./data/', prune_length = None, 
#                    auto_partition_low_quality_segments = True)
#
#for rate in xrange(1,102,1): ##porportion
#    usr=[]
#    totalseg = 0
#    inv_user = 0
#    for p in pv:
#        pid, i,t = p
#        totalseg += t
#        _,invc = i[rate-1] 
#        if invc > 0 :
#            inv_user+=1
#            usr.append(invc)
#        else:
#            usr.append(0)
#        
##    print rate*100,":",inv_seg,"/",totalseg,"user:",inv_user,":",usr
#    print rate,"segs:",totalseg,"users:",inv_user,":",usr
###########


################### Segements Validity info
#pv = test_validity(user_list=ul,datadir='./data/', prune_length = None,
#                   auto_partition_low_quality_segments = True)
#
#print
#
##for rate in xrange(1,21,1): ##porportion gap
#for rate in xrange(1,102,1): ##porportion
##for rate in xrange(1,200,1): ##time gap 
#    usr=[]
#    totalseg = 0
#    inv_seg = 0
#    inv_user = 0
#    for p in pv:
#        pid, i,t = p
#        totalseg += t
#        _,invc = i[rate-1] 
#        inv_seg += invc
#        if invc > 0 :
#            inv_user+=1
#            usr.append(invc)
#        else:
#            usr.append(0)
#        
##    print rate*100,":",inv_seg,"/",totalseg,"user:",inv_user,":",usr
#    print rate,":",inv_seg,"/",totalseg,"user:",inv_user,":",usr
##################


###### Read participants without action events
ps = read_participants_CSP(user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir='./data/', 
                           use_actions = False, prune_length = None, aoifiles = ['./data/Static_1.aoi','./data/Static_2.aoi','./data/general.aoi'],
                           require_valid_segs = True, auto_partition_low_quality_segments = True)
print
######


####### READ All Participants
#ps = read_participants_CSP(user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir='./data/', 
#                           use_actions = True,prune_length = None, aoifiles = ['./data/Static_1.aoi','./data/Static_2.aoi','./data/general.aoi'],
#                           auto_partition_low_quality_segments = True)
#print
#


##### WRITE features to file
write_features_tsv(ps, 'csp_eye.tsv',featurelist = params.featurelist, aoifeaturelabels=params.aoifeaturelist, id_prefix = False)



###### PRINT features on the screen
#fn,fv = export_features_all(ps, featurelist = params.featurelist, aoifeaturelabels=params.aoifeaturelist, id_prefix = False, require_valid = True)
#print fn
#for v in fv:
#    print v
######


####### Read participants without action events for validity check
#ps = read_participants_CSP(user_list = ul,pids = uids, log_time_offsets = alogoffset, datadir='./data/', 
#                           use_actions = False, prune_length = None, aoifiles = ['./data/Static_1.aoi','./data/Static_2.aoi','./data/general.aoi'],
#                           require_valid_segs = False, auto_partition_low_quality_segments = True)
#print
#######

########### PRINT scence validity
#print
#actionids = [1    ,2    ,3    ,4    ,9    ,10    ,11]
#print '\t',repr(actionids).strip('[').rstrip(']').replace(',','\t')
#for p in ps:
#    validscs = map(lambda x:x.scid, filter(lambda x:x.is_valid,p.scenes))
#    output = map(lambda x:int(x in validscs),actionids)
#    print p.id,'\t',(repr(output)).strip('[').rstrip(']').replace(',','\t')
#print
#for p in ps:
#    existingscs = filter(lambda x:x.scid in actionids,p.scenes)
#    exscdic = {}
#    for sc in existingscs:
#        exscdic[sc.scid] = sc
#        
#    def retnumberofsegs(dic,acid):
#        if acid in dic.keys():
#            return dic[acid].features['numsegments']
#        else:
#            return 0
#    output = map(lambda x:retnumberofsegs(exscdic,x),actionids)
#    print p.id,'\t',(repr(output)).strip('[').rstrip(']').replace(',','\t')    


###### PRINT invalid segements 
#for p in ps:
#    ##p.print_()
#    print p.id
#    print p.invalid_segments()
#    print p.valid_segments() 
    
####### %Discarded
#print "p.id,valid,vlength_sum,length_sum,valid portion"
#for p in ps:
#    vlength_sum = sum(map (lambda y:y.length,filter(lambda x:x.is_valid,p.segments)))
#    length_sum = sum(map(lambda x:x.length,p.segments))
#    print p.id,p.is_valid(),vlength_sum,length_sum,vlength_sum*1.0/length_sum
####### 
# 
 
    
###### BASIC test    
#rec = Recording.Recording('./data/P57-All-Data.tsv','./data/P57-Fixation-Data.tsv') 
#
#scenes,_,_ = partition_CSP('./data/Rec 08-Event-Data.tsv')
#print "scenes", scenes
#segs,scs = rec.process_rec( scenelist = scenes,aoifile ='./data/aois_57.aoi', )
#for seg in segs:
#    print "\n"
#    seg.print_()
#    if 'GraphA' in seg.aoi_data:
#        seg.aoi_data['GraphA'].print_()
#    print "\n"

