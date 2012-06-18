'''
UBC Eye Movement Data Analysys Toolkit
Created on 2011-08-25

@author: marymuir from skardan
'''

from PrimeClimb import *
from Participant import *
from params import *

ul=[14]
uids = [14]
alogoffset = [0]

# FOR AOIs - use Static2 for most participant use static3 for pilot14 (s8)

#ul =   [7,8,9,10,11,12,13,14,15,16,17,18,19]
#uids = [7,8,9,10,11,12,13,14,15,16,17,18,19]
#alogoffset = [0,0,0,0,0,0,0,0,0,0,0,0,0]
################## Segments Validity info
#pv = test_validityA(user_list=ul, datadir='./PrimeClimbData/', prune_length = None,   
#                           aoifiles = './PrimeClimbData/Static2.aoi')
#print
#
##for rate in xrange(1,21,1): ##proportion gap
#for rate in xrange(1,102,1): ##proportion
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
#################

########### Validity of users
#pv = test_validity2(user_list=ul,datadir='./PrimeClimbData/', prune_length = None)
#
#for rate in xrange(1,102,1): ##proportion
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

####### READ All Participants
ps = read_participants_PC(datadir='./PrimeClimbData/', user_list = ul, pids = uids,  
                           prune_length = None, aoifiles = './PrimeClimbData/Static2.aoi')
#print





###### WRITE features to file
write_features_tsv(ps, 'pc_eye.tsv',featurelist = params.featurelist,   
                           aoifeaturelabels=params.aoifeaturelist, id_prefix = False)



###### PRINT features on the screen
fn,fv = export_features_all(ps, featurelist = params.featurelist,   
                           aoifeaturelabels=params.aoifeaturelist, id_prefix = False,   
                           require_valid = True)
print fn
for v in fv:
    print v
######

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
 

