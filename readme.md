# Hydrological climate change modeling using a functional flows approach
## About
This repository includes code and datasets needed to analyze and visualize streamflow attributes under a variety of climate change scenarios. Streamflow analysis is broadly split into two categories: 1) Regional analysis of 18 sites in California's western Sierra Nevada, with streamflow routed under climate change conditions from two different emissions scenarios, and 2) a decision-scaling study on the Merced River, in which different climate attributes were scaled to produce climate scenarios, which were routed to streamflow using the SAC-SMA-DS hydrologic model. All daily streamflow timeseries were first processed with the Functional Flows Calculator (https://github.com/leogoesger/func-flow). Functional flow metric datasets are included in this repository so that all post-processing and visualization can be run without first processing the raw streamflow datasets. 

## Software and setup
This project uses Python3 for functional flow metric analysis. R code is provided to modify variability of daily precipitation traces, but output from this code is provided in the repository. 

### To run climate change analyses in Python:
1. Install Python3, Git and a text editor of your choice.
2. Clone this repository from Github (recommended) or download the repository as a zipfile. 
```
git clone [Github web address here]
cd climate_change_research_public/
```
3. Activate the virtual environment

In Mac OS:
```
source my-virtualenv/bin/activate
```
In Windows: 
```
my-virtualenv\Scripts\activate
```
4. Install dependencies 
```
pip install -r requirements.txt
```
5. Run analyses with the ```main.py``` file. Either 1) regional analyses or 2) Merced river analyses can be run at a time, see instructions in the code for commenting out one or the other of these two options. 

### To run precipitation processing script in R:
R studio is recommended for running the process_precip.r script. Precipitation output files will be stored as .txt files in the 'data_outputs/detrended-one-16th-rdata' directory. 


