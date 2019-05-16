from __future__ import division
import sys
import os
import numpy as np

def list_files(dir):
   files = []
   for obj in os.listdir(dir):
      if os.path.isfile(obj):
         files.append(obj)
   return files

#############################
#							#
#		  Globals			#
#							#
#############################
CVFileLocation = sys.argv[1]
IVFileLocation = sys.argv[2]
 
with open(CVFileLocation, "r") as cv:
 txtLines = [line for line in cv]
 idx = [i for i, line in enumerate(txtLines) if "BiasVoltage" in line][0]
 headers = txtLines[idx].split('\t')
 cv1kHz_idx = headers.index("LCR_Cp_freq1000.0")
 cv10kHz_idx = headers.index("LCR_Cp_freq10000.0")
            
 cv1kHz = []
 cv10kHz = []
 bv = []

 data = txtLines[idx+1:]
 for line in data:
     words = line.split()
     bv.append(float(words[0]))
     cv1kHz.append(1.0/(float(words[cv1kHz_idx])*float(words[cv1kHz_idx])))
     cv10kHz.append(1.0/(float(words[cv10kHz_idx])*float(words[cv10kHz_idx])))
        
Vmin = bv[0]*bv[0]    #Polarity is set to positive to be compatible with CVIVanalyze
Vmax = bv[-1]*bv[0]

for j in bv, cv1kHz:
  delta = [cv1kHz[i+1]-cv1kHz[i] for i in range(len(cv1kHz)-1)] 
  Range = [bv[i+1]-bv[i] for i in range(len(bv)-1)]
  RangeNorm = [i*(cv1kHz[-1]) for i in Range]

  m = [x/y for x,y in zip(delta, RangeNorm)] #m is define as normalized SLOPE

  mMag =  map(abs, m)     #converting all data to positive to set the depletion range
  mMag.insert(0, mMag[0]) #making all arrays the same length

  if bv[1] < 1:
    Deplete = [i for i,j in zip(bv, mMag) if ((j < 0.0005) and (i < -100.0))] #range of mimimum change
  else:
    Deplete = [i for i,j in zip(bv, mMag) if ((j < 0.0005) and (i > 100.0))] #range of mimimum change

  print "Depletion Volatges Array", Deplete
  if len(Deplete) == 0: #Creating an artificial depleteion array with last couple of values
    Deplete.append(bv[-4])
    Deplete.append(bv[-3])
    Deplete.append(bv[-2])
    Deplete.append(bv[-1])
    print "******************************************************************"
    print "************************* NO DEPLETION ***************************"
    print "******************************************************************"
  else:
    print "******************************************************************"
    print "*********************** Depletion Exist *************************"
    print "******************************************************************"

  if (bv[10] > 0):               #calculating the absolutine minimum point and neighbor points
    mfilter = [j for i,j in zip(bv, m) if  (i > 100.0)] #array to find the extrema far from start point
    PosBias = max(mfilter)             #to find the range before depletion in the normalized derivatice
    Rampup = []
    for i in xrange(len(m)):
      if m[i] == PosBias:
        Rampup.append(float(bv[i]))
        Rampup.append(float(bv[i-3]))
        Rampup.append(float(bv[i-5]))
  else:
    mfilter = [j for i,j in zip(bv, m) if  (i < -100.0)] #array to find the extrema far from start point
    NegBias = min(mfilter)
    Rampup = [] 
    for i in xrange(len(m)):
      if m[i] == NegBias:
        Rampup.append(float(bv[i]))
        Rampup.append(float(bv[i-3]))
        Rampup.append(float(bv[i-5]))

slopef1min = Rampup[2]*bv[0]       #If Error due to Out of Range, must
slopef1max = Rampup[0]*bv[0]       #manually put in voltage values here!
flatf1min = Deplete[0]*bv[0]
#flatf1min = -960.0

if Deplete[0] > 0:                          #setting the range of depletion, and 
  if ((Deplete[0]+150.0) <= bv[-1]):         #making sure it doesn't surpass the 
    flatf1max = (Deplete[0] + 150.0)*bv[0]  #maximum bias voltage
  else:
    flatf1max = Deplete[-1]*bv[0]
else:
  if ((Deplete[0]-150.0) >= bv[-1]): 
    flatf1max = (Deplete[0] - 150.0)*bv[0]
  else:
    flatf1max = Deplete[-1]*bv[0]


slopef2min = slopef1min
slopef2max = slopef1max
flatf2min = flatf1min
flatf2max = flatf1max

print "*************************************************"
print "****************** DATA POINTS ******************"
print "*************************************************"
print "slopef1min: ", slopef1min, "slopef1max: ", slopef1max, "flatf1min: ", flatf1min, "flatf1max: ", flatf1max
print "slopef2min: ", slopef2min, "slopef2max: ", slopef2max, "flatf2min: ", flatf2min, "flatf2max: ", flatf2max

if bv[1] > 0:
  Bulk = 0
else: Bulk = 1


#!/usr/bin/python

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""     CONFIGURATION PARAMETERS    """"""""""""""""""""""""
""""""""""""""""""""""""          VERSION : 3.17         """"""""""""""""""""""""
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

PlotSavingLocation = "./Plots/" %locals()

