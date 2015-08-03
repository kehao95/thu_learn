__author__ = 'kehao'
from web_learning import *
from web_learning import Semester
from web_learning import Course
from web_learning import Work


def main():
    print('Crawler v0.1')
    try:
        semester = Semester()
    except ValueError:
        print('failed to get Semester')
    for course in semester.courses():
        print(course.name, course.id, course.url)
        for work in course.works():
            print(work.title)


if __name__ == '__main__':
    main()
