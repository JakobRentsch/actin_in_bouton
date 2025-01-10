import os
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.plugin import ImageCalculator
from ij.measure import ResultsTable
from ij.process import FloatProcessor
import csv

'''
- take the raw images of the STED experiments:
	- 2 color STED experiments (SYP in red, actin in far-red)
	- for rescue also confocal channel for GFP
- convert the SYP to a mask
- for the rescuses also make a mask from GFP channel, then create common mask of SYP mask and GFP mask
- use final mask to generate ROIS
- run built-in measure function to measure rois in actin STED channel
- export the result as table
'''

#define the directories with the raw imagages for conditions and preparations
dirs=[
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/WT/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/WT/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/WT/3',
	
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/TKO/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/TKO/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/TKO/3',
	
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/FL-Rescue/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/FL-Rescue/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/FL-Rescue/3',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/FL-Rescue/4',
	
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/IDR-Rescue/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/IDR-Rescue/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data/IDR-Rescue/3']


for dir in dirs:
	
	#close all windows reset results table
	IJ.run("Close All")
	IJ.run("Clear Results")
    
    #get a list of all .tif files 
	list = os.listdir(dir)
	list = [x for x in list if x.endswith(".tif")]
	indices = sorted(set([x[x.index("{")+1:x.index("}")] for x in list]))
	final_table = {}
	
	#iterate over all images per experiment
	for num_image in indices:

		#clear all ROIs
		roiManager = RoiManager.getInstance()
		if roiManager is not None:
			roiManager.reset()

		num_pattern = ("{" + str(num_image) + "}")
		
		#define the filename pattern for the GFP, STED channels
		GFP = None
		if "Rescue" in dir:
			GFP = [x for x in list if "eGFP" in x and num_pattern in x]
	
		SV_patterns = ["STAR 580_STED", "STAR ORANGE STED"]
		SV = [x for x in list if any(p in x for p in SV_patterns) and num_pattern in x]
	
		RED_patterns = ["STAR 635_STED", "STAR 635P_STED", "STAR RED_STED", "STAR RED STED"]
		RED = [x for x in list if any(p in x for p in RED_patterns) and num_pattern in x]
	
		#stop the makro if there is more than one image per channel per measurement (safety check)
		assert len(RED) == 1 and len(SV) == 1, num_image

		img_actin = IJ.openImage(os.path.join(dir, RED[0]))
		img_actin.show()
		
		#converts images to masks based on intensity threshold
		#based on bild-in "Convert to Mask" function
		#funtion can also add blur if needed
		def find_mask(file,blur):
			img = IJ.openImage(os.path.join(dir, file))
			IJ.setAutoThreshold(img, "Default")
			IJ.run(img, "Gaussian Blur...", "sigma=" + str(blur) + " scaled")
			IJ.run(img, "Convert to Mask", "")
			return img
		
		#get the mask for the SV channel
		mask_sv = find_mask(SV[0], 0)
		
		#if there is a GFP image (Rescues) also generate a mask for the GFP channel 
		#and there find a common mask between GFP and SV channels
		if GFP:
			mask_gfp = find_mask(GFP[0], 0)
			ic = ImageCalculator()
			mask = ic.run("AND create", mask_gfp, mask_sv)
		else:
			mask = mask_sv

		mask.show()
		
		#converts the mask into rois
		#based on bild-in "Analyze Particles" function
		options = "size=10-Infinity pixel show=Overlay include add composite"
		IJ.run(mask, "Analyze Particles...", options)
		
		#check if there are rois generated in previous step
		roiManager = RoiManager.getInstance()
		if roiManager is None or roiManager.getCount() == 0:
			continue
		roiManager.setSelectedIndexes(range(roiManager.getCount()))

		img_actin.show()
		WindowManager.setTempCurrentImage(img_actin)
		
		#measure the generated rois in actin image
		IJ.run("Set Measurements...", "area mean standard min integrated display redirect=None decimal=3")
		roiManager.runCommand("Measure")
		resultsTable = ResultsTable.getResultsTable()
		resultsTable.show("Results")
	
	#save the results per measurement as table
	output_file = os.path.join(dir, 'final_table.csv')
	resultsTable.saveAs(output_file)

#close all windows reset results table
IJ.run("Close All")
IJ.run("Clear Results")
