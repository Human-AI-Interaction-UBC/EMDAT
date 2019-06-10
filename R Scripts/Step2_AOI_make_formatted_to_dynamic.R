
# Format Seg files into EMDAT style
#
# Author: Dereck Toker
# Last Update: October 26, 2017

library(data.table)


# export: check, comma, quote, CR+LF
#mmd_order <- fread("User_data.csv")
#mmd_order <- subset(mmd_order, sel = -c(date_created))

#Master user_list
users <- data.frame(user_id = c("1","9","12","16","18","19","21","25","26","30","31","32","35","36",
                                "38","40","42","45","52","55","58","59","60","61","62","63","64","65",
                                "66","67","68","69","70","71","72","73","74","75","76","77","78","79","80",
                                "81","46","50","82","84","85","88","89","90","91","92","93","95","97")) ########


length <- nrow(users)


for (i in 1:length) {
  
  a_user <- as.character(users[i,1])
  
  #get the seg data
  setwd("c:/Users/admin/Desktop/Tobii Export/Segs")
  seg_export <- fread(paste(a_user, ".csv", sep=""), sep=",")
  
  fileConn<-file(paste("dynamic_",a_user, ".aoi", sep=""))
  segs <- c()
  
  for (j in 1:nrow(seg_export)) {
  
    a_row <- seg_export[j]
    
    setwd("c:/Users/admin/Desktop/Tobii Export/aois_refsentences")
    an_mmd <- a_row[,mmd_id]
    aois <- fread(paste0("formatted", an_mmd, ".aoi"), sep="\n", header=FALSE)
    
    for (k in 1 :nrow(aois)) {
      segs <- c(segs, aois[k,])
      segs <- c(segs, paste("#\t",a_row[,start],",",a_row[,end],"\t", sep=""))
    }
  }
  
  writeLines(paste(segs, collapse="\n"), sep="", fileConn)
  close(fileConn)
}


