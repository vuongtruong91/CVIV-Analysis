# CVIV-Analysis
A modification of Soumya's script, that automates the depletion calculation
This repository contains two scripts, CVIVAnalyze.py, which has not been modified from Soumya’s repository, and extract.py, which is a modified script from Soumya’s config.py.
To run the script, extract.py requires CVIVAnalyze.py to be in the same working directory, along with a folder labeled as ‘Plots’, and the files to be analyze. extract.py requires 2 arguments, a CV text file for the first argument, and an IV file for the second.
An example command to run the script is as follows;
<python extract.py CV_example.txt IV_example.txt>
The script works best for materials that don’t surpass 1e15 fluence, and is only setup for linear plots.
