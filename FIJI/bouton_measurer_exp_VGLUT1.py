import os
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.plugin import ImageCalculator
from ij.measure import ResultsTable
from ij.process import FloatProcessor
import csv


'''
- take the preprossed expansion images (channel split):
	- 3 color expension experiments (C1=VGlut, C2=actin, C3=PSD95)
- convert the VGLUT channel to a mask (int treshold is used to exclude background)
- use built-in watershed function to separate overlapping rois based on circularity
- use final mask to generate ROIS
- run built-in measure function to measure rois in actin channel
- export the result as table
'''

#define the directories with the raw images for conditions and preparations
dirs=[
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/WT/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/WT/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/WT/3',
	
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/TKO/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/TKO/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/TKO/3'
	]

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
		
		#define the filename pattern for the C1=VGlut, C2=actin, C3=PSD95
		#VGlut
		VGL = [x for x in list if "C1-" in x and num_pattern in x]
		
	
		#Actin
		ACT = [x for x in list if "C2-" in x and num_pattern in x]
	
		#stop the macro if there is more than one image per channel per measurement (safety check)
		assert len(ACT) == 1 and len(VGL) == 1, num_image

		img_actin = IJ.openImage(os.path.join(dir, ACT[0]))
		img_actin.show()
		
		#converts images to masks based on intensity threshold
		#based on bild-in "Convert to Mask" function

		def find_mask(file):
			img = IJ.openImage(os.path.join(dir, file))
			IJ.setThreshold(img, 130, 2**16)
			IJ.run(img, "Convert to Mask", "")
			IJ.run(img, "Watershed", "")
			return img
		
		#get the mask for the Vglut channel
		mask = find_mask(VGL[0])

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
	output_file = os.path.join(dir, 'final_table_VGLUT1.csv')
	resultsTable.saveAs(output_file)

#close all windows reset results table
IJ.run("Close All")
IJ.run("Clear Results")
