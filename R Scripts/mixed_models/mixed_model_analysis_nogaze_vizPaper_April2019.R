library(data.table)
library(lmerTest)
library(lsmeans)


library(ggplot2)
library(dplyr)
library(Rmisc)

#setwd("C:/Users/admin/Desktop/MSNV 2 UBC/MergedData")
setwd("C:/Users/admin/Dropbox/PhD/Kong_MMD/Study 2 UBC/MergedData")

#read in data files
data_study1 <- fread("mmd_study1_ubc_final_result_april5.csv")
data_study2 <- fread("mmd_study2_ubc_final_result_april5.csv")


#Drop 15 users for bad data quality or misaligned calibration:
data_study2 <- data_study2[!user_id %in% c("msnv65","msnv11","msnv48","msnv28","msnv16","msnv74",
                                           "msnv3","msnv53","msnv64","msnv26","msnv36","msnv70",
                                           "msnv76","msnv83","msnv84")]

#drop msnv19 for no trigger logs and msnv23 for no VerbalWM score
data_study2 <- data_study2[!user_id %in% c("msnv19","msnv23")]

#user characteristic data for study2:
user_chars_study2 <- fread("User_Chars_Study2_April5.csv")
data_study2 <- merge(data_study2, user_chars_study2, by = "user_id")


data_study1$userful <- 0
data_study1$distracting <- 0
data_study1$confusing <- 0
data_study1$right_timing <- 0

data_study1 <- subset(data_study1, sel = c(user_id, mmd_id, mmd_task_time, mmd_accuracy, ease, interest, bar_pref,
                                           N4C, VARK_V, VARK_R, VerbalWM_longest, BarChartLit, BarChartLit_raw, VisualWM_Mean,
                                           PS, Meara, CF2, MV1, NAART,
                                           TIPI_X, TIPI_A, TIPI_C, TIPI_ES, TIPI_O, userful, distracting, confusing, right_timing))
data_study2 <- subset(data_study2, sel = c(user_id, mmd_id, mmd_task_time, mmd_accuracy, ease, interest, bar_pref,
                                           N4C, VARK_V, VARK_R, VerbalWM_longest, BarChartLit, BarChartLit_raw, VisualWM_Mean,
                                           PS, Meara, CF2, MV1, NAART,
                                           TIPI_X, TIPI_A, TIPI_C, TIPI_ES, TIPI_O, userful, distracting, confusing, right_timing))


#annotate the 2 groups:
data_study1$treatment = 'Control'
data_study2$treatment = 'Adaptive'

#analysis of both studies combined:
data_study_combined <- rbind(data_study1, data_study2)
data_study_combined$treatment = as.factor(data_study_combined$treatment)
data_study_combined$mmd_id = as.factor(data_study_combined$mmd_id)



#trigger data:
trigger_ratio <- fread("trigger_ratio_and_count_full_april27.csv")
trigger_ratio <- subset(trigger_ratio, sel = c(user_id, mmd_id, ratio_triggered,triggers))
trigger_ratio$mmd_id <- as.factor(trigger_ratio$mmd_id)
data_study_combined <- merge(data_study_combined, trigger_ratio, by = c('mmd_id', 'user_id'), all.x = TRUE)
data_study_combined[is.na(ratio_triggered)]$ratio_triggered <- 0


#compare_stats <- data_study_combined[, .(Meara = mean(Meara)), by = treatment]

#data_study_combined <- data_study_combined[!(ratio_triggered < 0.85 & treatment == 'Adaptive')]

