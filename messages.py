__author__ = 'kehao'
from thu_learn import *

def main():
    login()
    semester = Semester()
    messages = []
    for course in semester.courses:
        print(course.name)
        for message in course.messages:
            messages.append(message)

    messages.sort(key=lambda x: x.date, reverse=True)
    for m in messages:
        print(">>\t%s_%s\n%s"%(m.title,m.date,m.details.replace("\t\n ","")[:100]))


if __name__ == '__main__':
    main()


