'''
UBC Eye Movement Data Analysis Toolkit (EMDAT), Version 3

Wrapper for composite AOIs (AOIs defined as a set of polygons).
Created on 2014-5-25

@author: lalles
'''
import sys, os

def init_composite_AOIs(aoifilename, aoifilename_composite):
	"""
	Convert a composite AOI definition file to a simple file by exploding all composite AOIs (defined as a set of polygons) in a set of new AOIs defined as one single polygon
	
	Args:
		aoifilename: path of the AOIs definition file
		aoifilename_composite: destination of the temporary composite AOIs file

	Returns:
		List of new AOIs name
	"""
	try:
		aoifile=open(aoifilename, 'rb')
		aoifile_out=open(aoifilename_composite, 'wb')
		
		aoilines = aoifile.readlines()
		dynamic_aoi = []
		aoinewline = []
		aoinames = []
		
		for line in aoilines:
			if line.find(";") >-1: #multiple polygons
				chunks_polys=line.strip().split(';')
				for i in range(0,len(chunks_polys)):
					chunks_polys[i]=chunks_polys[i].split("\t")
					if i == 0:
						aoi_id=chunks_polys[i][0]
						chunks_polys[i][0] = aoi_id+"___"+str(i)
					else:
						chunks_polys[i][0] = aoi_id+"___"+str(i)+chunks_polys[i][0]
					aoinames.append(aoi_id+"___"+str(i))
					chunks_polys[i] = '\t'.join(chunks_polys[i])
				aoinewline.append(chunks_polys)
			else:
				aoinewline.append([line.strip()])
				if not line.strip().startswith('#'):
					chunks=line.strip().split('\t')
					aoinames.append(chunks[0])
					
		for numl, lines in enumerate(aoinewline):
			if not lines[0].startswith('#'):
				for l in lines:
					aoifile_out.write(l+'\n')
					if numl<len(aoinewline)-1 and aoinewline[numl+1][0].startswith('#'):
						aoifile_out.write(aoinewline[numl+1][0]+'\n')

		aoifile.close()
		aoifile_out.close()
		return aoinames
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print "Exception", sys.exc_info()
		print "Line ", exc_tb.tb_lineno

		
def postprocess_composite_AOIs(outfilename, aoinames, aoi_feat):
	"""
	Post-process the features output file by merging all exploded single AOI (init_composite_AOIs() must be called first)
	
	Args:
		outfilename: features output file
		aoinames: list of AOIs names (returned by init_composite_AOIs())
		aoi_feat: list of AOI features
	"""
	try:
		outfile=open(outfilename, 'rb')
		outlines = outfile.readlines()
		
		if not outlines[0].find("___")>-1:
			outfile.close()
			return 0 #no composite AOI, nothing to do
		
		#else
		outfile.close()
		outfile=open(outfilename, 'wb')
		header_feat = outlines[0].split('\t')
		merge_id = []
		merge_subid = []
		to_remove=[]
		
		for col in aoinames:
			if col.find("___")>-1:
				col_c = col.split("___")
				if col_c[1] == '0':
					merge_id.append( header_feat.index(col+"_"+aoi_feat[0]) )
					merge_subid.append([])
				else:
					last_id = 0 if len(merge_subid) == 0 else len(merge_subid)-1
					merge_subid[last_id].append( header_feat.index(col+"_"+aoi_feat[0]) )
					for i in range(0,len(aoi_feat)):
						to_remove.append(header_feat.index(col+"_"+aoi_feat[0])+i)
				
#		print merge_id
#		print merge_subid
		to_remove.sort()
		to_remove.reverse()
		
		for numl,l in enumerate(outlines):
			if numl == 0:
				chunk = l.split('\t')
				for mid in merge_id:
					for i in range(0,len(aoi_feat)):
						chunk[mid+i] = chunk[mid+i].replace("___0", "")
				for delid in to_remove: #remove all polygons of the composite AOI except the first
					chunk.pop(delid)
				out=('\t'.join(chunk))
				if out.find('\n')==-1:
					out = out+'\n'
				outfile.write(out) #clean header
			else:
				chunk = l.split('\t')
				for idc,col_feat0 in enumerate(merge_id): #for all first polygons of a composite AOI
					for idf, feat in enumerate(aoi_feat): # for all AOI features
						init_val = float(chunk[col_feat0+idf])
						for col_subfeat in merge_subid[idc]: #for all other polygons of the composite AOI
							if feat == "fixationrate" or feat == "numfixations" or feat == "proportionnum" or feat == "proportiontime" or feat == "totaltimespent":
								init_val = init_val + float(chunk[col_subfeat+idf])
							elif feat == "longestfixation" or feat == "timetolastfixation":
								init_val = max(init_val, float(chunk[col_subfeat+idf]))
							elif feat == "timetofirstfixation":
								init_val = min(init_val, float(chunk[col_subfeat+idf]))
							else:
								raise Exception("Unknown AOI feature : "+feat)
							
						chunk[col_feat0+idf] = 	str(init_val) # merge values in the column of the first polygon
				
				for delid in to_remove: #remove all polygons of the composite AOI except the first
					chunk.pop(delid)
				
				out=('\t'.join(chunk))
				if out.find('\n')==-1:
					out = out+'\n'
				outfile.write(out)
						
		outfile.close()	
	except:
		exc_type, exc_obj, exc_tb = sys.exc_info()
		print "Exception", sys.exc_info()
		print "Line ", exc_tb.tb_lineno

