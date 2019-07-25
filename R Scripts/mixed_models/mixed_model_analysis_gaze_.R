
# the normalization method

# Example of FDR:  5 x 8 gaze features to check
# 3 UCs, treatment, = 7 or 4 tests x 8 features per AOI family: FDR correction is 56 or 32
# Meara, VerbalWM, BarChartLit, Treatment, Meara*Treatment, VerbalWMMeara*Treatment, BarChartLitMeara*Treatment

# FDR:
# (Benjamini & Hochberg 1995).
# The obtained p-values from our models are ordered from smallest to largest
# such that the smallest p-value has a rank of i = 1, the next smallest has i = 2, etc. 
# Then we compare each individual p-value to its Benjamini-Hochberg critical threshold:
# of q = (i/m)alpha, where i is the rank, m is the total number of models, and alpha is set to 0.05.
# Next we find the largest p-value that has p <= q given its rank r, and then all p-values at rank i <= r are also considered significant.


library(data.table)
library(lmerTest)


#Step 1: Look for impact of UCs and Treatment on Gaze


c <- c("Legend_longestfixation",
       "Legend_meanfixationduration","Legend_numtransfrom_Labels",
       "Legend_numtransfrom_NonBars", "Legend_numtransfrom_Bars",
       "Legend_timetofirstfixation",
       "Legend_timetolastfixation","Legend_totaltimespent",
       "Labels_longestfixation",
       "Labels_numtransfrom_Legend",
       "Labels_numtransfrom_NonBars", "Labels_numtransfrom_Bars",
       "Labels_timetofirstfixation",
       "Labels_timetolastfixation","Labels_totaltimespent",
       "NonBars_longestfixation",
       "NonBars_meanfixationduration","NonBars_numtransfrom_Legend",
       "NonBars_numtransfrom_Labels", "NonBars_numtransfrom_Bars",
       "NonBars_proportionnum","NonBars_timetofirstfixation",
       "NonBars_timetolastfixation","NonBars_totaltimespent",
       "Bars_longestfixation",
       "Bars_meanfixationduration","Bars_numtransfrom_Legend",
       "Bars_numtransfrom_Labels", "Bars_numtransfrom_NonBars",
       "Bars_timetofirstfixation",
       "Bars_timetolastfixation","Bars_totaltimespent"
)


sink("UBC_standard_ReadingP_Oct2.txt")

for (n in c) {
  
  a_model <- paste(n," ~ Meara*Treatment + Verbal_WM*Treatment + (1 | mmd_id) + (1 | user_id)", sep="")
  
  test <- lmerTest::lmer(a_model, working_table, REML = TRUE)
  
  print(n)
  print(summary(test))
  
  
}

closeAllConnections()



#Step 2: Look for impact of relevant gaze metrics on performance



c <- c("Viz_fixationrate","Viz_longestfixation",
       "Viz_meanfixationduration","Viz_numtransfrom_Bars",
       "Viz_numtransfrom_Refs", "Viz_numtransfrom_Text",
       "Viz_proportionnum","Viz_proportiontime","Viz_proptransfrom_Bars",
       "Viz_proptransfrom_Refs","Viz_proptransfrom_Text","Viz_timetofirstfixation",
       "Viz_timetolastfixation","Viz_totaltimespent",
       "Text_fixationrate","Text_longestfixation",
       "Text_meanfixationduration","Text_numtransfrom_Bars",
)


#### Time:
sink("Correlation_of_gaze_speed_Oct2.txt")

for (n in c) {
  
  a_model <- paste("task_time ~ ", n, "*Treatment + (1 | mmd_id) + (1 | user_id)", sep="")
  
  test <- lmerTest::lmer(a_model, working_table, REML = TRUE)
  
  print(summary(test))
  
  
}

closeAllConnections()



### Accuracy
sink("Correlation_of_gaze_accurracy_Oct2.txt")

for (n in c) {
  
  a_model <- paste("accuracy ~ ", n, "*Treatment + (1 | mmd_id) + (1 | user_id)", sep="")
  
  test <- lmerTest::lmer(a_model, working_table, REML = TRUE)
  
  print(summary(test))
  
  
}

