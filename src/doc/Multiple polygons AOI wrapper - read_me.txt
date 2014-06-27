EMDAT Wrapper - Composite AOIs - 2014-05-25


1/ How to define an AOI composed by A1...AN individual polygons:

aoiname<tab>A1point1x,A1point1y<tab>...<tab>A1pointnx,A1pointny<tab>;<tab>A2point1x,A2point1y<tab>...<tab>A2pointnx,A2pointny<tab>;<tab>...ANpoint1x,ANpoint1y<tab>...<tab>ANpointnx,ANpointny

Each polygon is defined by a subet of points, and separed to the next polygon by ';<tab>'.

Nothing changes for the dynamic AOIs.

Examples: see "./sampledata/Simple composite aois.aoi" and "./sampledata/Dynamic composite aois.aoi"


2/ How to use a composite AOI file:

In a main EMDAT run file:

- import 'EMDAT_multipleAOIs_wrapper'
- call the EMDAT_multipleAOIs_wrapper.init_composite_AOIs() function before reading participants
- call the EMDAT_multipleAOIs_wrapper.postprocess_composite_AOIs() after having exported features

Examples: see 'testCompositeAOI.py'


3/ 'EMDAT_multipleAOIs_wrapper' Doc

def init_composite_AOIs(aoifilename, aoifilename_composite):
"""
Convert a composite AOI definition file to a simple file by exploding all composite AOIs (defined as a set of polygons) in a set of new AOIs defined as one single polygon
	
Args:
	aoifilename: path of the AOIs definition file
	aoifilename_composite: destination of the temporary composite AOIs file

Returns:
	List of new AOIs name
"""

def postprocess_composite_AOIs(outfilename, aoinames, aoi_feat):
"""
Post-process the features output file by merging all exploded single AOI (init_composite_AOIs() must be called first)
	
Args:
	outfilename: features output file
	aoinames: list of AOIs names (returned by init_composite_AOIs())
	aoi_feat: list of AOI features
"""


Author: Sebastien Lalle; lalles@cs.ubc.ca