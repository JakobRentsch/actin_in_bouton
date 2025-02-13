import os
import numpy as np
import re
import matplotlib.pyplot as plt

'''
-this script runs over the directories of the raw data for all conditions and preparations to find the final_table.csv
 containing the measurement outputs (FIJI macros: bouton_measurer.py and full_image_actin_measurer.py) of all rois
 and the whole actin images 
-this script normalizes the max intensity per roi of actin by the max intensity of the whole actin image
-the results a further summarized to generate median (median is chosen because data are not normal) normalized max
intensity per image and median max intensity per preparation
-the saved .csv files contain indentifiers columns for each condition (WT = 1, TKO = 2, FL-Rescue = 3, IDR-Rescue = 4)
and preparation number and image number
-the results are saved as .csv files as follows:
WT_all_rois --> data based on rois (as defined by bouton_measurer.py FIJI macro) for the WT conditons
..._ims --> rois are summarized by calculating medians per image
..._ims --> rois are summarized by calculating medians per preparation
all_conditions_norm_max_int_rois --> normalized max intensity based on rois (as defined by bouton_measurer.py FIJI macro)
                                summarized for all conditions
all_conditions_area_nm^2 --> area of rois in nm^2 (as defined by bouton_measurer.py FIJI macro)
                            summarized for all conditions                  
-script also generated quick boxplot to visualize output, these are not saved
'''

input_directory = '/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Data'
output_directory = '/Users/jakobrentsch/FU Box/Papers/Dual color sted of actin and syp/Analysis/Source data'
conditions = ['WT', 'TKO', 'FL-Rescue', 'IDR-Rescue']

#takes the .csv files that are the output of the FIJI macro for each measurement and adds it to 1 .csv file
def csv_files_summarizer(directoy, condition):
    csv_files = []

    # Walk through directory and its subdirectories
    for root, dirs, files in os.walk(input_directory):
        for file in files:

            if file.endswith("final_table.csv") and condition in root:
                # Append full file path to the list
                csv_files.append(os.path.join(root, file))


    all_csv_list = []

    full_image_csv = np.loadtxt(input_directory + '/actin_mean_int.csv',
                                  delimiter=',', skiprows=1, usecols=(2,3,4,5,6,7,8))
    full_image_names = np.loadtxt(input_directory + '/actin_mean_int.csv',
                                  delimiter=',', skiprows=1, usecols=1, dtype = 'str')

    for csv_file in csv_files:

        # Extract the identifier (for each preparation) from the filename
        identifier = csv_file[-17]

        # Load the CSV file
        temp_csv_values = np.loadtxt(csv_file, delimiter=',', skiprows=1, usecols=(2,3,4,5,6,7,8))
        im_names = np.loadtxt(csv_file, delimiter=',', skiprows=1, usecols=1, dtype = 'str')

        im_ids = []
        list_full_image_max = []
        
        #extrac the maximum int of all images from different .csv files
        for im_name in im_names:

            n=0
            for full_image_name in full_image_names:

                if im_name[0:im_name.find(':')] == full_image_name:

                    #extract the maximum intensity of the actin image
                    temp_image_max_int = full_image_csv[n, 4]
                    list_full_image_max.append(temp_image_max_int)

                n += 1

            str_search = re.search('{(.*)}', im_name)
            im_id = int(str_search.group(1))
            im_ids.append(im_id)

        temp_csv = np.concatenate((np.zeros([temp_csv_values.shape[0], 5]), temp_csv_values), axis=1)

        # swap the roi area column with the mean intensity columnm, this makes handling the columns easier later
        temp_csv[:, [5, 6]] = temp_csv[:, [6, 5]]

        #add columns that identify each preparation and image
        temp_csv[:, 1] = np.full((temp_csv.shape[0]), identifier)
        temp_csv[:, 2] = im_ids
        temp_csv[:, 3] = list_full_image_max

        #add column for the normalized intensity
        temp_csv[:, 4] = temp_csv[:, 9] / temp_csv[:, 3] #normalize the max bouton int to the max of the overall image

        # add column that identifies each condition
        if condition == 'WT':
            temp_csv[:, 0] = np.full((temp_csv.shape[0]), 1)

        if condition == 'TKO':
            temp_csv[:, 0] = np.full((temp_csv.shape[0]), 2)

        if condition == 'FL-Rescue':
            temp_csv[:, 0] = np.full((temp_csv.shape[0]), 3)

        if condition == 'IDR-Rescue':
            temp_csv[:, 0] = np.full((temp_csv.shape[0]), 4)

        # Append the concatenated result to all_rois
        all_csv_list.append(temp_csv)

    all_rois = np.concatenate(all_csv_list)

    header_rois = ['condi', 'rep', 'image', 'image_int_max', 'roi_int_max_norm','roi_mean_int','roi_area',
                   'roi_StdDev_int', 'roi_int_min','roi_int_max', 'roi_int_Den', 'roi_RawIntDen' ]

    all_rois_header = np.vstack((header_rois, all_rois))

    #mean per im
    all_ims = []
    all_reps = []

    for rep_id in np.unique(all_rois[:, 1]):

        rois_rep = all_rois[all_rois[:, 1] == rep_id, :]
        temp_line = np.concatenate((rois_rep[0, 0:3], [np.median(rois_rep[:, 3])],[np.median(rois_rep[:, 4])]))
        all_reps.append(temp_line)

        for im_id in np.unique(rois_rep[:, 2]):

            temp_im = rois_rep[rois_rep[:, 2] == im_id, :]
            temp_line = np.concatenate((temp_im[0, 0:4],  [np.median(temp_im[:, 4])]))
            all_ims.append(temp_line)

    header_ims = ['condi', 'rep', 'image', 'image_int_max', 'median_image_int_max_norm']
    all_ims_header = np.vstack((header_ims, all_ims))

    header_reps = ['condi', 'rep', 'image', 'rep_median_int_max', 'median_image_int_max_norm']
    all_reps_header = np.vstack((header_reps, all_reps))

    np.savetxt(output_directory + '/' + condition + '_all_rois.csv', all_rois_header, fmt='%s', delimiter=',')
    np.savetxt(output_directory + '/' + condition + '_all_ims.csv', all_ims_header, fmt='%s', delimiter=',')
    np.savetxt(output_directory + '/' + condition + '_all_reps.csv', all_reps_header, fmt='%s', delimiter=',')

    return np.array(all_rois), np.array(all_ims), np.array(all_reps)

