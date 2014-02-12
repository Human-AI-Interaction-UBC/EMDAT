'''
Created on Dec 10, 2012
This file is created to fix a PARTICULAR problem of merging: 
NormalImageContent and ImageContentRestrictedInput to one AOI: ImageContent
NormalTextContent and TextContentRestrictedInput to one AOI: TextContent
@author: Daria
'''
from AOI import  *
from copy import deepcopy
#Merge AOIs NormalImageContent and ImageContentRestrictedInput to ImdageContent 
def MergeToXContent(scene, newname, normalaoi, restrictedaoi):
    #print "Normal aoi: " + str(scene.aoi_data[normalaoi])
    #print "Restricted AOI: " + scene.aoi_data[restrictedaoi]
    if (scene.aoi_data.has_key(normalaoi)) and (scene.aoi_data.has_key(restrictedaoi)): #if both AOIs are not empty
        MergeToXContent_noNone (scene, newname, normalaoi, restrictedaoi) 
    else:
        if (scene.aoi_data.has_key(normalaoi)): #if restricted aoi is empty
            aoidata = deepcopy(scene.aoi_data[normalaoi])
            aoidata.aoi.aid = newname
            scene.aoi_data[newname]=aoidata
        if (scene.aoi_data.has_key(restrictedaoi)): #if normal AOI is empty
            aoidata = deepcopy(scene.aoi_data[restrictedaoi])
            aoidata.aoi.aid = newname
            scene.aoi_data[newname]=aoidata

def MergeToXContent_noNone (scene, newname, normalaoi, restrictedaoi):
    
    aoi = deepcopy(scene.aoi_data[normalaoi].aoi)
    aoi.aid = newname
    #def __init__(self,aoi,seg_fixation_data, starttime, endtime, active_aois):
    fnorm = scene.aoi_data[normalaoi].features
    frest = scene.aoi_data[restrictedaoi].features
    aoistat= AOI_Stat(aoi, [], 0, 1,[])
    #create new feature set
    aoistat.features={}
    aoistat.features['numfixations'] =fnorm['numfixations']+frest['numfixations']
    aoistat.features['longestfixation'] = max(fnorm['longestfixation'],frest['longestfixation'])
    aoistat.features['timetofirstfixation'] = -1
    aoistat.features['timetolastfixation'] = -1
    
    aoistat.features['fixationsonscreen']=fnorm['fixationsonscreen']+frest['fixationsonscreen']
    aoistat.features['timeonscreen'] = fnorm['timeonscreen']+frest['timeonscreen']
    
    aoistat.features['totaltimespent'] =  fnorm['totaltimespent']+frest['totaltimespent']
            
    aoistat.features['proportionnum_dynamic'] = (float(aoistat.features['numfixations'])) / aoistat.features['fixationsonscreen']
    aoistat.features['proportiontime_dynamic'] = (float(aoistat.features['totaltimespent'])) / aoistat.features['timeonscreen']
    aoistat.features['proportiontime'] = fnorm['proportiontime']+frest['proportiontime']
    aoistat.features['proportionnum'] = fnorm['proportionnum']+frest['proportionnum']
    if aoistat.features['totaltimespent'] != 0:
        aoistat.features['fixationrate'] = (float(aoistat.features['numfixations'])) / aoistat.features['totaltimespent']
    else:
        aoistat.features['fixationrate'] = 0

    
    aoistat.features['sumtransfrom']=fnorm['sumtransfrom']+frest['sumtransfrom']
    aoistat.features['sumtransto']=fnorm['sumtransto']+frest['sumtransto']
    print "!!!!!!!!!!!!!"
    print scene.aoi_data.keys()    
    for elaoi in scene.aoi_data.keys():
        if elaoi is not "TextContent" and elaoi is not "ImageContent" and elaoi is not "Content":
            aid = elaoi
            print "currently in: " + elaoi
            
            if fnorm.has_key('numtransto_%s'%(aid)):
                if frest.has_key('numtransto_%s'%(aid)):
                    aoistat.features['numtransto_%s'%(aid)] = fnorm['numtransto_%s'%(aid)]+frest['numtransto_%s'%(aid)]
                    aoistat.features['numtransfrom_%s'%(aid)] = fnorm['numtransfrom_%s'%(aid)]+frest['numtransfrom_%s'%(aid)]
                    if aoistat.features['sumtransto']!=0:
                        aoistat.features['proptransto_%s'%(aid)] = (float(aoistat.features['numtransto_%s'%(aid)]))/  aoistat.features['sumtransto']
                    else:
                        aoistat.features['proptransto_%s'%(aid)] = 0
                    if aoistat.features['sumtransfrom']!=0:
                        aoistat.features['proptransfrom_%s'%(aid)] = (float(aoistat.features['numtransfrom_%s'%(aid)]))/  aoistat.features['sumtransfrom']
                    else:
                        aoistat.features['proptransfrom_%s'%(aid)] = 0
                else:
                    aoistat.features['numtransto_%s'%(aid)] = fnorm['numtransto_%s'%(aid)]
                    aoistat.features['numtransfrom_%s'%(aid)] = fnorm['numtransfrom_%s'%(aid)]
                    if aoistat.features['sumtransto']!=0:
                        aoistat.features['proptransto_%s'%(aid)] = (float( aoistat.features['numtransto_%s'%(aid)])) / aoistat.features['sumtransto']
                    else:
                        aoistat.features['proptransto_%s'%(aid)] = 0
                    if aoistat.features['sumtransfrom']!=0:
                        aoistat.features['proptransfrom_%s'%(aid)] =  (float( aoistat.features['numtransfrom_%s'%(aid)])) / aoistat.features['sumtransfrom']
                    else:
                        aoistat.features['proptransfrom_%s'%(aid)] = 0
            else:
                if frest.has_key('numtransto_%s'%(aid)):
                    aoistat.features['numtransto_%s'%(aid)] = frest['numtransto_%s'%(aid)]
                    aoistat.features['numtransfrom_%s'%(aid)] = frest['numtransfrom_%s'%(aid)]
                    if aoistat.features['sumtransto']!=0:
                        aoistat.features['proptransto_%s'%(aid)] = (float( aoistat.features['numtransto_%s'%(aid)])) / aoistat.features['sumtransto']
                    else:
                        aoistat.features['proptransto_%s'%(aid)] = 0
                    if aoistat.features['sumtransfrom']!=0:
                        aoistat.features['proptransfrom_%s'%(aid)] =  (float( aoistat.features['numtransfrom_%s'%(aid)])) / aoistat.features['sumtransfrom']
                    else:
                        aoistat.features['proptransfrom_%s'%(aid)]  = 0

    
    scene.aoi_data[newname] = aoistat