#write.csv(data_study_combined, "combined_data_for_Seb_April5.csv",row.names = FALSE)
#mixed model testing:
speed_model <- lmerTest::lmer(mmd_task_time ~ #N4C*treatment + #VARK_V*treatment + VARK_R*treatment + 
                                VerbalWM_longest*treatment + BarChartLit*treatment + MV1*treatment + NAART*treatment +
                                PS*treatment + Meara*treatment + CF2*treatment + VisualWM_Mean*treatment +
                                #TIPI_X*treatment + TIPI_A*treatment + TIPI_C*treatment + TIPI_ES*treatment + TIPI_O*treatment +
                                (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                                control = lmerControl(optimizer ="Nelder_Mead"))
step_speed_model <- step(speed_model)
step_speed_model
print(anova(speed_model))

accuracy_model <- lmerTest::lmer(mmd_task_time ~ treatment +
                               # TIPI_X*treatment + TIPI_A*treatment + TIPI_C*treatment + TIPI_ES*treatment + TIPI_O*treatment +
                                  (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                               control = lmerControl(optimizer ="Nelder_Mead"))
step_accuracy_model <- step(accuracy_model)
step_accuracy_model
#print(anova(accuracy_model))
print(anova(accuracy_model))

accuracy_model <- lmerTest::lmer(mmd_accuracy ~ treatment + 
                                   (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                                 control = lmerControl(optimizer ="Nelder_Mead"))


#construct stepwise identified models:
speed_model_refined <- lmerTest::lmer(mmd_task_time ~ MV1 + VerbalWM_longest +
                                        (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                                      control = lmerControl(optimizer ="Nelder_Mead"))

print(anova(speed_model_refined))

accuracy_model_refined <- lmerTest::lmer(mmd_accuracy ~ NAART +
                                           BarChartLit*treatment + Meara*treatment +
                                           (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                                         control = lmerControl(optimizer ="Nelder_Mead"))
print(anova(accuracy_model_refined))


#effect size accuracy: 0.34
r <- sqrt((3.565)^2/((3.565)^2 + 97))
#speed: 0.13


#convert caracteristics to median split for post-hoc interpretation:
data_study_combined$VerbalWM_longest_median[data_study_combined$VerbalWM_longest <  median(data_study_combined$VerbalWM_longest)] <- "LowVerbalWM"
data_study_combined$VerbalWM_longest_median[data_study_combined$VerbalWM_longest >=  median(data_study_combined$VerbalWM_longest)] <- "HighVerbalWM"
data_study_combined$VerbalWM_longest_median <- as.factor(data_study_combined$VerbalWM_longest_median)

data_study_combined$BarChartLit_median[data_study_combined$BarChartLit <  median(data_study_combined$BarChartLit)] <- "LowBarChartLit"
data_study_combined$BarChartLit_median[data_study_combined$BarChartLit >=  median(data_study_combined$BarChartLit)] <- "HighBarChartLit"
data_study_combined$BarChartLit_median <- as.factor(data_study_combined$BarChartLit_median)

data_study_combined$VisualWM_Mean_median[data_study_combined$VisualWM_Mean <  median(data_study_combined$VisualWM_Mean)] <- "LowVisualWM"
data_study_combined$VisualWM_Mean_median[data_study_combined$VisualWM_Mean >=  median(data_study_combined$VisualWM_Mean)] <- "HighVisualWM"
data_study_combined$VisualWM_Mean_median <- as.factor(data_study_combined$VisualWM_Mean_median)

data_study_combined$PS_median[data_study_combined$PS <  median(data_study_combined$PS)] <- "LowPS"
data_study_combined$PS_median[data_study_combined$PS >=  median(data_study_combined$PS)] <- "HighPS"
data_study_combined$PS_median <- as.factor(data_study_combined$PS_median)

data_study_combined$Meara_median[data_study_combined$Meara <  median(data_study_combined$Meara)] <- "LowMeara"
data_study_combined$Meara_median[data_study_combined$Meara >=  median(data_study_combined$Meara)] <- "HighMeara"
data_study_combined$Meara_median <- as.factor(data_study_combined$Meara_median)

data_study_combined$NAART_median[data_study_combined$NAART <  median(data_study_combined$NAART)] <- "LowNAART"
data_study_combined$NAART_median[data_study_combined$NAART >=  median(data_study_combined$NAART)] <- "HighNAART"
data_study_combined$NAART_median <- as.factor(data_study_combined$NAART_median)

data_study_combined$CF2_median[data_study_combined$CF2 <=  median(data_study_combined$CF2)] <- "LowCF2"
data_study_combined$CF2_median[data_study_combined$CF2 >  median(data_study_combined$CF2)] <- "HighCF2"
data_study_combined$CF2_median <- as.factor(data_study_combined$CF2_median)

data_study_combined$MV1_median[data_study_combined$MV1 <  median(data_study_combined$MV1)] <- "LowMV1"
data_study_combined$MV1_median[data_study_combined$MV1 >=  median(data_study_combined$MV1)] <- "HighMV1"
data_study_combined$MV1_median <- as.factor(data_study_combined$MV1_median)




#construct stepwise models for pairwise:
speed_model_refined_median <- lmerTest::lmer(mmd_task_time ~ VerbalWM_longest_median +  MV1_median + CF2_median*treatment +
                                          (1 | user_id) + (1 | mmd_id), data_study_combined, REML = FALSE)
accuracy_model_refined_median <- lmerTest::lmer(mmd_accuracy ~ NAART_median + Meara_median*treatment + 
                                           BarChartLit_median*treatment + 
                                             (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE)


#**Pairwise Comparisons on SPEED**:
#INTERACTION effects:
obk1a <- lsmeans(speed_model_refined_median, pairwise ~ treatment | CF2_median, adjust = 'none')
obk1b <- lsmeans(speed_model_refined_median, pairwise ~ CF2_median | treatment, adjust = 'none')
t1a <- subset(summary(obk1a$contrasts), p.value < 1)
t1b <- subset(summary(obk1b$contrasts), p.value < 1)


#MAIN effects:
### Overall, low VerbaWM users spend sig. more time on task: ~10 seconds
### Overall, high MV1 users spend sig. more time on task: ~10 seconds
### Overall, high barchartlit spend sig. more time on task: ~7 secnds longer

s1_stats <- data_study_combined %>% group_by(MV1_median) %>% summarise(mmd_task_time = mean(mmd_task_time))


#**Pairwise Comparisons on ACCURACY**:
#INTERACTION effects:
obk1a <- lsmeans(accuracy_model_refined_median, pairwise ~ treatment | Meara_median, adjust = "none")
obk1b <- lsmeans(accuracy_model_refined_median, pairwise ~ Meara_median | treatment, adjust = "fdr")
t1a <- subset(summary(obk1a$contrasts), p.value < 1)
t1b <- subset(summary(obk1b$contrasts), p.value < 1)
### In the adaptive condition: high Merara users are sig. more accurate than low Meara users: ~8.5%

obk2a <- lsmeans(accuracy_model_refined_median, pairwise ~ treatment*BarChartLit_median, adjust = "fdr")

obk2a <- lsmeans(accuracy_model_refined_median, pairwise ~ treatment | BarChartLit_median, adjust = "none")
obk2b <- lsmeans(accuracy_model_refined_median, pairwise ~ BarChartLit_median | treatment, adjust = "fdr")
t2a <- subset(summary(obk2a$contrasts), p.value < 1)
t2b <- subset(summary(obk2b$contrasts), p.value < 1)
### Low barchartlit is more accurate in the adaptive vs control p = .08 (marginal)


obk2a <- lsmeans(accuracy_model_refined_median, pairwise ~ treatment | PS_median, adjust = "fdr")
obk2b <- lsmeans(accuracy_model_refined_median, pairwise ~ BarChartLit_median | treatment, adjust = "fdr")
t2a <- subset(summary(obk2a$contrasts), p.value < 1)
t2b <- subset(summary(obk2b$contrasts), p.value < 1)


sss <- summarySE(data_study_combined, measurevar="mmd_accuracy", groupvars=c("BarChartLit","treatment"))
ggplot(sss, aes(x=BarChartLit, y=mmd_accuracy, group=treatment)) + 
  geom_errorbar(aes(ymin=mmd_accuracy-ci*0.8, ymax=mmd_accuracy+ci*0.8), width=.1, position=position_dodge(width = 0.2)) +
  geom_line(aes(color=treatment)) +
  geom_point(aes(color=treatment))


#MAIN effects:
### Overall, users are more accurate with the adaptive version: ~2.2%
### Overall High NAART users are sig. more accurate than low NAART users: ~0.8%


s1_stats <- data_study_combined %>% group_by(CF2_median) %>% summarise(mmd_task_time = mean(mmd_task_time))

sss <- summarySE(data_study_combined, measurevar="mmd_task_time", groupvars=c("CF2","treatment"))

ggplot(sss, aes(x=CF2, y=mmd_task_time, colour=treatment)) + 
  geom_errorbar(aes(ymin=mmd_task_time-ci*0.8, ymax=mmd_task_time+ci*0.8), width=.1, position=position_dodge(width = 0.2)) +
  geom_line(aes(color=treatment)) +
  geom_point(position=position_dodge(width = 0.2))


s1_stats <- data_study_combined %>% group_by(treatment,BarChartLit_median) %>% summarise(mmd_accuracy = mean(mmd_accuracy))
ggplot(s1_stats, aes(x = BarChartLit_median, y = mmd_accuracy, group = treatment)) +  
  geom_line(aes(color=treatment)) +
geom_point(aes(color=treatment))

s1_stats <- data_study_combined %>% group_by(treatment,mmd_id) %>% summarise(mmd_accuracy = mean(mmd_accuracy))
s1_stats <- data_study_combined[CF2_median == 'LowBarChartLit'] %>% group_by(treatment,mmd_id) %>% summarise(mmd_accuracy = mean(mmd_accuracy))
s1_stats$mmd_id <- as.factor(s1_stats$mmd_id)
ggplot(s1_stats, aes(x = mmd_id, y = mmd_accuracy, fill =treatment)) +  geom_bar(position = "dodge", stat = "identity")

s1_stats <- data_study_combined %>% group_by(treatment,mmd_id) %>% summarise(mmd_task_time = mean(mmd_task_time))
ggplot(s1_stats, aes(x = BarChartLit_median, y = mmd_task_time, group = treatment)) +  
  geom_bar(aes(color=treatment)) +
  geom_point(aes(color=treatment))

s1_stats <- data_study_combined[CF2_median == 'HighCF2'] %>% group_by(treatment,mmd_id) %>% summarise(mmd_task_time = mean(mmd_task_time))
s1_stats$mmd_id <- as.factor(s1_stats$mmd_id)
ggplot(s1_stats, aes(x = mmd_id, y = mmd_task_time, fill =treatment)) +  geom_bar(position = "dodge", stat = "identity")


#******Subjective Measures:
ease_model <- lmerTest::lmer(ease ~ #N4C*treatment + VARK_V*treatment + VARK_R*treatment +
                               VerbalWM_longest*treatment + BarChartLit*treatment + MV1*treatment + NAART*treatment +
                               PS*treatment + Meara*treatment + CF2*treatment + VisualWM_Mean*treatment + NAART*treatment +
                               #TIPI_X*treatment + TIPI_A*treatment + TIPI_C*treatment + TIPI_ES*treatment + TIPI_O*treatment +
                               (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                             control = lmerControl(optimizer ="Nelder_Mead"))
step_ease_model <- step(ease_model)
step_ease_model

interest_model <- lmerTest::lmer(interest  ~ #N4C*treatment + VARK_V*treatment + VARK_R*treatment +
                                   VerbalWM_longest*treatment + BarChartLit*treatment + MV1*treatment + NAART*treatment +
                                   PS*treatment + Meara*treatment + CF2*treatment + VisualWM_Mean*treatment +
                                   #TIPI_X*treatment + TIPI_A*treatment + TIPI_C*treatment + TIPI_ES*treatment + TIPI_O*treatment +
                                   (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                                 control = lmerControl(optimizer ="Nelder_Mead"))
step_interest_model <- step(interest_model)
step_interest_model

#construct stepwise identified models:

interest_model_refined <- lmerTest::lmer(interest ~ NAART +
                                       (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE,
                                       control = lmerControl(optimizer ="Nelder_Mead"))
print(anova(interest_model_refined))


#MAIN effects on EASE**::
### Overall High Disembedding users rated the documents as easier to understand compared to low Disembedding users

#MAIN effects on INTEREST**::
### Overall High NAART users were more interested compared to low NAART users


s1_stats <- data_study_combined %>% group_by(NAART_median) %>% summarise(interest = mean(interest))


# The obtained p-values from our models are ordered from smallest to largest,
# such that the smallest p-value has a rank of    i = 1, the next smallest
# has i = 2, etc. Then we compare each individual p-value to its Benjamini-Hochberg
# critical threshold of q = (i/m)alpha, where i is the rank, m is the total number of
# models, and alpha is set to 0.05. Next we find the largest p-value that has p < q
# given its rank r, and then all p-values at rank i <= r are also considered significant.
# Applying the Benjamini-Hochberg procedure to our results yielded a critical threshold
# of q = .0273, obtained at rank r = 30.




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

#PLOTS:
sss <- summarySE(data_study_combined, measurevar="mmd_task_time", groupvars=c("CF2_median","treatment"))
sss$CF2_median <- factor(sss$CF2_median, levels(sss$CF2_median)[c(2,3,1)])
ggplot(sss, aes(x=CF2_median, y=mmd_task_time, group=treatment)) + 
  geom_errorbar(aes(ymin=mmd_task_time-ci*0.95, ymax=mmd_task_time+ci*0.95, color=treatment), width=.1, position=position_dodge(width = 0.07)) +
  geom_line(aes(color=treatment)) +
  geom_point(aes(color=treatment))

sss <- summarySE(data_study_combined, measurevar="mmd_accuracy", groupvars=c("Meara_median","treatment"))
sss$Meara_median <- factor(sss$Meara_median, levels(sss$Meara_median)[c(2,3,1)])
ggplot(sss, aes(x=Meara_median, y=mmd_accuracy, group=treatment)) + 
  geom_errorbar(aes(ymin=mmd_accuracy-ci*0.95, ymax=mmd_accuracy+ci*0.95, color=treatment), width=.1, position=position_dodge(width = 0.07)) +
  geom_line(aes(color=treatment)) +
  geom_point(aes(color=treatment))


data_study_combined$Task_accuracy <- data_study_combined$mmd_accuracy
data_study_combined$Task_time <- data_study_combined$mmd_task_time
data_study_combined$Group <- data_study_combined$treatment

sss <- summarySE(data_study_combined, measurevar="Task_accuracy", groupvars=c("Visualization_literacy","Group"))
sss$Visualization_literacy <- factor(sss$Visualization_literacy, levels(sss$Visualization_literacy)[c(2,3,1)])
ggplot(sss, aes(x=Visualization_literacy, y=Task_accuracy, group=Group)) + 
  geom_errorbar(aes(ymin=Task_accuracy-ci*0.95, ymax=Task_accuracy+ci*0.95, color=Group),
                width=.15, position=position_dodge(width = 0.07), size = 0.75, show_guide=FALSE) +
  geom_line(aes(color=Group,linetype = Group), size = 1.5) +
  geom_point(aes(color=Group)) + #ylim(0,0.85) + 
  theme(legend.key.size =  unit(0.5, "in")) +
  scale_x_discrete(labels=c("Low\n(33 users)", "Medium\n(35 users)", "High\n(36 users)"))
  #scale_linetype_manual(name="Group: ",values=c(Adaptive="dashed", Control="solid"), color=Group)


#construct stepwise models for pairwise:
speed_model_refined_median <- lmerTest::lmer(mmd_task_time ~ VerbalWM_longest_median +  MV1_median + BarChartLit_median*treatment +
                                               (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE)

accuracy_model_refined_median <- lmerTest::lmer(mmd_accuracy ~ NAART_median +
                                                  BarChartLit_median*treatment +
                                                  (1 | user_id) + (1 | mmd_id), data_study_combined, REML = TRUE)

obk2 <- lsmeans(accuracy_model_refined_median, pairwise ~ treatment*BarChartLit_median, adjust = 'fdr')
t2 <- summary(obk2$contrasts)

#barChartLit accuracy low vs adptive vs control: r = 0.33
#r <- sqrt((3.4294)^2/((3.4294)^2 + 96))
#barChartLit accuracy adaptive low vs high accuracy: r = 0.28
#r <- sqrt((-2.8185537)^2/((-2.8185537)^2 + 96))

#barChartLit speed low vs adptive vs control: r = 0.15
#r <- sqrt((1.53211315)^2/((1.53211315)^2 + 95))
# Cohen 1988/1992
#r = .1 (small)
#r = .3 (medium)
#r = .5 (large)s

#Subjective checks for adaptive only:
subjective_adaptive <- data_study_combined[treatment == 'Adaptive' & mmd_id == 3]

a1 <- kruskal.test(userful ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'MedBarChartLit'])
a2 <- kruskal.test(userful ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'LowBarChartLit'])
a3 <- kruskal.test(userful ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'HighBarChartLit'])
b1 <- kruskal.test(distracting ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'MedBarChartLit'])
b2 <- kruskal.test(distracting ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'LowBarChartLit'])
b3 <- kruskal.test(distracting ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'HighBarChartLit'])
c1 <- kruskal.test(confusing ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'MedBarChartLit'])
c2 <- kruskal.test(confusing ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'LowBarChartLit'])
c3 <- kruskal.test(confusing ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'HighBarChartLit'])
d1 <- kruskal.test(right_timing ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'MedBarChartLit'])
d2 <- kruskal.test(right_timing ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'LowBarChartLit'])
d3 <- kruskal.test(right_timing ~ BarChartLit_median, data = subjective_adaptive[BarChartLit_median != 'HighBarChartLit'])
a1 <- a1$p.value
a2 <- a2$p.value
a3 <- a3$p.value
b1 <- b1$p.value
b2 <- b2$p.value
b3 <- b3$p.value
c1 <- c1$p.value
c2 <- c2$p.value
c3 <- c3$p.value
d1 <- d1$p.value
d2 <- d2$p.value
d3 <- d3$p.value

