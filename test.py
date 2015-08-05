__author__ = 'kehao'
from thu_learn import *
from multiprocessing.dummy import Pool as ThreadPool


def main():
    pool = ThreadPool(8)
    print('Crawler v0.2')
    login()
    try:
        semester = Semester(current=False)
    except ValueError:
        print('failed to get Semester')
    for course in semester.courses:
        print(course.name, course.id, course.url)
        for work in course.works:
            # print(work.url)
            print(work.title, work.id, work.start_time, work.end_time)
            if work.file is not None:
                print(work.file.name, work.file.url)
                work.file.save(root=('file/' + course.name))
        '''
        # save files
        root = ('file/' + course.name)
        if not os.path.exists(root):
            os.makedirs(root)
        pool.map(lambda f: f.save(root=root), course.files)
        '''
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
