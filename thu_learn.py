# -*- coding: utf-8 -*-
__author__ = 'kehao'
import requests
from bs4 import BeautifulSoup, Comment
import re
import os
import getpass
import logging

_DebugLevel = logging.DEBUG
logging.basicConfig(level=logging.DEBUG)

# global vars
_session = requests.session()
_URL_BASE = 'https://learn.tsinghua.edu.cn'
_URL_LOGIN = _URL_BASE + '/MultiLanguage/lesson/teacher/loginteacher.jsp'

# 学期
_URL_CURRENT_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=1'
_URL_PAST_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2'
# 个人信息
_URL_PERSONAL_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/vspace/vspace_userinfo1.jsp'

# 课程不同板块前缀
# 课程公告
_PREF_MSG = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id='
# 课程信息
_PREF_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/course_info.jsp?course_id='
# 课程文件
_PREF_FILES = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/download.jsp?course_id='
# 教学资源
_PREF_LIST = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/ware_list.jsp?course_id='
# 课程作业
_PREF_WORK = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id='


def login(user_id=None, user_pass=None):
    """
    login to get cookies in _session
    :param user_id: your Tsinghua id "keh13" for example
    :param user_pass: your password
    :return:True if succeed
    """
    if user_id is None or user_pass is None:
        user_id = input("TsinghuaId:")
        user_pass = getpass.getpass("Password:")
    data = dict(
        userid=user_id,
        userpass=user_pass,
    )
    r = _session.post(_URL_LOGIN, data)
    # 即使登录失败也是200所以根据返回内容简单区分了
    if len(r.content) > 120:
        logging.debug("login failed")
        return False
    else:
        logging.debug("login success")
        return True


def make_soup(url):
    """
    _session.GET the page, handle the encoding and return the BeautifulSoup
    :param url: Page url
    :return: BeautifulSoup
    """
    r = _session.get(url)
    r.encoding = 'bgk'
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


class Semester:
    """
    Class Semester have all courses in it
    """

    def __init__(self, current=True):
        """
        set the current flag to get current/past Semester
        :param current: Boolean True/False for Current/Past semester
        :return: None
        """
        if _session is None:
            raise RuntimeError("Call login(userid, userpass) before anything else")
        if current:
            self.url = _URL_CURRENT_SEMESTER
        else:
            self.url = _URL_PAST_SEMESTER
        self._courses = list(self.courses)

    @property
    def courses(self):
        """
        return all the courses under the semester
        :return: Courses generator
        """
        soup = make_soup(self.url)
        for j in soup.find_all('tr', class_=['info_tr', 'info_tr2']):
            i = j.find('a')
            url = i['href']
            if url.startswith('/Mult'):
                url = _URL_BASE + url
            else:
                # !!important!! ignore the new WebLearning Courses At This moment
                continue
            name = i.contents[0]
            name = re.sub(r'[\n\r\t ]', '', name)
            name = re.sub(r'\([^\(\)]+\)$', '', name)
            id = url[-6:]
            yield Course(name=name, url=url, id=id)


class Course:
    """
    this is the Course class
    """

    def __init__(self, id, url=None, name=None):
        pass
        self._id = id
        self._url = url
        self._name = name
        self._works = list(self.works)
        self._files = list(self.files)
        self._messages = list(self.messages)
        logging.debug(name)

    @property
    def url(self):
        """course url"""
        return self._url

    @property
    def name(self):
        """course name"""
        return self._name

    @property
    def id(self):
        """courses id"""
        return self._id

    @property
    def works(self):
        """
        get all the work in course
        :return: Work generator
        """
        url = _PREF_WORK + self._id
        soup = make_soup(url)
        for i in soup.find_all('tr', class_=['tr1', 'tr2']):
            tds = i.find_all('td')
            url = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/' + i.find('a')['href']
            id = re.search(r'(\d+)', url).group(0)
            title = i.find('a').contents[0]
            start_time = tds[1].contents[0]
            end_time = tds[2].contents[0]
            submitted = ("已经提交" in tds[3].contents[0])
            yield Work(id=id, title=title, url=url, start_time=start_time, end_time=end_time, submitted=submitted)

    @property
    def messages(self):
        """
        get all messages in course
        :return: Message generator
        """
        url = _PREF_MSG + self.id
        soup = make_soup(url)
        for m in soup.find_all('tr', class_=['tr1', 'tr2']):
            tds = m.find_all('td')
            title = tds[1].contents[1].text
            url = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/' + tds[1].contents[1]['href']
            id = re.search(r"id=(\d+)", url).group(1)
            date = tds[3].text
            yield Message(title=title, url=url, date=date, id=id)
            # TODO

    @property
    def files(self):
        """
        get all files in course
        :return: File generator
        """

        def file_size_M(s):
            digitals = s[:-1]
            if s.endswith('K'):
                return float(digitals) / 1024
            elif s.endswith('M'):
                return float(digitals)
            else:
                return 1024 * float(digitals)

        url = _PREF_FILES + self.id
        soup = make_soup(url)
        for j in soup.find_all('tr', class_=['tr1', 'tr2']):
            name = re.search(r'getfilelink=([^&]+)&', str(j.find(text=lambda text: isinstance(text, Comment)))).group(1)
            a = j.find('a')
            url = 'http://learn.tsinghua.edu.cn/kejian/data/%s/download/%s' % (self.id, name)
            title = re.sub(r'[\n\r\t ]', '', a.contents[0])
            name = re.sub(r'_[^_]+\.', '.', name)
            size = file_size_M(j.find_all('td')[-3].text)
            yield File(size=size, name=name, url=url)
        pass

    @property
    def info(self):
        url = _PREF_INFO + self.id
        return Info(url)