s1_stats <- subjective_adaptive[BarChartLit_median != 'HighBarChartLit', .(right_timing = mean(right_timing)), by = BarChartLit_median]
s2_stats <- subjective_adaptive[BarChartLit_median != 'MedBarChartLit', .(right_timing = mean(right_timing)), by = BarChartLit_median]
s3_stats <- subjective_adaptive[BarChartLit_median != 'HighBarChartLit', .(distracting = mean(distracting)), by = BarChartLit_median]
s4_stats <- subjective_adaptive[Meara_median != 'HighMeara', .(useful = mean(userful)), by = Meara_median]
s5_stats <- subjective_adaptive[BarChartLit_median != 'LowBarChartLit', .(distracting = mean(distracting)), by = BarChartLit_median]


#mixed model to check for impact of trigger ratio:
subjective_adaptive <- data_study_combined[treatment == 'Adaptive']


triggers_user <- subjective_adaptive[, .(average_ratio = round(mean(ratio_triggered),2)), by = "user_id"]
triggers_user <- triggers_user[order(average_ratio)]
ggplot(triggers_user, aes(x = user_id, y = average_ratio)) +  geom_bar(stat = "identity") +
  scale_x_discrete(limits=triggers_user$user_id) + theme(axis.text.x = element_text(angle = 90, hjust = 1))


