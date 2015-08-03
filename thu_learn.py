# -*- coding: GBK -*-
__author__ = 'kehao'
import requests
from bs4 import BeautifulSoup
import re
import json
import os



# global vars
output = open("TEST.txt", "w", encoding='utf-8')
_session = requests.session()
_userid = input('userid:')
_userpass = input('userpass:')
_URL_BASE = 'https://learn.tsinghua.edu.cn'
_URL_LOGIN = _URL_BASE + '/MultiLanguage/lesson/teacher/loginteacher.jsp'

# Á½Á´½ÓÊÇ²»Í¬µÄÑ§ÆÚ
_URL_CURRENT_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=1'
_URL_PAST_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2'

# ¾É°æÍøÂçÑ§ÌÃ¸÷°å¿éprefex
# ¹«¸æ
_PREF_NTF = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id='
# ÐÅÏ¢
_PREF_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/course_info.jsp?course_id='
# ¿Î³ÌÎÄ¼þ
_PREF_DOWN = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/download.jsp?course_id='
# ½ÌÑ§×ÊÔ´
_PREF_LIST = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/ware_list.jsp?course_id='
# ¿Î³Ì×÷Òµ
_PREF_WORK = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id='


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


def make_soup(url):
    r = _session.get(url)
    r.encoding = 'bgk'
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


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
        self.soup = make_soup(self.url)
        pass

    @property
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
        self._id = id
        self._url = url
        self._name = name
        self.r = None
        self.show()

    def show(self):
        output.write(u'url:' + self._url + u'\n')
        output.write(u'name:' + self._name + u'\n')
        output.write(u'id:' + self._id + u'\n')

    @property
    def url(self):
        return self._url

    @property
    def name(self):
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def works(self):
        url = _PREF_WORK + self._id
        soup = make_soup(url)
        list = []
        for i in soup.find_all('tr', class_='tr1'):
            list.append(i)
        for i in soup.find_all('tr', class_='tr2'):
            list.append(i)
        for i in list:
            # TODO
            tds = i.find_all('td')
            url = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/' + i.find('a')['href']
            id = re.search(r'(\d+)', url).group(0)
            title = i.find('a').contents[0]
            start_time = tds[1].contents[0]
            end_time = tds[2].contents[0]
            yield Work(id=id, title=title, url=url, start_time=start_time, end_time=end_time)

    @property
    def messages(self):
        pass
        # TODO

    @property
    def files(self):
        pass
        # TODO


class Work:
    """
    the homework class
    """

    def __init__(self, url=None, id=None, title=None, start_time=None, end_time=None):
        self._url = url
        self._id = id
        self._title = title
        self._details = None
        self._file = None
        self._start_time = start_time
        self._end_time = end_time
        self.soup = make_soup(self.url)
        pass

    def show(self):
        output.write(u'work-title:' + self._title + u'\n')

    @property
    def url(self):
        return self._url

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        return self._title

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time

    @property
    def details(self):
        if self._details is None:
            try:
                self._details = self.soup.find_all('td', class_='tr_2')[1].textarea.contents[0]
            except:
                pass
        return self._details

    @property
    def file(self):
        if self._file is None:
            try:
                fname = self.soup.find_all('td', class_='tr_2')[2].a.contents[0]
                furl = 'http://learn.tsinghua.edu.cn' + self.soup.find_all('td', class_='tr_2')[2].a['href']
                self._file = File(url=furl, name=fname)
            except:
                pass
        return self._file


class File:
    def __init__(self, url, name=None, note=None):
        self._name = name
        self._url = url
        self._note = note

    def save(self, root='.'):
        if not os.path.exists(root):
            os.makedirs(root)
        r = requests.get(self.url)
        with open(root + '/' + self.name, 'wb') as f:
            f.write(r.content)

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def note(self):
        return self._note


init()


def main():
    import test
    test.main()


if __name__ == '__main__':
    main()
