import xml.etree.ElementTree as ET
import os
import pandas as pd
import read_diff


def get_root():
    tree = ET.parse("Query.xml")
    root = tree.getroot()
    location = root.find('driver_location')
    return location.text

def get_filter():
    tree = ET.parse("Query.xml")
    root = tree.getroot()
    filter = root.find('complexity_filter')
    return int(filter.text)

def get_complexity_with_SM(path, files, methods):
    with open('config.xml', 'r') as fopen:
        lines = fopen.readlines()
    for i in range(len(lines)):
        if lines[i].find('source_directory') >= 0:
            lines[i] = ('        <source_directory>' + path + '</source_directory>\n')
    with open('config.xml', 'w') as fopen:
        fopen.writelines(lines)
    os.system('test.bat')
    csv_file = pd.read_csv('methods_detail.csv')
    complexity = []
    for i in range(len(files)):
        find = False
        for index, row in csv_file.iterrows():
            if files[i] == row['File Name'] and methods[i] == row['Method']:
                complexity.append(row['Complexity'])
                find = True
                break
        if not find:
            complexity.append('')
    return complexity
        

def get_function_complexity(root, input_file = 'Func_changed.txt', output_file = 'output.csv'):
    filter = get_filter()
    with open(input_file, 'r') as fopen:
        lines = fopen.readlines()
    #commit_version = lines[0].strip()
    #os.system('git reset --hard ' + version)
    #del lines[0]
    current_folder = ''
    files = []
    methods = []
    output_lines = ['File Name,Methods,Complexity\n']
    for line in lines:
        line = line.strip().split(',')
        file_full_path, method = line[0], line[-1]
        folder = file_full_path[:file_full_path.rfind('\\') + 1]
        file = file_full_path[file_full_path.rfind('\\') + 1:]
        if folder != current_folder and current_folder:
            complexity = get_complexity_with_SM(root + current_folder, files, methods)
            for i in range(len(files)):
                files[i] = os.path.join(current_folder, files[i])
                output_lines.append(files[i] + ',' + methods[i] + ',' + str(complexity[i]) + '\n')
            files = []
            methods = []
            current_folder = folder
            print('Finishing analysing files in folder ' + current_folder)
        else:
            current_folder = folder
            files.append(file)
            methods.append(method)
    if current_folder:
        complexity = get_complexity_with_SM(os.path.join(root, current_folder), files, methods)

    for i in range(len(files)):
        if complixity[i] < filter:
            continue
        files[i] = os.path.join(current_folder, files[i])
        output_lines.append(files[i] + ',' + methods[i] + ',' + str(complexity[i]) + '\n')
    print('Finishing analysing files in folder ' + current_folder)
    with open(output_file, 'w') as fopen:
        fopen.writelines(output_lines)
    print('Generate ' + output_file + ' success!')
                
root = get_root()
read_diff.test(input_driver_path = root)
get_function_complexity(root)