sss <- subjective_adaptive[,.(trigger_ratio = mean(trigger_ratio)), by = 'mmd_id']
sss$mmd_id <- as.factor(sss$mmd_id)
ggplot(sss, aes(x = mmd_id, y = trigger_ratio, group=1)) + geom_line() + geom_point()

speed_model <- lmerTest::lmer(mmd_task_time ~ triggers +
                                (1 | user_id) + (1 | mmd_id), subjective_adaptive, REML = TRUE,
                              control = lmerControl(optimizer ="Nelder_Mead"))
print(anova(speed_model))
#effect size: 0.55
#r <- sqrt((8.658)^2/((8.658)^2 + 171))

main_effect_time <- subjective_adaptive[,.(mmd_task_time = mean(mmd_task_time)), by = 'ratio_triggered']


accuracy_model <- lmerTest::lmer(mmd_accuracy ~ triggers +
                                   (1 | user_id) + (1 | mmd_id), subjective_adaptive, REML = TRUE,
                                 control = lmerControl(optimizer ="Nelder_Mead"))
print(anova(accuracy_model))

ease_model <- lmerTest::lmer(ease ~ triggers +
                               (1 | user_id) + (1 | mmd_id), subjective_adaptive, REML = TRUE,
                             control = lmerControl(optimizer ="Nelder_Mead"))
