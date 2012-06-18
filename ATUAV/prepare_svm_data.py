from PETL import *
from Participant import *
import os, string, sys

SEGDIR = './segfiles/'

def prepare_svm_data(participants, datafile = "svm_data.txt"):
    
    outlines = []

    qnames = ['bar_uniform_1', 'bar_uniform_2', 'bar_uniform_3', 'bar_uniform_4', 'bar_uniform_5', 'bar_spikey_1', 'bar_spikey_2', 'bar_spikey_3', 'bar_spikey_4', 'bar_spikey_5', 'bar_double_1', 'bar_double_2', 'bar_double_3', 'bar_double_4', 'radar_uniform_1', 'radar_uniform_2', 'radar_uniform_3', 'radar_uniform_4', 'radar_uniform_5', 'radar_spikey_1', 'radar_spikey_2', 'radar_spikey_3', 'radar_spikey_4', 'radar_spikey_5', 'radar_double_1', 'radar_double_2', 'radar_double_3', 'radar_double_4']

    #prefs = read_prefs()

    for p in participants:
        for t in p.trials:
            if not t.is_valid:
                continue
            outline = []
            g_type = t.qid[:t.qid.index('_')]
            t_type = t.qid[t.qid.index('_')+1:]
            if g_type == 'bar':
                bar = t.qid
                other = 'radar_' + t_type
                radar = other
            elif g_type == 'radar':
                radar = t.qid
                other = 'bar_' + t_type
                bar = other
            other_t = filter(lambda x: x.qid == other, p.trials)[0]
            outline.append(str(t.completion_time))
            #if t.completion_time > other_t.completion_time:
            #    outline.append("1")
            #else:
            #    outline.append("0")
            #if t.is_correct:
            #if t.confidence >= 4:
            #    outline.append("1")
            #else:
            #    outline.append("0")
            #outline.append(t.length)
            outline.append(t.meanfixationduration)
            #outline.append(t.sumfixationduration)
            outline.append(t.stddevfixationduration)
            outline.append(t.meanpathdistance)
            #outline.append(t.sumpathdistance)
            outline.append(t.stddevpathdistance)
            #outline.append(t.sumabspathangles)
            outline.append(t.meanabspathangles)
            outline.append(t.stddevabspathangles)
            #outline.append(t.sumrelpathangles)
            outline.append(t.meanrelpathangles)
            outline.append(t.stddevrelpathangles)
            #outline.append(t.numfixations)
            outline.append(int(t.qid[:3]=='bar'))
            #outline.append(int(t.qid[:3]=='rad'))
            #for q in qnames:
            #    if t.qid == q:
            #        outline.append('1')
            #    else:
            #        outline.append('0')
            if t.qid[:3] == 'bar':
                outline.append('1')
            else:
                outline.append('0') 
            aids = sorted(t.aoi_data.items(), key = lambda x: x[0])
            for (aid, a) in aids:
                #outline.append(a.numfixations)
                outline.append(a.timetofirstfixation)
                outline.append(a.timetolastfixation)
                outline.append(a.longestfixation)
                #outline.append(a.totaltimespent)
                outline.append(a.proportiontime)
                outline.append(a.proportionnum)
                for (aid, x) in aids:
                    #outline.append(a.numtransto[aid])
                    #outline.append(a.numtransfrom[aid])
                    outline.append(a.proptransto[aid])
                    outline.append(a.proptransfrom[aid])
            outlines.append(outline)

    print "Done reading..."

    with open(datafile, 'w') as f:
        for o in outlines:
            o[1:] = map(lambda x, y: str(x)+':'+str(y), range(1, len(o[1:])+1), o[1:])
            line = string.join(o) + '\n'
            f.write(line)

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


def main():
    prune_lengths = map(int, sys.argv[1:])

    listing = os.listdir(SEGDIR)
    listing = filter(lambda y: y[-5:] == '.segs', listing)
    
    #for x in [10000,12000, 14000, 16000, None]:
    for x in prune_lengths:
        print "Starting x=%d"%(x)
        participants = read_participants(listing, prune_length=x)

        prepare_svm_data(participants, datafile = "svm_test%d.libsvm"%(x))

    print "Starting All Data"
    participants = read_participants(listing)
    prepare_svm_data(participants, datafile = "svm_test_ALL.libsvm")


if __name__ == '__main__':
    main()
