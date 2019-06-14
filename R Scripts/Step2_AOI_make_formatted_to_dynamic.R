
# Takes static ref viz aoi files and makes them dynamic, with time invervals
# taken from trigger (intervention) seg files. Generated files can only be used 
# by the subtractive and dynamic boundaries EMDAT version. 

library(data.table)

setwd("/Users/kristys/Documents/MSNV_Adapt_Gaze_Analysis_2019/Eye_Tracking_Processing")
users <- fread("study2_user_list.csv")
msnv_ids <- as.character(c(27, 60, 11, 30, 62, 72, 28, 74, 5, 20, 76, 66, 9, 3))

for (user in users$user_id) {
  setwd("/Users/kristys/Documents/MSNV_Adapt_Gaze_Analysis_2019/Eye_Tracking_Processing")
  #segs <- fread(paste0("segs/", user, ".seg"), sep="\t") 
  segs <- fread(paste0("segs_control/", user, ".seg"), sep="\t") 
  
  setwd("../../EMDAT-subtractive")
  fileConn <- file(paste0('ref_viz_dynamic_aois_per_user/dynamic_' , user, ".aoi"))
  
  dyn_aois <- c()
  for (msnv in msnv_ids) {
    ref_viz <- fread(paste0('ref_viz/ref_viz_', msnv,".aoi"), sep="\n", header = FALSE)
    for (i in 1:nrow(ref_viz)) {
      seg_start <- segs[V1==msnv]$V3
      seg_end <- segs[V1==msnv]$V4
      aoi <- paste0(ref_viz[i], '\n#\t', seg_start, ',', seg_end)
      dyn_aois <- c(dyn_aois, aoi)
    }
  }
  
  writeLines(paste(dyn_aois, collapse="\n"), sep="", fileConn)
  close(fileConn)
}


