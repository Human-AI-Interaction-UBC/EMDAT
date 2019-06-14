
# Produce static aoi files per msnv that has 4 AOIs: refs combined, bars combined,
# and rest of text and rest of viz. Generated files are used as input to script
# that makes them dynamic.

library(magick)
library(stringr)
library(data.table)

setwd("/Users/kristys/Documents/EMDAT-subtractive")

mmd_list <- as.character(c(3,5,9,11,20,27,28,30,60,62,66,72,74,76))
#mmd_list <- as.character(c(3))

for (mmd in mmd_list) {
  txt_viz <- fread(paste('R Scripts/overall_aois/', mmd,".aoi",sep=""), sep="\n", header = FALSE)
  
  Text <- as.character(txt_viz[1,])
  Viz <- as.character(txt_viz[2,])
  
  nr_bars <- fread(paste0('../MSNV_Adapt_Gaze_Analysis_2019/Eye_Tracking_Processing/non_relevant_aois_adjusted/', mmd, '_NR.aoi'), sep="\n", header = FALSE)
  nr_bars <- nr_bars[nrow(nr_bars)]
  nr_bars_combined <- gsub('overall_list', 'Bar', nr_bars)
  nr_bars_combined <- strtrim(nr_bars_combined, nchar(nr_bars_combined)-1)
  nr_bars_combined <- gsub(';', '\nBar', nr_bars_combined)
  rel_bars <- fread(paste0('../MSNV_Adapt_Gaze_Analysis_2019/Eye_Tracking_Processing/relevant_aois_adjusted/', mmd, '_Relevant.aoi'), sep="\n", header = FALSE)
  rel_bars <- rel_bars[nrow(rel_bars)]
  rel_bars_combined <- gsub('overall_list', '\nBar', rel_bars)
  rel_bars_combined <- strtrim(rel_bars_combined, nchar(rel_bars_combined)-1)
  rel_bars_combined <- gsub(';', '\nBar', rel_bars_combined)
  bars_combined <- paste0(nr_bars_combined, rel_bars_combined)
  
  Bars_subtractive <- paste0(nr_bars[1], rel_bars[1])
  Bars_subtractive <- gsub('overall_list', '', Bars_subtractive)
  Bars_subtractive <- strtrim(Bars_subtractive, nchar(Bars_subtractive)-1)
  
  #refs <- fread(paste0('../AOI_ATUAV_Experimenter_Platform/ref_aois_adaptive/', mmd, '.aoi'), sep="\n", header = FALSE)
  refs <- fread(paste0('../AOI_ATUAV_Experimenter_Platform/ref_aois_control/', mmd, '.aoi'), sep="\n", header = FALSE)
  refs <- refs[nrow(refs)]
  refs_combined <- gsub(paste0('overall_', mmd), 'Ref', refs)
  refs_combined <- paste0(strtrim(refs_combined, nchar(refs_combined)-1), '\n')
  refs_combined <- gsub(';', '\nRef', refs_combined)
  
  Refs_subtractive <- gsub(paste0('overall_', mmd), '', refs[1])
  Refs_subtractive <- strtrim(Refs_subtractive, nchar(Refs_subtractive)-1)
  
  Text <- paste0(Text, "\t--",Refs_subtractive,"\n")
  Viz <- paste0(Viz, "\t--",Bars_subtractive,"\n")
  
  #fileConn<-file(paste0("ref_viz/ref_viz_",mmd, ".aoi"))
  fileConn<-file(paste0("ref_viz_control/ref_viz_",mmd, ".aoi"))
  results <- c(Text, Viz, refs_combined, bars_combined)
  writeLines(results, sep="", fileConn)
  close(fileConn)

}
