#from Trial import *
import Recording as Recording
import os, string


def read_logfile(logfile):
    answers = {}
    with open(logfile, 'r') as f:
        loglines = f.readlines()

    for l in loglines:
        (qid, time, answer, confidence) = l.split()
        answers[qid] = (answer, int(confidence))

    return answers

gold_answers = read_logfile('../logfiles/GOLD.logfile.txt')

class Participant():
    def __init__(self, pid, segsfile, datafile, fixfile, aoifile = None, prune_length= None):

        rec = Recording.Recording(datafile, fixfile, media_offset = (0, 18))
        self.trials = rec.segment(segsfile, aoifile = aoifile, prune_length = prune_length)
        self.id = pid

    def invalid_trials(self):
        return map(lambda y: y.qid, filter(lambda x: not x.is_valid, self.trials))

    def valid_trials(self):
        return map(lambda y: y.qid, filter(lambda x: x.is_valid, self.trials))

    def export_features(self, featurelist, aoifeaturelist=None):
        data = []
        featnames = []
        first = True
        for t in self.trials:
            trial_feats = []
            trial_feats.append(t.qid)
            for f in featurelist:
                if first: featnames.append(f)
                trial_feats.append(eval('t.%s'%(f)))

            for f in aoifeaturelist:
                for a in sorted(t.aoi_data.iterkeys()):
                    if first: featnames.append('%s_%s'%(a, f))
                    trial_feats.append(eval('t.aoi_data[a].%s'%(f)))
            first = False
            data.append(trial_feats)            

        return featnames, data

    def export_features_tsv(self, featurelist, aoifeaturelist=None):
        featnames, data  = self.export_features(featurelist, aoifeaturelist = aoifeaturelist)

        ret = ' \t'+ string.join(featnames, '\t') + '\n'
        for t in data:
            ret += (string.join(map(str, t), '\t') + '\n')
        return ret
        

     

def read_participants(indir, prune_length = None, aoifile = 'aois/aois.tsv'):
    listing = filter(lambda x: x[-5:] == '.segs', os.listdir(indir))
    participants = []
    for segfile in listing:
        # print segfile
        if segfile == '.svn':
            continue
        pid = segfile.split('.')[0]
        # print pid
        # print
        p = Participant(pid, aoifile=aoifile, prune_length = prune_length)
        participants.append(p)

    return participants