def MinorTextImageFix(scene):
    print "Minor Text Image Fix"
    imfeat = scene.aoi_data["ImageContent"].features
    textfeat = imfeat = scene.aoi_data["TextContent"].features
    contentfeat = scene.aoi_data["Content"].features
    
    
#    imfeat["numtransto_TextContent"] = scene.aoi_data["NormalImageContent"].features["numtransto_TextContentRestrictedInput"] + scene.aoi_data["ImageContentRestrictedInput"].features["numtransto_NormalTextContent"]
#    imfeat["numtransfrom_TextContent"] = scene.aoi_data["NormalImageContent"].features["numtransfrom_TextContentRestrictedInput"] + scene.aoi_data["ImageContentRestrictedInput"].features["numtransfrom_NormalTextContent"]
#    imfeat["proptransto_TextContent"] = scene.aoi_data["NormalImageContent"].features["proptransto_TextContentRestrictedInput"] + scene.aoi_data["ImageContentRestrictedInput"].features["proptransto_NormalTextContent"]
#    imfeat["proptransfrom_TextContent"] = scene.aoi_data["NormalImageContent"].features["proptransfrom_TextContentRestrictedInput"] + scene.aoi_data["ImageContentRestrictedInput"].features["proptransfrom_NormalTextContent"]
#    
#    
#    textfeat["numtransto_ImageContent"] = scene.aoi_data["NormalTextContent"].features["numtransto_ImageContentRestrictedInput"] + scene.aoi_data["TextContentRestrictedInput"].features["numtransto_NormalImageContent"]
#    textfeat["numtransfrom_ImageContent"] = scene.aoi_data["NormalTextContent"].features["numtransfrom_ImageContentRestrictedInput"] + scene.aoi_data["TextContentRestrictedInput"].features["numtransfrom_NormalImageContent"]
#    textfeat["proptransto_ImageContent"] = scene.aoi_data["NormalTextContent"].features["proptransto_ImageContentRestrictedInput"] + scene.aoi_data["TextContentRestrictedInput"].features["proptransto_NormalImageContent"]
#    textfeat["proptransfrom_ImageContent"] = scene.aoi_data["NormalTextContent"].features["proptransfrom_ImageContentRestrictedInput"] + scene.aoi_data["TextContentRestrictedInput"].features["proptransfrom_NormalImageContent"]
#    
    
