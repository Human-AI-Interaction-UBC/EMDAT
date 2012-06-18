from PETL import *
from Participant import *
import os, string

VAL_THRESH = .8

def process_validity(trials):
    tot_num = 0
    tot_val = float(0)

    num_under_thresh = 0

    for t in trials:
        qid = t.qid
        val = t.validity
        num = t.num_samples

        tot_val += val*num
        tot_num += num

        if not t.is_valid():
            num_under_thresh += 1
        print t.qid, str(t.calc_validity())

    avg_val = tot_val / tot_num
    print avg_val
    print num_under_thresh
    print

    return avg_val, num_under_thresh

def process_correctness(trials):
    tot_num = 0
    tot_incor = 0

    for t in trials:
        tot_num += 1
        if not t.correct:
            tot_incor += 1

    return tot_incor

def calc_valids(participants):
    valids = {}
    for p in participants:
        inval = p.valid_segments()
        for i in inval:
            valids.setdefault(i, []).append(p.condition)

    cond_count0 = [0]*8
    cond_count1 = [0]*8
    cond_count2 = [0]*8
    cond_count3 = [0]*8
    for key in valids.iterkeys():
        print key
        for i in xrange(1,9):
            n = valids[key].count(i)
            print '\t', i, n
            if n == 0:
                cond_count0[i-1] += 1
            if n == 1:
                cond_count1[i-1] += 1
            if n == 2:
                cond_count2[i-1] += 1
            if n == 3:
                cond_count3[i-1] += 1
                
        print 'Total:', len(valids[key])
        print

    print "Cond Count0:"
    for i in xrange(8):
        print i+1, cond_count0[i]
    print
    print "Cond Count1:"
    for i in xrange(8):
        print i+1, cond_count1[i]
    print
    print "Cond Count2:"
    for i in xrange(8):
        print i+1, cond_count2[i]
    print
    print "Cond Count3:"
    for i in xrange(8):
        print i+1, cond_count3[i]
    print

def read_prefs():
    with open('prefs.txt', 'r') as f:
        inlines = f.readlines()

    prefs = {}
        
    for l in inlines:
        l = l.strip()
        if l == '':
            break
        (id, name, pref_bar, pref_rad) = l.split('\t')
        if pref_bar == '0':
            pref = 0
        elif pref_bar == 'tie':
            pref = 1
        elif pref_bar == '1':
            pref = 2
        prefs[id] = pref

    return prefs



def prepare_mona_files(participants):

    qnames = sorted(['bar_uniform_1', 'bar_uniform_2', 'bar_uniform_3', 'bar_uniform_4', 'bar_uniform_5', 'bar_spikey_1', 'bar_spikey_2', 'bar_spikey_3', 'bar_spikey_4', 'bar_spikey_5', 'bar_double_1', 'bar_double_2', 'bar_double_3', 'bar_double_4', 'radar_uniform_1', 'radar_uniform_2', 'radar_uniform_3', 'radar_uniform_4', 'radar_uniform_5', 'radar_spikey_1', 'radar_spikey_2', 'radar_spikey_3', 'radar_spikey_4', 'radar_spikey_5', 'radar_double_1', 'radar_double_2', 'radar_double_3', 'radar_double_4'])

    timelines = []
    corrlines = []
    conflines = []

    timelines.append(' \t' + string.join(qnames, '\t') + '\n')
    corrlines.append(' \t' + string.join(qnames, '\t') + '\n')
    conflines.append(' \t' + string.join(qnames, '\t') + '\n')

    for p in participants:
        trials = sorted(p.trials, key= lambda x: x.qid)
        timelines.append(string.join([str(p.id)] + map(lambda x: str(x.length), trials), '\t') + '\n')
        corrlines.append(string.join([str(p.id)] + map(lambda x: str(x.is_correct), trials), '\t') + '\n')
        conflines.append(string.join([str(p.id)] + map(lambda x: str(x.confidence), trials), '\t') + '\n')

    with open('out/times.txt', 'w') as f:
        for l in timelines:
            f.write(l)

    with open('out/correctness.txt', 'w') as f:
        for l in corrlines:
            f.write(l)

    with open('out/confidence.txt', 'w') as f:
        for l in conflines:
            f.write(l)
        
def validity_rate(participants):
    tot_num = float(0)
    num_valid = float(0)
    for p in participants:
        for t in p.trials:
            tot_num += 1
            if t.is_valid:
                num_valid+=1
    print num_valid
    print tot_num
    print num_valid/tot_num
    

def main():
    segdir = 'segfiles/'
    listing = os.listdir(segdir)
    listing = filter(lambda y: y[-5:] == '.segs', listing)
    participants = read_participants(listing)
    validity_rate(participants)
    exit()
    gaps = []
    props = []
    for p in participants:
        for t in p.trials:
            gaps.append(t.largest_data_gap)
            props.append(t.proportion_valid)
    gaps.sort()
    props.sort(reverse=True)

    print '0\t0.000'
    last = 0.0
    for i in xrange(len(gaps)):
        if gaps[i]==last:
            continue
        x = float(i) / len(gaps)
        if gaps[i] == float('inf'):
            print 'inf\t%.3f'%(x)
        else:
            print '%d\t%.3f'%(gaps[i], x)
        last = gaps[i]
        
    print
    print

    print '1.000\t0.000'
    last = 1.000
    for i in xrange(len(props)):
        if props[i] == last:
            continue
        x = float(i) / len(props)
        print '%.3f\t%.3f'%(props[i], x)
    last = props[i]
        
    exit()
    
    for x in [10000,12000, 14000, 16000, None]:
    #for x in [2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000, 6500, 7000, 7500,
    #8000, 8500, 9000, 9500]:
        print "Starting x=%d"%(x)
        participants = read_participants(listing, prune_length=x)

        prepare_svm_data(participants, datafile = "svm_test%d.txt"%(x))




    #p = Participant("segfiles/525330.segs", "data/P525330-All-Data.tsv", "data/P525330-Fixation-Data.tsv", "../logfiles/525330.logfile.txt")
    #t = p.trials[0]
    
    #for f in t.fixdata:
    #    print f.timestamp, f.fixationduration, f.mappedfixationpointx, f.mappedfixationpointy
    
    #print
    #print t.meanfixationduration
    #print t.sumfixationduration
    #print
    #print t.distances
    #print t.meanpathdistance
    #print t.sumpathdistance

        
        


        #num+=1
        #tot_val += avg_val
        #tot_num_under_thresh += num_under_thresh
        #unders.append(num_under_thresh)

    #print "Overall Statistics:"
    #print "Average Validity:", tot_val/num
    #print "Average Number under Threshold", tot_num_under_thresh / num
    #print unders
    

if __name__ == '__main__':
    main()
