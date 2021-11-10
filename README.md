## EMTF BDT Performance Plotter
=======
## EMTF BDT Performance Plotter
>>>>>>> 52cc87b628f8b1fd3abcc39e41dc3d0cf3724b6f
This repository contains tools to evaluate the performance of the EMTF BDT after retraining.

## Setup

### For Running
```
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_10_6_1_patch2 
cd CMSSW_10_6_1_patch2/src
cmsenv

git clone git@github.com:jrotter2/EMTF_BDT_PerformancePlotter.git
cd EMTF_BDT_PerformancePlotter

pip3 install -r requirements.txt --user
```

### For Developing
You should first fork this repository.
```
source /cvmfs/cms.cern.ch/cmsset_default.sh
cmsrel CMSSW_10_6_1_patch2
cd CMSSW_10_6_1_patch2/src
cmsenv

git clone git@github.com:<your_GitHub_username>/EMTF_BDT_PerformancePlotter.git
git checkout -b <your_branch_name>
git push origin <your_branch_name>

pip3 install -r requirements.txt --user
```
After you have made changes you can push them to your branch using,
```
git add .
git commit -m "Some Message..."
git push
```
Once your changes are stable and complete they can merged via a PR to the master branch.

### Upon Logging In (Each Session)
It is recommended that you add these to your bash profile.
In order to access files from EOS you will need to setup your environment for your session using,
```
source /cvmfs/cms.cern.ch/cmsset_default.sh
voms-proxy-init --voms cms
cd ~/path/to/your/directory/CMSSW_10_6_1_patch2/src/
cmsenv
```

## Structure

The repository is structure so that one could run each individual plotter seperataly or call the general plotter to make multiple different types of performance plots.

Additionally there are helper classes in the `helpers` directory which can be used to store multiuse functions or useful calculations.

### General Plotter
`plotter.py` is responsible for making general plots.

### Efficiency Plotter
`efficiencyPlotter.py` is responsible for making efficiency plots. It can be called directly by:
```
python3 efficiencyPlotter.py <options> outputDir inputFile
```
To see a full list of options you can execute `python3 efficiencyPlotter.py --help`

This plotter will generate efficiency vs pT and efficiency vs eta plots for multiple selections passed through `<options>`.

### Occupancy Plotter
`occupancyPlotter.py` is responsible for making occupancy plots.

### Resolution Plotter
`resolutionPlotter.py` is responsible for making resolution plots, which are probability distributions for missing pT for a certain number of events (i.e. how precisely the trigger is estimating muon pT). The resolution plotter gives more information on how to scale the efficiency plots for a turn-on rate efficiency of =>90%. It can be called directly by:
```
python3 resolutionPlotter.py <options> outputDir inputFile
```
This plotter will generate resolutions using a Gaussian distribution.

### Helpers
Stored in the `helpers` directory, are used to store multiuse functions or useful calculations.