print(anova(ease_model))

interest_model <- lmerTest::lmer(interest ~ ratio_triggered +
                                   (1 | user_id) + (1 | mmd_id), subjective_adaptive, REML = TRUE,
                                 control = lmerControl(optimizer ="Nelder_Mead"))
print(anova(interest_model))



speed_model <- lmerTest::lmer(mmd_task_time ~ NAART_median*ratio_triggered_median +
                                (1 | user_id) + (1 | mmd_id), subjective_adaptive, REML = TRUE,
                              control = lmerControl(optimizer ="Nelder_Mead"))
interest_model <- lmerTest::lmer(interest ~ Meara_median*ratio_triggered_median + BarChartLit_median*ratio_triggered_median +
                                   (1 | user_id) + (1 | mmd_id), subjective_adaptive, REML = TRUE,
                                 control = lmerControl(optimizer ="Nelder_Mead"))

sss <- summarySE(subjective_adaptive, measurevar="mmd_task_time", groupvars=c("ratio_triggered_median","NAART_median"))
sss$NAART_median <- factor(sss$NAART_median, levels(sss$NAART_median)[c(2,3,1)])
ggplot(sss, aes(x=NAART_median, y=mmd_task_time, group=ratio_triggered_median)) + 
  geom_errorbar(aes(ymin=mmd_task_time-ci*0.95, ymax=mmd_task_time+ci*0.95, color=ratio_triggered_median), width=.1, position=position_dodge(width = 0.07)) +
  geom_line(aes(color=ratio_triggered_median)) +
  geom_point(aes(color=ratio_triggered_median))

