__author__ = 'kehao'
from thu_learn import *


def main():
    login()
    semester = Semester()
    for course in semester.courses:
        path = 'file/' + course.name
        if not os.path.exists(path):
            os.makedirs(path)
        for file in course.files:
            file.save(path)


if __name__ == '__main__':
    main()