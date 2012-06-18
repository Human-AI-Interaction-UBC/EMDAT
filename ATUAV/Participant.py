#from Trial import *
import PETL.Recording as Recording

SEGDIR = 'segfiles/'
DATADIR = 'data/'
LOGDIR = '../logfiles/'

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
   def __init__(self, pid, aoifile = None, prune_length= None):
      segsfile = SEGDIR + pid + '.segs'  
      datafile = DATADIR + 'P' + pid + '-All-Data.tsv'
      fixfile = DATADIR + 'P' + pid + '-Fixation-Data.tsv'
      logfile = LOGDIR + pid + '.logfile.txt'

      rec = Recording.Recording(datafile, fixfile)
      trials = rec.segment(segsfile, aoifile = aoifile, prune_length = prune_length)
      self.id = pid
      self.trials = trials2exp1trials(trials, logfile)
      self.condition = self.get_condition()

   def get_condition(self):
      condition = 1
      if self.trials[0].qid[:3] == 'rad':
         condition += 4
         rad_first = self.trials[0].qid
         bar_first = self.trials[14].qid
      else:
         bar_first = self.trials[0].qid
         rad_first = self.trials[14].qid
      if bar_first[-8:] == 'spikey_1':
         condition += 1
      if rad_first[-8:] == 'spikey_1':
         condition += 2
      return condition

   def invalid_trials(self):
      return map(lambda y: y.qid, filter(lambda x: not x.is_valid, self.trials))

   def valid_trials(self):
      return map(lambda y: y.qid, filter(lambda x: x.is_valid, self.trials))


 

def add_aois(trials, aoifile):
    aoidict = readaois(aoifile)
    aois = []
    for t in trials:
        chart_type = t.qid[:9]
        print aoidict[aid]
        aoi = aoidict[chart_type]
        aois.append(aoi)
        
    t = t.set_aois(aois)

def trials2exp1trials(trials, logfile):

   answers = read_logfile(logfile)
   ret = []
   for i in xrange(len(trials)):
      qid = trials[i].qid
      (answer, confidence) = answers[qid]
      trials[i].answer = answer
      trials[i].confidence = confidence
      trials[i].is_correct = (answer == gold_answers[qid][0])
   return trials
      

def read_segs(segfile):
   segs = []
   with open(segfile, 'r') as f:
      seglines = f.readlines()

   for l in seglines:
      l = l.strip()
      l = l.split('\t')
      qid = l[0]
      [segstart, segend] = eval(l[1])

      segstart = int(segstart)
      segend = int(segend)
      segs.append((qid, segstart, segend))
   return segs

def read_participants(listing, prune_length = None, aoifile = 'aois/aois.tsv'):
   participants = []
   for segfile in listing:
      if segfile == '.svn':
         continue
      pid = segfile.split('.')[0]
      #print qid
      #print
      p = Participant(pid, aoifile=aoifile, prune_length = prune_length)
      participants.append(p)

   return participants

