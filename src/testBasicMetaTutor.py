'''
Created on 2012-08-23

@author: skardan
'''

import sys
import os

window = "Window1"
if len(sys.argv) >= 2:
    window = sys.argv[1]

#CHOOSE THE INPUT AND OUTPUT DIRECTORIES FOR YOUR DATA AND RESULTS
DIR = '../../data/'
SEGDIR = DIR + "SEGs/" 	
AOIDIR = DIR + "AOIs/"
outputLocation = "../../EMDAToutput/" 
	


sys.path.append("./")

import MetaTutorPartNatasha
from MetaTutorPartNatasha import read_participants_Basic
import params
from Participant import export_features_all, write_features_tsv

listing = os.listdir(SEGDIR)
listing = filter(lambda y: y[-5:] == '.segs', listing)

list_of_participants = []
for l in listing:
    list_of_participants.append(l[0:len(l)-5])

#based on data validation process
list_of_participants = ['MT208PN41005', 'MT208PN41008', 'MT208PN41009', 'MT208PN41010', 'MT208PN41011', 
                        'MT208PN41012', 'MT208PN41013', 'MT208PN41015', 'MT208PN41017', 'MT208PN41018', 'MT208PN41019', 
                        'MT208PN41020', 'MT208PN41023', 'MT208PN41024', 'MT208PN41027', 'MT208PN41029', 
                        'MT208PN41030', 'MT208PN41033', 'MT208PN41035', 'MT208PN41037', 'MT208PN41038', 
                        'MT208PN41039', 'MT208PN41040', 'MT208PN41041', 'MT208PN41042', 'MT208PN41043', 
                        'MT208PN41045', 'MT208PN41049', 'MT208PN41050', 'MT208PN41051', 'MT208PN41052', 
                        'MT208PN41053', 'MT208PN41054', 'MT208PN41058', 'MT208PN41059', 'MT208PN41060', 
                        'MT208PN41061', 'MT208PN41064', 'MT208PN41068', 'MT208PN41070', 'MT208PN41072', 
                        'MT208PN41076', 'MT208PN41080', 'MT208PN41081', 'MT208PN41082', 'MT208PN41084', 
                        'MT208PN41085', 'MT208PN41086', 'MT208PN41087', 'MT208PN41088', 'MT208PN41091']
print list_of_participants

###### Read participants
ps = read_participants_Basic(DIR, SEGDIR, list_of_participants, prune_length = None, aoidir = AOIDIR, log_time_offsets=None, 
                          require_valid_segs = True, auto_partition_low_quality_segments = True)

###### Write participants
fnames = write_features_tsv(ps, outputLocation + 'features.tsv',featurelist = params.featurelist, aoifeaturelabels=params.aoifeaturelist, id_prefix = True) # removed last paraM: list_of_scenes = ["main"])
validityfile = outputLocation + "validity.tsv"
NUMDIGITS = 7
with open(validityfile, 'w') as f:
    line = 'Scene id' +'\t'+ 'Participant validity' + '\t' + 'Fix-based prop'+ '\t' + 'Proportion' +'\n'
    f.write(line)
    for p in ps:
        for sc in p.scenes:
            if sc.scid != "main":
                line = sc.scid+ '\t'+ str(round(sc.largest_data_gap, NUMDIGITS)) + '\t' + str(round(sc.proportion_valid_fix, NUMDIGITS))+ '\t' + str(round(sc.proportion_valid, NUMDIGITS)) +'\n'
                f.write(line)

            
listoffeatures = outputLocation + "feature_list.tsv" #CHANGE BASED ON TEST

with open(listoffeatures, 'w') as ff:
    for el in fnames:
        line = "@attribute\t"+el+"\tnumeric\n"
        ff.write(line)
ff.close()
