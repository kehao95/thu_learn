__author__ = 'kehao'
from thu_learn import *
import sys


def main():
    login()
    Q = []
    semester = Semester(current=True)
    for course in semester.courses:
        for work in course.works:
            if not work.submitted:
                Q.append((work, course.name))

    Q.sort(key=lambda w: w[0].end_time)
    for w in Q:
        courseName = w[1]
        work = w[0]
        print(">>%s<<\n%s %s \n%s" % (work.end_time, courseName, work.title, work.details))


if __name__ == "__main__":
    main()
