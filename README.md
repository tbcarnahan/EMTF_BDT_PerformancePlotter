# EMTF BDT Performance Plotter
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
`plotter.py` is responsible for making general plots. It can make efficiency plots and resolution plots for different selections. It can be called by,
```
python3 plotter.py <options> outputDir outputFileName inputFile
```
The options `-e`(or `--eff`) will set a flag to create efficiency plots and `-r`(or `--res`) will set a flag to create resolution plots. Additional options can be seen by running `python3 plotter.py --help`.
### Efficiency Plotter
`efficiencyPlotter.py` is responsible for making efficiency plots. It can be called directly by:
```
python3 efficiencyPlotter.py <options> outputDir outputFileName inputFile
```
To see a full list of options you can execute `python3 efficiencyPlotter.py --help`

This plotter will generate efficiency vs pT, efficiency vs eta, and efficiency vs phi plots for multiple selections passed through `<options>`. These plots will be saved to a pdf specified by `outputDir` and `outputFileName`.

### Occupancy Plotter
`occupancyPlotter.py` is responsible for making occupancy plots.

### Resolution Plotter
`resolutionPlotter.py` is responsible for making resolution plots.

### Helpers
Stored in the `helpers` directory, are used to store multiuse functions or useful calculations.

