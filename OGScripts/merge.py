import os
import fnmatch
import argparse
import csv
from LabtoCM import labToCM

def custom_sort_key(file_name):
    order = {}
    for char in 'spdfg':
        order[char] = file_name.find(char) if char in file_name else float('inf')
    return [order[char] for char in 'spdfg']

def sort_lists(list1, list2):
    return [x for _, x in sorted(zip(list2, list1))]


def get_fresco_files(dir, search_string):
    os.chdir(f'{dir}/fresco_output_files/')
    fresco_folder_path = os.getcwd()
    totalFiles = sorted(os.listdir(fresco_folder_path))

    matching_files = []
    for file in totalFiles:
        if file.endswith('.sorted'):
            if fnmatch.fnmatch(file, f'*{search_string}*'):
                matching_files.append(file)
        else:
            continue
    # print(matching_files)
    configs = []
    for file in matching_files:
        tempconf = file.split('_')[2]
        configs.append(tempconf)
    sorted_files = sorted(configs, key=custom_sort_key) # make sure that the lowest transfer config is listed 1st, for creating the .inp file that is created
    sorted_list1 = sort_lists(matching_files, sorted_files)
    # print(sorted_list1)
    return sorted_list1, fresco_folder_path

def get_cross_section(dir, search_string):
    os.chdir(f'{dir}/angular_dist_folder/')
    ang_dist_folder = os.getcwd()
    totalFiles = sorted(os.listdir(ang_dist_folder))
    
    for file in totalFiles:
        if str(search_string) in file:
            return file, ang_dist_folder

def write_to_file(dir, cross_sec_path, fresco_path, cross_section_file, fresco_files):
    os.chdir(f'{dir}/minimizing_folder/')
    minimizing_folder = os.getcwd()
    #CM_angles = [11.30, 22.9, 28.6, 34.20, 39.9, 45.4, 51.0, 56.5]
    with open(f'{cross_sec_path}/{cross_section_file}', 'r') as f:
        stripped = [s.strip() for s in f]
        lab_angles = []
        cross_sec = []
        finalError = []
        for line in stripped:
            angle, x_sec, err = line.split()
            lab_angles.append(float(angle))
            cross_sec.append(x_sec)
            finalError.append(err)
    print('Lab Angles: ', lab_angles)
    int_angles = [int(x) for x in lab_angles]
    cm_angles = labToCM(int_angles)
    print("Calculated Center of Mass angles: ",cm_angles)
    
    fresco_list = []
    for file in fresco_files:
        with open(f'{fresco_path}/{file}', 'r') as f:
            stripped = [s.strip() for s in f]
            fresco_temp = []
            for line in stripped:
                angle, fresco_val = line.split()
                useCMAngles = True  # --> set this to false to use lab angles in outputs, also change line below to lab_angles
                if float(angle) in cm_angles:  # --> this line can be changed for CM or lab angle fresco values
                    fresco_temp.append(fresco_val)
            fresco_list.append(fresco_temp)

    if len(fresco_list) == 1: # checking to see if mixed l-transfer 
        name = fresco_files[0].split('.')[0]
        outputfile = f'{name}.inp'
        storefile = os.path.join(minimizing_folder, outputfile)

        if useCMAngles: # case where we use the CM angles in the output file
            with open(storefile, 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(zip(cm_angles, cross_sec, finalError, fresco_list[0]))
        else:
            with open(storefile, 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(zip(lab_angles, cross_sec, finalError, fresco_list[0]))

    else: # if we make it here, then we have a mixed l-transfer
        f1 = fresco_files[0].split('.')[0]
        f2 = fresco_files[1].split('.')[0]
        fname1 = f1.split('_')
        fname2 = f2.split('_')
        finalName = "_".join(fname1[:3] + fname2[2:])
        outputfile = f'{finalName}.inp'
        storefile = os.path.join(minimizing_folder, outputfile)
        if useCMAngles:
            with open(storefile, 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(zip(cm_angles, cross_sec, finalError, fresco_list[0], fresco_list[1]))
        else:
            with open(storefile, 'w') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerows(zip(lab_angles, cross_sec, finalError, fresco_list[0], fresco_list[1]))
    print(f"Succesfully written file: {outputfile}")


def parseArgs():
    parser = argparse.ArgumentParser(description="Search for files with a specific number in their names.")
    parser.add_argument("search_number", type=int, help="The number to search for in file names.")
    args = parser.parse_args()
    return args

def main():
    args = parseArgs()
    search_string = args.search_number
    dir = os.getcwd()

    fresco_files, fresco_path = get_fresco_files(dir, search_string)
    cross_section_file, cross_sec_path = get_cross_section(dir, search_string)
    write_to_file(dir, cross_sec_path, fresco_path, cross_section_file, fresco_files)


if __name__ == '__main__':
    main()

