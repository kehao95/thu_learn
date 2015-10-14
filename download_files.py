__author__ = 'kehao'
from thu_learn import *
import sys

_FILES_ROOT_PATH = 'file'
_NEW_FILES_PATH  = _FILES_ROOT_PATH+'/'+ 'new_files'

_UPDATE_FLAG = True
_MAX_FILE_SIZE = 20



def set_flag():
    if len(sys.argv) == 1:
        print("\n>> Will update files ---save new files to %s)"%_NEW_FILES_PATH)
        print(">> If you want to save all files in the course folder please give a parament: \n\t'python download_files.py init' ")
        _UPDATE_FLAG = True
    else:
        print(">> Init")
        _UPDATE_FLAG = False


def main():
    set_flag()
    login()
    semester = Semester(current=True)
    if not os.path.exists(_NEW_FILES_PATH):
        os.makedirs(_NEW_FILES_PATH)
    for course in semester.courses:
        path = _FILES_ROOT_PATH+'/' + course.name
        print(course.name)
        if not os.path.exists(path):
            os.makedirs(path)
        for file in course.files:
            if _UPDATE_FLAG is True:
                # update files
                if not (os.path.isfile(path+'/'+file.name) or os.path.isfile(_NEW_FILES_PATH+'/'+file.name)):
                    # files existing in the path will not be saved
                    print('\t',file.name,file.size)
                    if file.size < _MAX_FILE_SIZE:
                        file.save(path)
            else:
                # first time
                print('\t',file.name,file.size)
                if file.size < _MAX_FILE_SIZE:
                    file.save(_NEW_FILES_PATH)





if __name__ == '__main__':
    main()

