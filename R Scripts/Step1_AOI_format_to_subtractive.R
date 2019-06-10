  
library(magick)
library(stringr)
library(data.table)

mmd_list <- as.character(c(3,5,9,11,20,27,28,30,60,62,66,72,74,76))

for (i in 1:length(mmd_list)){
  
  #read in coordinates
  setwd("c:/Users/admin/Desktop/BT_EyeTracking/Tobii Export/aois/XOffset_fixed") ###########
  my_data <- fread(paste(mmd_list[i],".aoi",sep=""), sep="\n", header = FALSE)
  
  Text <- as.character(my_data[1,])
  Viz <- as.character(my_data[2,])
  Ref <- as.character(my_data[3,])
  Bars <- as.character(my_data[4,])
    
  Ref_new <- gsub(";", "\nRefs", Ref)
  Ref_subtractive <- gsub("Refs", "", Ref)
  Ref_subtractive <- gsub(";", "\t;", Ref_subtractive)
  
  Bars_new <- gsub(";", "\nBars", Bars)
  Bars_subtractive <- gsub("Bars", "", Bars)
  Bars_subtractive <- gsub(";", "\t;", Bars_subtractive)  
  
  Text <- paste(Text, "\t--",Ref_subtractive,"\n",sep="")
  
  Viz <- paste(Viz, "\t--",Bars_subtractive,"\n",sep="")
  
  Ref_new <- paste(Ref_new, "\n", sep="")
  
  fileConn<-file(paste("formatted",mmd_list[i], ".aoi", sep=""))
  results <- c(Text, Viz, Ref_new, Bars_new)
  writeLines(results, sep="", fileConn)
  close(fileConn)

}