'''
- runs the csv_file_summarizer function over all conditions to get the intensity values of all datapoints and normalize to
the max intensity of the image / rep 
k specifies the level of analysis (rois as datapoints k=0, ims as datapoints k=1, reps as datapoints k=2 )
'''
def int_getter(var_conditions, k):
    max_len = 0

    for condition in var_conditions:

        temp_len = csv_files_summarizer(input_directory, condition)[k].shape[0]

        if temp_len > max_len:
            max_len = temp_len

    array_norm = np.zeros([max_len, len(conditions)])

    n = 0
    for condition in conditions:
        temp_array = csv_files_summarizer(input_directory, condition)[k]
        temp_array_norm = temp_array[:,4]
        padded_temp_array_norm = np.pad(temp_array_norm, (0, max_len - temp_array.shape[0]), constant_values=np.nan)
        array_norm[:,n] = padded_temp_array_norm
        n += 1

    return array_norm

all_condis_rois = int_getter(conditions, 0)
all_condis_ims = int_getter(conditions, 1)
all_condis_reps = int_getter(conditions, 2)

all_condis_rois_header = np.vstack((conditions, all_condis_rois))
all_condis_ims_header = np.vstack((conditions, all_condis_ims))
all_condis_reps_header = np.vstack((conditions, all_condis_reps))

np.savetxt(output_directory + '/all_conditions_norm_max_int_rois.csv', all_condis_rois_header, fmt='%s', delimiter=',')
np.savetxt(output_directory + '/all_conditions_norm_max_int_ims.csv', all_condis_ims_header, fmt='%s', delimiter=',')
np.savetxt(output_directory + '/all_conditions_norm_max_int_reps.csv', all_condis_reps_header, fmt='%s', delimiter=',')

#gets area of all boutons in um^2
def area_getter(var_conditions):
    max_len = 0

    for condition in var_conditions:

        temp_len = csv_files_summarizer(input_directory, condition)[0].shape[0]

        if temp_len > max_len:
            max_len = temp_len

    array_norm = np.zeros([max_len, len(conditions)])

    n = 0
    for condition in conditions:
        temp_array = csv_files_summarizer(input_directory, condition)[0]
        temp_array_norm = temp_array[:, 6]
        padded_temp_array_norm = np.pad(temp_array_norm, (0, max_len - temp_array.shape[0]), constant_values=np.nan)
        array_norm[:, n] = padded_temp_array_norm
        n += 1

    return array_norm

all_condis_rois_area = area_getter(conditions)
all_condis_rois_area_header = np.vstack((conditions, all_condis_rois_area))
np.savetxt(output_directory + '/all_conditions_area_um^2_rois.csv', all_condis_rois_area_header, fmt='%s', delimiter=',')

def boxplotter(array, figure_n, figure_title, ylabel):

    plt.figure(figure_n)
    plt.boxplot([array[~np.isnan(array[:,0]),0],
                array[~np.isnan(array[:,1]),1],
                array[~np.isnan(array[:,2]),2],
                array[~np.isnan(array[:,3]),3]],
                tick_labels = conditions, showmeans=True, showfliers=False)
    plt.title(figure_title)
    plt.ylabel(ylabel)

    # Overlay data points as scatter
    for i in range(array.shape[1]):
        data = array[~np.isnan(array[:, i]), i]
        x = np.random.normal(i + 1, 0.04, size=len(data))  # jitter for better visibility
        plt.scatter(x, data, alpha=0.5, s=5, color='black', marker = '.')  # Adjust `s` for point size

    plt.xticks(range(1, len(conditions) + 1), conditions)
    plt.title(figure_title)
    plt.ylabel(ylabel)

#generate boxplots for all conditions for normalized max int and area (are not saved)
boxplotter(all_condis_rois, 1, 'Boutons as data points', 'normalized max bouton intensity (a.u.)')
boxplotter(all_condis_ims, 2, 'Images as data points', 'normalized max bouton intensity (a.u.)')
boxplotter(all_condis_reps, 3, 'Preparations as data points', 'normalized max bouton intensity (a.u.)')
boxplotter(all_condis_rois_area, 4, 'Bouton Area', 'Area in nm^2')

plt.show()