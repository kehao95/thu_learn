__author__ = 'kehao'
from thu_learn import *


def main():
    login()
    semester = Semester()
    for course in semester.courses:
        print('===%r==='% course.name)
        for work in course.works:
            print('\ntitle: %r' %work.title)
            print('details:\n%r'%work.details)


if __name__ == '__main__':
    main()
