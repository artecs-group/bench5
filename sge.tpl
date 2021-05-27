#!/bin/bash
#$ -q queue.q
#$ -V
#$ -wd [EXEDIR]
#$ -N [JOBNAME]
#$ -o [LOGPATH]
#$ -e [LOGPATH]
#$ -m e
#$ -M mail@example.com
#$ -R y
[COMMAND]
