# -*- coding: GBK -*-
__author__ = 'kehao'
import requests
from bs4 import BeautifulSoup
import re

# global vars
output = open("TEST.txt", "w", encoding='utf-8')
_session = requests.session()
_userid = input('userid:')
_userpass = input('userpass:')
_URL_BASE = 'https://learn.tsinghua.edu.cn'
_URL_LOGIN = _URL_BASE + '/MultiLanguage/lesson/teacher/loginteacher.jsp'

# 两链接是不同的学期
_URL_CURRENT_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=1'
_URL_PAST_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2'

# 旧版网络学堂各板块prefex
# 公告
_PREF_NTF = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id='
# 信息
_PREF_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/course_info.jsp?course_id='
# 课程文件
_PREF_DOWN = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/download.jsp?course_id='
# 教学资源
_PREF_LIST = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/ware_list.jsp?course_id='
# 课程作业
_PREF_WORK = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id='

def set_

def init():
    """
    init options login to get cookies
    :return:
    """
    data = dict(
        userid=_userid,
        userpass=_userpass,
    )
    _session.post(_URL_LOGIN, data)


class Semester:
    """
    this is the Semester class
    using the url as id
    """

    def __init__(self, current=True):
        if current:
            self.url = _URL_CURRENT_SEMESTER
        else:
            self.url = _URL_PAST_SEMESTER
        self.r = _session.get(self.url)
        self.r.encoding = 'bgk'
        self.soup = BeautifulSoup(self.r.content, "html.parser")
        pass

    def courses(self):
        """
        get all courses in the home
        :return: Course obj        self.name = name
        """
        list = []
        for i in self.soup.find_all('tr', class_='info_tr2'):
            list.append(i.find('a'))
        for i in self.soup.find_all('tr', class_='info_tr'):
            list.append(i.find('a'))
        for i in list:
            url = i['href']
            if url.startswith('/Mult'):
                url = _URL_BASE + url
            else:
                # !!important!! ignore the new WebLearning Courses At This moment
                continue
            name = i.contents[0]
            name = re.sub(r'[\n\r\t ]', '', name)
            id = url[-6:]
            yield Course(name=name, url=url, id=id)

    def save(self):
        with open('result.html', 'w', encoding="gbk") as f:
            f.write(self.r.text)

    def print(self):
        print(self.r)


class Course:
    """
    this is the Course class
    """

    def __init__(self, id, url=None, name=None):
        self.id = id
        self.url = url
        self.name = name
        self.r = None
        self.show()

    def show(self):
        output.write(u'url:' + self.url + u'\n')
        output.write(u'name:' + self.name + u'\n')
        output.write(u'id:' + self.id + u'\n')

    def works(self):
        url = _PREF_WORK + self.id
        self.r = _session.get(url)
        self.r.encoding = 'bgk'
        soup = BeautifulSoup(self.r.content, "html.parser")
        list = []
        for i in soup.find_all('tr', class_='tr1'):
            list.append(i)
        for i in soup.find_all('tr', class_='tr2'):
            list.append(i)
        for i in list:
            # TODO
            # start_date
            # end_date
            # id
            href = i.find('a')['href']
            title = i.find('a').contents[0]
            yield Work(title=title)


class Work:
    """
    the homework class
    """

    def __init__(self, title, details=None, file_link=None):
        self.id = id
        self.title = title
        self.details = details
        self.file_link = file_link

    def show(self):
        output.write(u'work-title:' + self.title + u'\n')


init()


def main():
    import test
    test.main()


if __name__ == '__main__':
    main()