sss <- summarySE(subjective_adaptive, measurevar="interest", groupvars=c("ratio_triggered_median","Meara_median"))
sss$Meara_median <- factor(sss$Meara_median, levels(sss$Meara_median)[c(2,3,1)])
ggplot(sss, aes(x=Meara_median, y=interest, group=ratio_triggered_median)) + 
  geom_errorbar(aes(ymin=interest-ci*0.95, ymax=interest+ci*0.95, color=ratio_triggered_median), width=.1, position=position_dodge(width = 0.07)) +
  geom_line(aes(color=ratio_triggered_median)) +
  geom_point(aes(color=ratio_triggered_median))


obks <- lsmeans(speed_model, pairwise ~ NAART_median*ratio_triggered_median, adjust = 'none')
ts <- summary(obks$contrasts)
obki <- lsmeans(interest_model, pairwise ~ Meara_median*ratio_triggered_median, adjust = 'none')
ti <- summary(obki$contrasts)

sss <- summarySE(subjective_adaptive, measurevar="mmd_task_time", groupvars=c("not_triggered"))
ggplot(sss, aes(x = not_triggered, y = mmd_task_time, group=1)) + geom_line() + geom_point()

ggplot(sss, aes(x=not_triggered, y=mmd_task_time, group=1)) + 
  geom_errorbar(aes(ymin=mmd_task_time-ci*0.95, ymax=mmd_task_time+ci*0.95), width=.1, position=position_dodge(width = 0.07)) +
  geom_line() + geom_point()

