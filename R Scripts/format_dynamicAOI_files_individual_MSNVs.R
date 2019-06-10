
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
                                "81","46","50","82","84","85","88","89","90","91","92","93","95","97"))


#users to remove
#32, bad gaze, and no performance info
users <- subset(users, user_id != "32")
users <- subset(users, user_id != "35")
# 85 is missing trial 15

length <- nrow(users)

mmd_list <- as.character(c(3,5,9,11,18,20,27,28,30,60,62,66,72,74,76))

for (msnv in mmd_list){

  for (i in 1:length) {
  
    a_user <- as.character(users[i,1])
  
    #get the seg data
    setwd("c:/Users/admin/Desktop/Tobii Export/Segs")
    seg_export <- fread(paste(a_user, ".csv", sep=""), sep=",")
  
    setwd(paste("c:/Users/admin/Desktop/Tobii Export/aois_refsentences/", msnv, "_aoi",sep=""))
    fileConn<-file(paste("dynamic_",a_user, ".aoi", sep=""))
    segs <- c()
  
    a_row <- seg_export[mmd_id == msnv,]
    
    setwd("c:/Users/admin/Desktop/Tobii Export/aois_refsentences")
    aois <- fread(paste(msnv, "_sentence_fixed.aoi", sep=""), sep="\n", header=FALSE)
    
    for (k in 1 :nrow(aois)) {
      segs <- c(segs, aois[k,])
      segs <- c(segs, paste("#\t",a_row[,start],",",a_row[,end],"\t", sep=""))
    }
    
    setwd(paste("c:/Users/admin/Desktop/Tobii Export/aois_refsentences/", msnv, "_aoi",sep=""))
    writeLines(paste(segs, collapse="\n"), sep="", fileConn)
    close(fileConn)
  }
}


