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
        work = w[0]
        print(">>>>>%r\n%s %s \n\t%s" % (work.end_time, work.title, w[1], work.details))


if __name__ == "__main__":
    main()