sss <- summarySE(subjective_adaptive, measurevar="ease", groupvars=c("ratio_triggered"))
ggplot(sss, aes(x = ratio_triggered, y = ease, group=1)) + geom_line() + geom_point()

ggplot(sss, aes(x=ratio_triggered, y=ease, group=1)) + 
  geom_errorbar(aes(ymin=ease-ci*0.95, ymax=ease+ci*0.95), width=.1, position=position_dodge(width = 0.07)) +
  geom_line() + geom_point()


sss <- summarySE(subjective_adaptive, measurevar="mmd_task_time", groupvars=c("NAART_median","ratio_triggered"))
ggplot(sss, aes(x=ratio_triggered, y=mmd_task_time, group=NAART_median)) + 
  geom_errorbar(aes(ymin=mmd_task_time-ci*0.95, ymax=mmd_task_time+ci*0.95, color=NAART_median), width=.1, position=position_dodge(width = 0.07)) +
  geom_line(aes(color=NAART_median)) +
  geom_point(aes(color=NAART_median))


#Trigger Model
trigger_model <- lmerTest::lmer(ratio_triggered ~ BarChartLit +
                                (1 | user_id) + (1 | mmd_id), subjective_adaptive, REML = TRUE,
                                control = lmerControl(optimizer ="Nelder_Mead"))
