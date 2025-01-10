import os
from ij import IJ, ImagePlus
from ij import WindowManager
from ij.plugin.frame import RoiManager
from ij.plugin import ImageCalculator
from ij.measure import ResultsTable
from ij.process import FloatProcessor
import csv


#this macro runs over all actin images of the expansion miscroscopy and measures (intensity and area) them using the build-in 
#"Measure" function, the results are saved as a .csv file

#define the directories with the raw images for conditions and preparations
dirs=[
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/WT/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/WT/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/WT/3',
	
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/TKO/1',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/TKO/2',
	'/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split/TKO/3',]

#define the output path for final .csv file
output_path = '/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Expansion data/20241120_Data_for_jakob/Channel Split'

IJ.run("Close All")
IJ.run("Clear Results")

for dir in dirs:

	#get a list of all .tif files 
	list = os.listdir(dir)
	list = [x for x in list if x.endswith(".tif")]
	indices = sorted(set([x[x.index("{")+1:x.index("}")] for x in list]))

	for num_image in indices:
		
		#define the filename pattern for the STED channel of the actin image
		num_pattern = ("{" + str(num_image) + "}")
		num_pattern = ("{" + str(num_image) + "}")
		
		#define the filename pattern for the C1=VGlut, C2=actin, C3=PSD95
		#Actin
		ACT = [x for x in list if "C2-" in x and num_pattern in x]
		#stop the makro if there is more than one image per actin image (safety check)
		assert len(ACT) == 1, num_image
	

		img_actin = IJ.openImage(os.path.join(dir, ACT[0]))
	
		#measure the overall actin image
		IJ.run("Set Measurements...", "area mean standard min integrated display redirect=None decimal=3")
		IJ.run(img_actin, "Measure", "")
		resultsTable = ResultsTable.getResultsTable()
		
		#save the resulting output for all files as table
		output_file = os.path.join(output_path + '/actin_mean_int.csv')
		resultsTable.saveAs(output_file)