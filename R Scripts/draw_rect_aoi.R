
library(magick)
library(stringr)

setwd("/Users/kristys/Documents/EMDAT-subtractive")

mmd_list <- as.character(c(3,5,9,11,20,27,28,30,60,62,66,72,74,76))
#mmd_list <- as.character(c(76))

for (msnv in mmd_list) {
  
  #read in image
  an_image <- image_read(paste("../msnv_screenshots/", msnv,".png",sep=""))
  #an_image <- image_read(paste(msnv,".png",sep=""))
  im <- image_draw(an_image)
  
  #read in AOI coordinates
  #my_aois <- fread(paste("R Scripts/SampleAOIs/", msnv,".aoi",sep=""), header = FALSE, sep = "\n")
  my_aois <- fread(paste("R Scripts/labels_AOIs/", msnv,".aoi",sep=""), header = FALSE, sep = "\n")
  
  #for (i in 1:2) {
  for (i in 1:nrow(my_aois)) {
    if (str_split(as.character(my_aois[i,]), "\t")[[1]][1] != 'Labels')
      next
    bars <- str_split(as.character(my_aois[i,]), "\t")[[1]][-1]
    
    bars <- bars[!sapply(bars, function(x) x == "")]
    
    top <- as.integer(str_split(bars[1], ",")[[1]][[2]])
    left <- as.integer(str_split(bars[1], ",")[[1]][[1]])
    width <- as.integer(str_split(bars[2], ",")[[1]][[1]]) - as.integer(str_split(bars[1], ",")[[1]][[1]])
    height <- as.integer(str_split(bars[3], ",")[[1]][[2]]) - as.integer(str_split(bars[2], ",")[[1]][[2]])
    
    rect(left, top + height, left + width, top, col = rgb(1, 0.2, 0.2, alpha = 0.2))
  }
  
  #image_write(im, path = paste(msnv,"_overall.png"), format = "png")
  image_write(im, path = paste(msnv,"_labels.png"), format = "png")
  
}
