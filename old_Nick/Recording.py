# PETL - Recording.py
# Nicholas FitzGerald - nicholas.fitzgerald@gmail.com
#
# Class to hold all the data from a given recording

from Datapoint import *
from Trial import *

class Recording():
    def __init__(self, all_file, fixation_file, media_offset = (0,0)):
        """
        @type all_file: str
        @type fixation_file: str
        @param all_file: The filename of the 'All-Data.tsv' file output by the
        Tobii software.
        @param fixation_file: The filename of the 'Fixation-Data.tsv' file output by the
        Tobii software.
        """
        self.all_data = read_all_data(all_file)
        self.fix_data = read_fixation_data(fixation_file, media_offset =
        media_offset)

    def segment(self, segfile, aoifile = None, prune_length = None,
    media_offset = (0,0)):
        """
        Divides the recording into an array of L{Trials<Trial.Trial>}. These trials are
        defined by the time intervals.

        @type segfile: An array of triples (str, int, int)
        @param segfile: Filename containing segment definitions in format:
            pid\t[<starttime>, <endtime>]
        ending timestamp. NB: Timestamps currently must be sorted in absolute chronological
        order, with no overlap.
        @type aoifile: string
        @param aoifile: the filename of a file defining the Areas of Interest.
        """
        segs = read_segs(segfile)
        ret = []
        def get_chunk(data, ind, start, end):
            curr_ind = ind
            while data[curr_ind].timestamp < start:
                curr_ind += 1
            start_ind = curr_ind
            curr_ind += 1
            while data[curr_ind].timestamp < end:
                curr_ind += 1
            end_ind = curr_ind - 1
            return curr_ind, start_ind, end_ind
        
        aoidict = {}
        if aoifile:
            aoidict = read_aois(aoifile)

        all_ind = 0
        fix_ind = 0
        for (qid, start, end) in segs:
            chart_type = None
            for prefix in aoidict.iterkeys():
               if prefix == qid[:len(prefix)]:
                  chart_type = prefix
                  break
            aois = []
            if chart_type in aoidict:
                aois = aoidict[chart_type]
            else:
               raise Exception("prefix error")

            all_ind, all_start, all_end = get_chunk(self.all_data, all_ind, start, end)
            fix_ind, fix_start, fix_end = get_chunk(self.fix_data, fix_ind, start, end)
            ret.append(Trial(qid, self.all_data[all_start:all_end],
            self.fix_data[fix_start:fix_end], aois=aois,
            prune_length=prune_length))
        return ret
            

def read_all_data(all_file):
    """
    Returns an array of L{Datapoints<Datapoint.Datapoint>} read from the data
    file.

    @type all_file: str
    @param all_file: The filename of the 'All-Data.tsv' file output by the
    Tobii software.
    """
    with open(all_file, 'r') as f:
        lines = f.readlines()

    return map(Datapoint, lines[25:])

# read_fixation_data(all_file)
# pre:
#      fixation_file = filename for the "Fixation-Data.tsv" file holding the data
# post:
#      returns an array of Fixationss corresponding to the lines of the datafile
def read_fixation_data(fixation_file, media_offset = (0,0)):
    """
    Returns an array of L{Fixations<Datapoint.Fixation>} read from the fixation
    file.

    @type fixation_file: str
    @param fixation_file: The filename of the 'Fixation-Data.tsv' file output
    by the Tobii software.
    """
    with open(fixation_file, 'r') as f:
        lines = f.readlines()

    return map(lambda x: Fixation(x, media_offset=media_offset), lines[19:])


def read_aois(aoifile):
    aoidict = {}
    with open(aoifile, 'r') as f:
        aoilines = f.readlines()

    aids = aoilines[0].strip().split('t')
   
    for l in aoilines[1:]:
        l = l.strip()
        chunks = l.split('\t')
        chart_type = chunks[0][:9]
        #join the aids to the ploys
        polys = map(lambda x, (y,z): (x,y,z), aids, map(eval, chunks[1:]))
        aoidict[chart_type] = polys

    return aoidict

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


