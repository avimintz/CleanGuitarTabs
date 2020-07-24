import os
import re
import sys
from time import ctime
from argparse import ArgumentParser
from collections import defaultdict

def directory_file_map(files, current_dir):
    types_pattern = '(' + '|'.join(types) + ')'
    pattern = re.compile(r'.*?(\s*\([0-9]\)\s*)\.' + types_pattern,re.IGNORECASE) # r-string so that we dont confuse \s with \\s
    file_ext_pattern = re.compile(fr'.*(\.{types_pattern})$',re.IGNORECASE)

    band = ""
    dir_files = defaultdict(lambda:[])
    for file in files:
        # find a way to do with pattern matching
        file_short_name = file
        band = current_dir.split('\\')[-1]
        band_prefix = band.lower() + ' - '
        if file_short_name.lower().startswith(band_prefix):
            file_short_name = file_short_name[len(band_prefix):]
        file_short_name = file_short_name.replace(band + ' - ','')
        file_short_name = file_short_name.replace('_','') #clean it up
        match_result = pattern.findall(file_short_name)
        if match_result:
            file_short_name = file_short_name.replace(match_result[0][0],'')
        match_result = file_ext_pattern.findall(file_short_name)
        assert match_result, f'check {current_dir} {file_short_name}'
        file_short_name = file_short_name.replace(match_result[0][0],'')
        
        # fix case if different
        if file_short_name.lower() in (x.lower() for x in dir_files.keys()):
            file_short_name = list(dir_files.keys())[[x.lower() for x in dir_files.keys()].index(file_short_name.lower())]
            
        dir_files[file_short_name].append(file)
    
    return band,dir_files

def clean_subdir(current_dir, files, types, test_mode):
    band, dir_files = directory_file_map(files, current_dir)
    
    printed_directory = False
    for short_name, files in dir_files.items():
        candidates = None
        for file_type in types:
            candidates = [x for x in files if x.lower().endswith('.' + file_type)]
            if candidates:
                break
        sorted_candidates = sorted(candidates,key=lambda x:os.stat(current_dir + '\\' + x).st_size, reverse=True)
        candidate = sorted_candidates[0]
        
        
        before = candidate
        after = short_name + '.' + candidate.split(''.')[-1].lower()
        after = after.replace(band + ' - ','')
        to_del = list(set(files) - set([candidate]))
        
        if not to_del and before == after:
            continue

        if not printed_directory:
            print(f'Directory: {current_dir}')
            printed_directory = True
        if before != after:
            print(f'move: {before} -> {after}')
        if to_del:
            print(f'delete: {to_del}')
        if not test_mode:
            for file_to_del in to_del:
                os.remove(current_dir + '\\' + file_to_del)
            if before != after:
                os.rename(current_dir + '\\' + before,current_dir + '\\' + after)   
    return

def main(base_dir, types, test_mode):

    print(f'{ctime()} Starting')
    for current_dir,sub_dirs,files in os.walk(base_dir):
        if sub_dirs:
            continue
        clean_subdir(current_dir, files, types, test_mode)
    print( f'{ctime()} Done')

types = [ 'gp5','gp4','gp3','gtp','gp','ptb','txt' ]

def get_args():
    parser = ArgumentParser(description='Clean up Guitar Tabs directory')
    parser.add_argument('folder', type=str, nargs='?', help='folder to scan')
    parser.add_argument('--run', action='store_const',const=True, default=False, help='run [this will rename/delete files')
    args = parser.parse_args()
    
    if not args.folder:
        from tkinter.filedialog import askdirectory
        args.folder = askdirectory()
    assert os.path.isdir(args.folder)
    return args

args = get_args()
base_dir = args.folder
test_mode = not args.run
main(base_dir, types, test_mode)

# to do:
# use os.path functions