def FixFromForAllAOIs(scene):
    print "Finally"
    for aoiname in scene.aoi_data.keys():
        print aoiname
        
        #NATASHA: THIS NEEDS TO BE CHANGED BACK:
        """
        #fix transitions related to TextContent area
        if scene.aoi_data[aoiname].features.has_key("numtransto_NormalTextContent"):
            if scene.aoi_data[aoiname].features.has_key("numtransto_TextContentRestrictedInput"):
                
                scene.aoi_data[aoiname].features["numtransto_TextContent"]=scene.aoi_data[aoiname].features["numtransto_TextContentRestrictedInput"]+scene.aoi_data[aoiname].features["numtransto_NormalTextContent"]
                scene.aoi_data[aoiname].features["numtransfrom_TextContent"]=scene.aoi_data[aoiname].features["numtransfrom_TextContentRestrictedInput"]+scene.aoi_data[aoiname].features["numtransfrom_NormalTextContent"]
                scene.aoi_data[aoiname].features["proptransto_TextContent"]=scene.aoi_data[aoiname].features["proptransto_TextContentRestrictedInput"]+scene.aoi_data[aoiname].features["proptransto_NormalTextContent"]
                scene.aoi_data[aoiname].features["proptransfrom_TextContent"]=scene.aoi_data[aoiname].features["proptransfrom_TextContentRestrictedInput"]+scene.aoi_data[aoiname].features["proptransfrom_NormalTextContent"]
            else:
                scene.aoi_data[aoiname].features["numtransto_TextContent"]=scene.aoi_data[aoiname].features["numtransto_NormalTextContent"]
                scene.aoi_data[aoiname].features["numtransfrom_TextContent"]=scene.aoi_data[aoiname].features["numtransfrom_NormalTextContent"]
                scene.aoi_data[aoiname].features["proptransto_TextContent"]=scene.aoi_data[aoiname].features["proptransto_NormalTextContent"]
                scene.aoi_data[aoiname].features["proptransfrom_TextContent"]=scene.aoi_data[aoiname].features["proptransfrom_NormalTextContent"]
        else:
            if scene.aoi_data[aoiname].features.has_key("numtransto_TextContentRestrictedInput"):
                scene.aoi_data[aoiname].features["numtransto_TextContent"]=scene.aoi_data[aoiname].features["numtransto_TextContentRestrictedInput"]
                scene.aoi_data[aoiname].features["numtransfrom_TextContent"]=scene.aoi_data[aoiname].features["numtransfrom_TextContentRestrictedInput"]
                scene.aoi_data[aoiname].features["proptransto_TextContent"]=scene.aoi_data[aoiname].features["proptransto_TextContentRestrictedInput"]
                scene.aoi_data[aoiname].features["proptransfrom_TextContent"]=scene.aoi_data[aoiname].features["proptransfrom_TextContentRestrictedInput"]
                
        #fix transitions related to ImageContent area
        if scene.aoi_data[aoiname].features.has_key("numtransto_NormalImageContent"):
            if scene.aoi_data[aoiname].features.has_key("numtransto_ImageContentRestrictedInput"):
                
                scene.aoi_data[aoiname].features["numtransto_ImageContent"]=scene.aoi_data[aoiname].features["numtransto_ImageContentRestrictedInput"]+scene.aoi_data[aoiname].features["numtransto_NormalImageContent"]
                scene.aoi_data[aoiname].features["numtransfrom_ImageContent"]=scene.aoi_data[aoiname].features["numtransfrom_ImageContentRestrictedInput"]+scene.aoi_data[aoiname].features["numtransfrom_NormalImageContent"]
                scene.aoi_data[aoiname].features["proptransto_ImageContent"]=scene.aoi_data[aoiname].features["proptransto_ImageContentRestrictedInput"]+scene.aoi_data[aoiname].features["proptransto_NormalImageContent"]
                scene.aoi_data[aoiname].features["proptransfrom_ImageContent"]=scene.aoi_data[aoiname].features["proptransfrom_ImageContentRestrictedInput"]+scene.aoi_data[aoiname].features["proptransfrom_NormalImageContent"]
            else:
                scene.aoi_data[aoiname].features["numtransto_ImageContent"]=scene.aoi_data[aoiname].features["numtransto_NormalImageContent"]
                scene.aoi_data[aoiname].features["numtransfrom_ImageContent"]=scene.aoi_data[aoiname].features["numtransfrom_NormalImageContent"]
                scene.aoi_data[aoiname].features["proptransto_ImageContent"]=scene.aoi_data[aoiname].features["proptransto_NormalImageContent"]
                scene.aoi_data[aoiname].features["proptransfrom_ImageContent"]=scene.aoi_data[aoiname].features["proptransfrom_NormalImageContent"]
        else:
            if scene.aoi_data[aoiname].features.has_key("numtransto_ImageContentRestrictedInput"):
                scene.aoi_data[aoiname].features["numtransto_ImageContent"]=scene.aoi_data[aoiname].features["numtransto_ImageContentRestrictedInput"]
                scene.aoi_data[aoiname].features["numtransfrom_ImageContent"]=scene.aoi_data[aoiname].features["numtransfrom_ImageContentRestrictedInput"]
                scene.aoi_data[aoiname].features["proptransto_ImageContent"]=scene.aoi_data[aoiname].features["proptransto_ImageContentRestrictedInput"]
                scene.aoi_data[aoiname].features["proptransfrom_ImageContent"]=scene.aoi_data[aoiname].features["proptransfrom_ImageContentRestrictedInput"]
        """
        
        #fix transitions related to Content area
        if scene.aoi_data[aoiname].features.has_key("numtransto_NormalContent"):
            if scene.aoi_data[aoiname].features.has_key("numtransto_ContentRestrictedInput"):
                
                scene.aoi_data[aoiname].features["numtransto_Content"]=scene.aoi_data[aoiname].features["numtransto_ContentRestrictedInput"]+scene.aoi_data[aoiname].features["numtransto_NormalContent"]
                scene.aoi_data[aoiname].features["numtransfrom_Content"]=scene.aoi_data[aoiname].features["numtransfrom_ContentRestrictedInput"]+scene.aoi_data[aoiname].features["numtransfrom_NormalContent"]
                scene.aoi_data[aoiname].features["proptransto_Content"]=scene.aoi_data[aoiname].features["proptransto_ContentRestrictedInput"]+scene.aoi_data[aoiname].features["proptransto_NormalContent"]
                scene.aoi_data[aoiname].features["proptransfrom_Content"]=scene.aoi_data[aoiname].features["proptransfrom_ContentRestrictedInput"]+scene.aoi_data[aoiname].features["proptransfrom_NormalContent"]
            else:
                scene.aoi_data[aoiname].features["numtransto_Content"]=scene.aoi_data[aoiname].features["numtransto_NormalContent"]
                scene.aoi_data[aoiname].features["numtransfrom_Content"]=scene.aoi_data[aoiname].features["numtransfrom_NormalContent"]
                scene.aoi_data[aoiname].features["proptransto_Content"]=scene.aoi_data[aoiname].features["proptransto_NormalContent"]
                scene.aoi_data[aoiname].features["proptransfrom_Content"]=scene.aoi_data[aoiname].features["proptransfrom_NormalContent"]
        else:
            if scene.aoi_data[aoiname].features.has_key("numtransto_ContentRestrictedInput"):
                scene.aoi_data[aoiname].features["numtransto_Content"]=scene.aoi_data[aoiname].features["numtransto_ContentRestrictedInput"]
                scene.aoi_data[aoiname].features["numtransfrom_Content"]=scene.aoi_data[aoiname].features["numtransfrom_ContentRestrictedInput"]
                scene.aoi_data[aoiname].features["proptransto_Content"]=scene.aoi_data[aoiname].features["proptransto_ContentRestrictedInput"]
                scene.aoi_data[aoiname].features["proptransfrom_Content"]=scene.aoi_data[aoiname].features["proptransfrom_ContentRestrictedInput"]
