df <- read.csv("~/Desktop/Packet Analysis/inter_arrival1.csv", header=FALSE)
library("fitdistrplus")
plotdist(df$V1, histo=TRUE, demp=TRUE)
plot(df$V1)
descdist(df$V1)
par(mfrow=c(2,2))
fe <- fitdist(df$V1, "exp")
fe
denscomp(list(fe), legendtext=c("exp"))
cdfcomp(list(fe), legendtext=c("exp"))
qqcomp(list(fe), legendtext=c("exp"))