class Work:
    """
    the homework class
    """

    def __init__(self, url=None, id=None, title=None, start_time=None, end_time=None, submitted=None):
        self._url = url
        self._id = id
        self._title = title
        self._details = self.details
        self._file = self.file
        self._start_time = start_time
        self._end_time = end_time
        self._submitted = submitted
        logging.debug(title)
        pass

    @property
    def url(self):
        """work url"""
        return self._url

    @property
    def id(self):
        """work id"""
        return self._id

    @property
    def title(self):
        """work title"""
        return self._title

    @property
    def start_time(self):
        """
        start date of the work
        :return:str time 'yyyy-mm-dd'
        """
        return self._start_time

    @property
    def end_time(self):
        """
        end date of the work
        :return: str time 'yyyy-mm-dd'
        """
        return self._end_time

    @property
    def submitted(self):
        """
        end date of the work
        :return: str time 'yyyy-mm-dd'
        """
        return self._submitted

    @property
    def details(self):
        """
        the description of the work
        :return:str details /None if not exists
        """
        soup = make_soup(self.url)
        try:
            _details = soup.find_all('td', class_='tr_2')[1].textarea.contents[0]
        except:
            _details = ""
        return _details

    @property
    def file(self):
        """
        the file attached to the work
        :return: Instance of File/None if not exists
        """
        soup = make_soup(self.url)
        try:
            fname = soup.find_all('td', class_='tr_2')[2].a.contents[0]
            furl = 'http://learn.tsinghua.edu.cn' + soup.find_all('td', class_='tr_2')[2].a['href']
            _file = File(url=furl, name=fname)
        except(AttributeError):
            _file = None
        return _file


class File:
    def __init__(self, url, name, size=0, note=None):
        self._name = name
        self._url = url
        self._note = note
        self._size = size

    def save(self, path='.'):
        r = requests.get(self.url, stream=True)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path + '/' + self.name, 'wb') as handle:
            if not r.ok:
                raise ValueError('failed in saving file', self.name, self.url)
            for block in r.iter_content(1024):
                handle.write(block)

    @property
    def name(self):
        """file name
        Note! the file name is the name on the web but not the name in the download link
        """
        return self._name

    @property
    def url(self):
        """download url"""
        return self._url

    @property
    def note(self):
        """the description of the file
        this will exits under the CourseFile area but not in work area
        # considering take course.details as note
        """
        return self._note

    @property
    def size(self):
        return self._size


class Message:
    def __init__(self, url, title, date, id):
        self._id = id
        self._url = url
        self._title = title
        self._date = date
        self._details = self.details
        logging.debug(title)

    @property
    def id(self):
        return self._id

    @property
    def url(self):
        return self._url

    @property
    def title(self):
        return self._title

    @property
    def date(self):
        return self._date

    @property
    def details(self):
        soup = make_soup(self.url)
        _details = soup.find_all('td', class_='tr_l2')[1].text.replace('\xa0', ' ')
        _details = re.sub('(\\xa0)+', ' ', _details)
        _details = re.sub('\n+', '\n', _details)
        return _details


class Info:
    class Teacher:
        def __init__(self, name, email, phone, intro):
            self.name = name
            self.email = email
            self.phone = phone
            self.intro = intro

    def __init__(self, url):
        self.soup = make_soup(url)
        tds = self.soup.find_all('td')
        self._课程编号 = tds[4].text.replace(" ", "")
        self._课程序号 = tds[6].text.replace(" ", "")
        self._课程名称 = tds[8].text.replace(" ", "")
        self._学分 = tds[10].text.replace(" ", "")
        self._学时 = tds[12].text.replace(" ", "")
        self._指定教材 = tds[27].text.replace(" ", "")
        self._参考数目 = tds[29].text.replace(" ", "")
        self._考核方式 = tds[31].text.replace(" ", "")
        self._课程简介 = tds[33].text.replace(" ", "")
        self._teacher = self.Teacher(
            name=tds[19].text.replace("\xa0", ""),
            email=tds[21].text.replace("\xa0", ""),
            phone=tds[23].text[1:].split(";"),
            intro=re.sub(r'[\r\t ]', '', tds[25].text),
        )


def test():
    pass


def main():
    test()


if __name__ == '__main__':
    main()
