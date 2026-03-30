import csv
import os
import os.path
import argparse
import pathlib


def getoutput(file, fname, path):
    angles = []
    cross_sections = []
    with open(file, 'r') as f:
        stripped = [s.strip() for s in f]
        start_line = '@s1'
        end_line = 'END'
        end_count = 0
        lines_after_start = 0
        between_lines = False
        for line in stripped:
            if start_line in line:
                between_lines = True
                lines_after_start = 2
            elif line == end_line:
                if end_count == 0:
                    end_count +=1
                else:
                    between_lines = False
                    break
            
            if between_lines and lines_after_start > 0:
                lines_after_start -=1
            elif between_lines:
                ang, x_sec = line.split()
                angles.append(ang)
                cross_sections.append(x_sec)
        
    
    storefile = os.path.join(path, f'{fname}.sorted')
    with open(storefile, 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(zip(angles, cross_sections))
    print(f'Successfully written file {fname}.sorted!')

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("fresco", type=pathlib.Path, help="give name of fresco output file to extract cross-section info")
    args = parser.parse_args()
    return args

def main():
    '''
    Script that takes a FRESCO output file and scraps the the full DWBA angular distribution, currently skips elastic data.
    '''
    dir = os.getcwd()
    args = parseArgs()
    file = dir + '/' + str(args.fresco)
    path_name, ext = os.path.splitext(file)
    fname = path_name.split('/')[-1]
    getoutput(file, str(fname), dir)


if __name__ == '__main__':
    main()