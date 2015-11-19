__author__ = 'kehao'
from thu_learn import *
import re


def main():
    login()
    semester = Semester()
    messages = []
    for course in semester.courses:
        # print(course.name)
        for message in course.messages:
            messages.append(message)

    messages.sort(key=lambda x: x.date, reverse=False)
    for m in messages[:5]:
        details = re.sub(r"[\n\t \xa0]", "", m.details)[:100] + "..."
        print(">>%s<<\n%s\n%s\n" % (m.date, m.title, details))


if __name__ == '__main__':
    main()
