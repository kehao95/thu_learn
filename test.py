__author__ = 'kehao'
from thu_learn import *
from thu_learn import Semester
from thu_learn import Course
from thu_learn import Work


def main():
    print('Crawler v0.1')
    try:
        semester = Semester(current=False)
    except ValueError:
        print('failed to get Semester')
    for course in semester.courses:
        print(course.name, course.id, course.url)
        for work in course.works:
            print(work.title)



if __name__ == '__main__':
    main()
