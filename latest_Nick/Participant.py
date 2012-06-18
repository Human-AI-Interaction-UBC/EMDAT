import Recording
import os, string


class Participant():
    def __init__(self, pid, segsfile, datafile, fixfile, aoifile = None, prune_length= None):

        rec = Recording.Recording(datafile, fixfile, media_offset = (0, 18))
        self.trials = rec.segment(segsfile, aoifile = aoifile, prune_length = prune_length)
        self.id = pid

    def invalid_trials(self):
        return map(lambda y: y.qid, filter(lambda x: not x.is_valid, self.trials))

    def valid_trials(self):
        return map(lambda y: y.qid, filter(lambda x: x.is_valid, self.trials))

    def export_features(self, featurelist=None, aoifeaturelist=None, id_prefix =
    False, require_valid = True):
        data = []
        featnames = []
        if id_prefix:
            featnames.append('part_id')
        featnames.append('trial_id')
        first = True
        for t in self.trials:
            if not t.is_valid and require_valid:
                continue
            trial_feats = []
            if id_prefix:
                trial_feats.append(self.id)
            trial_feats.append(t.qid)
            fnames, fvals = t.get_features(featurelist = featurelist,
            aoifeaturelist = aoifeaturelist)
            if first: featnames += fnames
            trial_feats += fvals
            first = False
            data.append(trial_feats)            

        return featnames, data

    def export_features_tsv(self, featurelist=None, aoifeaturelist=None, id_prefix =
    False, require_valid = True):
        featnames, data  = self.export_features(featurelist, aoifeaturelist =
        aoifeaturelist, id_prefix = id_prefix, require_valid = require_valid)

        ret = string.join(featnames, '\t') + '\n'
        for t in data:
            ret += (string.join(map(str, t), '\t') + '\n')
        return ret

     

def read_participants(segsdir, datadir, prune_length = None, aoifile = None):
    listing = filter(lambda x: x[-5:] == '.segs', os.listdir(segsdir))
    participants = []
    for segfile in listing:
        # print segfile
        if segfile == '.svn':
            continue
        pid = segfile.split('.')[0]
        
        segsfile = segsdir + pid + '.segs'  
        datafile = datadir + 'P' + pid + '-All-Data.tsv'
        fixfile = datadir + 'P' + pid + '-Fixation-Data.tsv'

        # print pid
        # print
        p = Participant(pid,segsfile, datafile, fixfile, aoifile=aoifile, prune_length = prune_length)
        participants.append(p)

    return participants

def export_features_all(participants, featurelist = None, aoifeaturelist=None, id_prefix
= False, require_valid = True):
    data = []
    for p in participants:
        fnames, fvals = p.export_features(featurelist=featurelist,
        aoifeaturelist=aoifeaturelist, id_prefix=id_prefix, require_valid =
        require_valid)
        featnames = fnames
        data += fvals
    return featnames, data

def write_features_tsv(participants, outfile, featurelist = None, aoifeaturelist =
None, id_prefix = False):
    fnames, fvals = export_features_all(participants, featurelist =
    featurelist, aoifeaturelist = aoifeaturelist, id_prefix=id_prefix)
    
    with open(outfile, 'w') as f:
        f.write(string.join(fnames, '\t') + '\n')
        for l in fvals:
            f.write(string.join(map(str, l), '\t') + '\n')