closeAllConnections()






#example for 2-way split:

#convert caracteristics to median split for post-hoc interpretation:
data_study_combined$VerbalWM_longest_median[data_study_combined$VerbalWM_longest <  median(data_study_combined$VerbalWM_longest)] <- "LowVerbalWM"
data_study_combined$VerbalWM_longest_median[data_study_combined$VerbalWM_longest >=  median(data_study_combined$VerbalWM_longest)] <- "HighVerbalWM"
data_study_combined$VerbalWM_longest_median <- as.factor(data_study_combined$VerbalWM_longest_median)

data_study_combined$BarChartLit_median[data_study_combined$BarChartLit <  median(data_study_combined$BarChartLit)] <- "LowBarChartLit"
data_study_combined$BarChartLit_median[data_study_combined$BarChartLit >=  median(data_study_combined$BarChartLit)] <- "HighBarChartLit"
data_study_combined$BarChartLit_median <- as.factor(data_study_combined$BarChartLit_median)


#re-specify new pruned models for pairwise:
speed_model_refined_median <- lmerTest::lmer(mmd_task_time ~ VerbalWM_longest_median +  MV1_median + CF2_median*treatment +
                                               (1 | user_id) + (1 | mmd_id), data_study_combined, REML = FALSE)
accuracy_model_refined_median <- lmerTest::lmer(mmd_accuracy ~ NAART_median + Meara_median*treatment + 
                                                  BarChartLit_median*treatment + 
                                                  (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE)



#**Pairwise Comparisons on SPEED**:
#INTERACTION effects:
obk1a <- lsmeans(speed_model_refined_median, pairwise ~ treatment | CF2_median, adjust = 'none')
obk1b <- lsmeans(speed_model_refined_median, pairwise ~ CF2_median | treatment, adjust = 'none')
obk13 <- lsmeans(speed_model_refined_median, pairwise ~ CF2_median*treatment, adjust = 'none') #full
t1a <- subset(summary(obk1a$contrasts), p.value < 1)
t1b <- subset(summary(obk1b$contrasts), p.value < 1)



#**Pairwise Comparisons on ACCURACY**:
#INTERACTION effects:
obk1a <- lsmeans(accuracy_model_refined_median, pairwise ~ treatment | Meara_median, adjust = "none")
obk1b <- lsmeans(accuracy_model_refined_median, pairwise ~ Meara_median | treatment, adjust = "none")
t1a <- subset(summary(obk1a$contrasts), p.value < 1)
t1b <- subset(summary(obk1b$contrasts), p.value < 1)





#if we want to do 3-way split:
#################3-wa split checks:

hist(data_study_combined[mmd_id == '3']$BarChartLit)
hist(data_study_combined[mmd_id == '3']$Meara)
hist(data_study_combined[mmd_id == '3']$CF2)

data_study_combined <- data_study_combined[order(BarChartLit,BarChartLit_raw)]
pivot_lowA <- data_study_combined[nrow(data_study_combined)*(1/3)]$BarChartLit
pivot_lowB <- data_study_combined[nrow(data_study_combined)*(1/3)]$BarChartLit_raw
pivot_highA <- data_study_combined[nrow(data_study_combined)*(2/3)]$BarChartLit
pivot_highB <- data_study_combined[nrow(data_study_combined)*(2/3)]$BarChartLit_raw

data_study_combined$BarChartLit_median[data_study_combined$BarChartLit <  pivot_lowA] <- "Low"
data_study_combined$BarChartLit_median[data_study_combined$BarChartLit ==  pivot_lowA & 
                                         data_study_combined$BarChartLit_raw <  pivot_lowB] <- "Low"
data_study_combined$BarChartLit_median[data_study_combined$BarChartLit < pivot_highA &
                                         data_study_combined$BarChartLit > pivot_lowA] <- "Medium"
data_study_combined$BarChartLit_median[data_study_combined$BarChartLit == pivot_lowA &
                                         data_study_combined$BarChartLit_raw >= pivot_lowB] <- "Medium"
data_study_combined$BarChartLit_median[data_study_combined$BarChartLit >=  pivot_highA] <- "High"

data_study_combined$BarChartLit_median <- as.factor(data_study_combined$BarChartLit_median)
data_study_combined$Visualization_literacy <- data_study_combined$BarChartLit_median


data_study_combined <- data_study_combined[order(Meara)]
pivot_low <- data_study_combined[nrow(data_study_combined)*(1/4)]$Meara
pivot_high <- data_study_combined[nrow(data_study_combined)*(3/4)]$Meara
data_study_combined$Meara_median[data_study_combined$Meara <  pivot_low] <- "LowMeara"
data_study_combined$Meara_median[data_study_combined$Meara < pivot_high &
                                   data_study_combined$Meara >= pivot_low] <- "MedMeara"
data_study_combined$Meara_median[data_study_combined$Meara >=  pivot_high] <- "HighMeara"
data_study_combined$Meara_median <- as.factor(data_study_combined$Meara_median)

data_study_combined <- data_study_combined[order(CF2)]
pivot_low <- data_study_combined[nrow(data_study_combined)*(1/4)]$CF2
pivot_high <- data_study_combined[nrow(data_study_combined)*(3/4)]$CF2
data_study_combined$CF2_median[data_study_combined$CF2 <=  pivot_low] <- "LowCF2"
data_study_combined$CF2_median[data_study_combined$CF2 < pivot_high &
                                 data_study_combined$CF2 > pivot_low] <- "MedCF2"
data_study_combined$CF2_median[data_study_combined$CF2 >=  pivot_high] <- "HighCF2"
data_study_combined$CF2_median <- as.factor(data_study_combined$CF2_median)

data_study_combined <- data_study_combined[order(MV1)]
pivot_low <- data_study_combined[nrow(data_study_combined)*(1/4)]$MV1
pivot_high <- data_study_combined[nrow(data_study_combined)*(3/4)]$MV1
data_study_combined$MV1_median[data_study_combined$MV1 <=  pivot_low] <- "LowMV1"
data_study_combined$MV1_median[data_study_combined$MV1 < pivot_high &
                                 data_study_combined$MV1 > pivot_low] <- "MedMV1"
data_study_combined$MV1_median[data_study_combined$MV1 >=  pivot_high] <- "HighMV1"
data_study_combined$MV1_median <- as.factor(data_study_combined$MV1_median)

data_study_combined <- data_study_combined[order(VerbalWM_longest)]
pivot_low <- data_study_combined[nrow(data_study_combined)*(1/4)]$VerbalWM_longest
pivot_high <- data_study_combined[nrow(data_study_combined)*(3/4)]$VerbalWM_longest
data_study_combined$VerbalWM_longest_median[data_study_combined$VerbalWM_longest <=  pivot_low] <- "LowVerbalWM"
data_study_combined$VerbalWM_longest_median[data_study_combined$VerbalWM_longest < pivot_high &
                                              data_study_combined$VerbalWM_longest > pivot_low] <- "MedVerbalWM"
data_study_combined$VerbalWM_longest_median[data_study_combined$VerbalWM_longest >=  pivot_high] <- "HighVerbalWM"
data_study_combined$VerbalWM_longest_median <- as.factor(data_study_combined$VerbalWM_longest_median)


data_study_combined <- data_study_combined[order(NAART)]
pivot_low <- data_study_combined[nrow(data_study_combined)*(1/4)]$NAART
pivot_high <- data_study_combined[nrow(data_study_combined)*(3/4)]$NAART
data_study_combined$NAART_median[data_study_combined$NAART <=  pivot_low] <- "LowNAART"
data_study_combined$NAART_median[data_study_combined$NAART < pivot_high &
                                   data_study_combined$NAART > pivot_low] <- "MedNAART"
data_study_combined$NAART_median[data_study_combined$NAART >=  pivot_high] <- "HighNAART"
data_study_combined$NAART_median <- as.factor(data_study_combined$NAART_median)






