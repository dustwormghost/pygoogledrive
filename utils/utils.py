'''Utility class'''
import datetime
import os, sys
from zipfile import ZipFile

def log(msg):
    print '\n[%s] %s' % (datetime.datetime.now(), msg)

def list_files(dir_path):
    return os.listdir(dir_path)

def delete_files(dir_path, files=[]):
    log('Delete ' + str(len(files)) + ' files from ' + dir_path)
    for f in files:
        os.remove(''.join([dir_path, f]))
        print '*',

    log('Deleted')

def create_zip_file(from_path, o_file_name, files=[]):
    log('Zip ' + str(len(files)) + ' files from ' + from_path + ' to '  + o_file_name)
    if len(files) is 0 :
        log('Nothing to zip.')
        return False

    with ZipFile(o_file_name, 'w') as zip:
        for f in files:
            zip.write(''.join([from_path, f]))
            print '*',

    log('Zipped')
    return True