d = 240.0 * 1e-6 # thickness of sensor in SI measured before irradiation (if non-irradiated, it will be extracted from measurement via end capacitance)
A = 37.4 * 1e-3 # active area of sensor in SI
Irradiation = 1 # 1 for irradiated samples, 0 for non-irradiated samples
SensorType = Bulk #1 # 1 for P-type, 0 for N-type
ScaleTemp = 20.0 # Current scaling temperature
FlatFittingMethod1 = 1 # 0 for y=ax+b and 1 for y=b (forced to be horizontal line) ## for log-log scaled plot
FlatFittingMethod2 = 0 # 0 for y=ax+b and 1 for y=b (forced to be horizontal line) ## for 1/C^2 plot
CapManualf1 = -12.85E-12 # F (>0 if manual capacitance is wanted for flat fit and <0 if manual capacitance is not wanted)
CapManualf1Err = 10E-15 # F
CapManualf2 = -1.61E-11 # F (>0 if manual capacitance is wanted for flat fit and <0 if manual capacitance is not wanted)
CapManualf2Err = 10E-15 # F


"""If different ranges are wanted for log-log and 1/C^2 fittings, use following
parameters in addition to the parameters above (in this case, above parameters
set the ranges for log-log scaled fittings). If the same ranges are wanted for
both log-log and 1/C^2 fittings, then set slopef1min_1C < 0 and use the above
parameters to set the fitting ranges!"""

slopef1min_1C = slopef1min
slopef1max_1C = slopef1max
flatf1min_1C = flatf1min
flatf1max_1C = flatf1max

slopef2min_1C = slopef2min
slopef2max_1C = slopef2max
flatf2min_1C = flatf2min
flatf2max_1C = flatf2max

CapMode = 0 # 0 for parallel mode, 1 for serial mode
CapOffset = 0 # Capacitance offset if any
VdepCoeff = 1.2 # Vdep coefficient for extraction of leakage current and capacitance above full-depletion (for HPK, it is 1.2)
PlotDopingProfile = 0 # 0 if plot not wanted, 1 if plot wanted
PlotDoubleDerivative = 0 # 0 if plot not wanted, 1 if plot wanted
SavePopUpPlots = 1 # 0 if pop-up plots not wanted to be saved, 1 if wanted
LCRAccuracy = 0.05 # %
OpenMeasError = 3e-14 # F
CurrentAccuracy = 0.1 # %

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Sensor          Thickness[um]  Active Area[mm2]  Capacitance[pF]
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CA0126              284.7           25.0              9.252
CA0127              285.8           25.0              9.216
CA0133              255.4           25.0              10.315

CD1731              282.4           25.0              9.328
CD1737              280.2           25.0              9.400
CD1738              289.8           25.0              9.091

8556-02-37-3        300.0           6.25              2.880
8556-02-37-4        300.0           6.25              2.877
8556-02-39-1        300.0           6.25              2.876
8556-02-39-2        300.0           6.25              2.877

261636-10-23-1      155.1           6.25              4.246
261636-10-23-3      154.2           6.25              4.270
261636-10-23-4      155.4           6.25              4.238
261636-10-29-1      153.6           6.25              4.287

6336-03-41          49.11           25.0              53.642
6336-03-42          49.51           25.0              53.209
6336-03-43          49.85           25.0              52.836
6336-03-44          51.03           25.0              51.616

MCZ200Y_06_DiodeL_5 200.0           25.0
FTH200Y_04_DiodeL_9 200.0           25.0
MCZ200N_06_DiodeL_9 200.0           25.0
FTH200N_25_DiodeL_8 200.0           25.0
MCZ200Y_04_DiodeL_3 200.0           25.0
FTH200Y_03_DiodeL_9 200.0           25.0
MCZ200N_11_DiodeL_9 200.0           25.0
FTH200N_25_DiodeL_3 200.0           25.0
MCZ200Y_07_DiodeL_9 200.0           25.0
FTH200Y_04_DiodeL_8 200.0           25.0
MCZ200N_09_DiodeL_8 200.0           25.0
FTH200N_25_DiodeL_2 200.0           25.0
MCZ200Y_05_DiodeL_2 200.0           25.0
FTH200Y_04_DiodeL_3 200.0           25.0
MCZ200N_11_DiodeL_8 200.0           25.0
FTH200N_24_DiodeL_8 200.0           25.0
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

from CVIVAnalyze import *

ConfigurationParameters(CVFileLocation, IVFileLocation, PlotSavingLocation, d, A, Irradiation, SensorType, ScaleTemp, FlatFittingMethod1, FlatFittingMethod2, CapManualf1, CapManualf1Err, CapManualf2, CapManualf2Err, slopef1min, slopef1max, flatf1min, flatf1max, slopef2min, slopef2max, flatf2min, flatf2max, slopef1min_1C, slopef1max_1C, flatf1min_1C, flatf1max_1C, slopef2min_1C, slopef2max_1C, flatf2min_1C, flatf2max_1C, Vmin, Vmax, CapMode, CapOffset, VdepCoeff, PlotDopingProfile, PlotDoubleDerivative, SavePopUpPlots, LCRAccuracy,OpenMeasError, CurrentAccuracy)