step_trigger_model <- step(trigger_model)
step_trigger_model


#Triggers on Subjective:
subjective_adaptive2 <- subjective_adaptive[, .(sum_triggered = sum(triggers)), by = 'user_id']
data_study2_subj <- data_study2[mmd_id == 3]
subjective_adaptive2 <- merge(subjective_adaptive2, data_study2_subj, by = 'user_id')
subjective_adaptive2 <- subjective_adaptive2[order(sum_triggered)]
median_val <- subjective_adaptive2[nrow(subjective_adaptive2)/2,]$sum_triggered
subjective_adaptive2$sum_triggered_median <- ""
subjective_adaptive2[sum_triggered <= median_val]$sum_triggered_median <- "Low_Triggers"
subjective_adaptive2[sum_triggered > median_val]$sum_triggered_median <- "High_Triggers"
subjective_adaptive2$sum_triggered_median <- as.factor(subjective_adaptive2$sum_triggered_median)

a1 <- kruskal.test(userful ~ sum_triggered_median, data = subjective_adaptive2)
b1 <- kruskal.test(distracting ~ sum_triggered_median, data = subjective_adaptive2)
c1 <- kruskal.test(confusing ~ sum_triggered_median, data = subjective_adaptive2)
d1 <- kruskal.test(right_timing ~ sum_triggered_median, data = subjective_adaptive2)
useful_ <- a1$p.value
distracting_ <- b1$p.value
confusing_ <- c1$p.value
right_timing_ <- d1$p.value

sss <- summarySE(subjective_adaptive2, measurevar="distracting", groupvars=c("sum_triggered_median"))

# https://www.psychometrica.de/effect_size.html#cohenb
# https://www.psychometrica.de/effect_size.html#transform
#confusion: Cohen's d = 0.737, converted to r = 0.346
#distracting: Cohen's d = 0.808, converted to r = 0.375


#interaction effect: treatment and vislit on accuracy:
#main effect number of triggers on time:

#sss <- summarySE(data_study_combined[BarChartLit_median == 'Low'], measurevar="mmd_task_time", groupvars=c("mmd_id","treatment"))
#ggplot(sss, aes(x = mmd_id, y = mmd_task_time)) +
# geom_bar(aes(fill = treatment), position = "dodge", stat = "identity") +
# geom_errorbar(aes(ymin=mmd_task_time-ci*0.95, ymax=mmd_task_time+ci*0.95, color=treatment), width=.1, position=position_dodge(0.9))
