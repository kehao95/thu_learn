__author__ = 'kehao'
from thu_learn import *
from multiprocessing.dummy import Pool
import time


def test_semester():
    print('')
    semester = Semester(current=True)
    return semester.courses


def test_courses(courses):
    def foo(course):
        print(course.name, course.id, course.url[:10])
        return course.works, course.files, course.messages

    pool = Pool(_thread_size)
    r = pool.map(foo, courses)
    pool.close()
    pool.join()
    '''
    for course in courses:
        print(course.name, course.id, course.url[:10])
        yield course.works, course.files, course.messages
    '''
    return r


def test_works(works):
    def foo(work):
        print(work.title, work.url[:10])

    pool = Pool(_thread_size)
    pool.map(foo, works)
    pool.close()
    pool.join()
    '''
    for work in works:
        print(work.title, work.url[:10])
    '''


def test_files(files):
    def foo(file):
        print(file.name, file.url[:10])

    pool = Pool(_thread_size)
    pool.map(foo, files)
    pool.close()
    pool.join()

    '''
    for file in files:
        print(file.name, file.url[:10])
    '''


def test_messages(messages):
    def foo(message):
        print(message.title, message.date, message.details)

    pool = Pool(_thread_size)
    pool.map(foo, messages)
    pool.close()
    pool.join()
    '''
    for message in messages:
        print(message.title, message.date, message.details)
    '''


def test_all():
    login()
    courses = test_semester()
    for works, files, messages in test_courses(courses):
        print('works:')
        test_works(works)
        print('files:')
        test_files(files)
        print('messages:')
        test_messages(messages)


_thread_size = 8


def main():
    start = time.time()
    print('Crawler v1.0')
    test_all()
    end = time.time()
    print('thread %r using time %rs' % (_thread_size, end - start))

    if __name__ == '__main__':
        main()
