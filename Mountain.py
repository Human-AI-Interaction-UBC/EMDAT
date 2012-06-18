'''
UBC Eye Movement Data Analysys Toolkit
Created on 2011-08-26

@author: skardan
'''
from utils import *

class Mountain():
    def __init__(self, mid, mntNum, mount_start, mount_stop):
        self.mid = mid
        self.mntNum = mntNum
        self.mount_start = mount_start
        self.mount_stop = mount_stop
        self.time_seq = []
        self.time_seq.append(mount_start)
        self.time_seq.append(mount_stop)
        
    def print_(self):
        print "Mountain Name: ", self.mid, " with time_seq ", self.time_seq 