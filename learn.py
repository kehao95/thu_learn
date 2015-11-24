#! /usr/bin/python
# -*- coding: utf-8 -*-
import aiohttp
from bs4 import BeautifulSoup, Comment
import re
import os
import getpass
import asyncio
import logging
import time

__author__ = 'kehao'

# global vars
_URL_BASE = 'https://learn.tsinghua.edu.cn'
_URL_LOGIN = _URL_BASE + '/MultiLanguage/lesson/teacher/loginteacher.jsp'

# 学期
_URL_CURRENT_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
                        'lesson/student/MyCourse.jsp?typepage=1'
_URL_PAST_SEMESTER = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
                     'lesson/student/MyCourse.jsp?typepage=2'
# 个人信息
_URL_PERSONAL_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
                     'vspace/vspace_userinfo1.jsp'

# 课程不同板块前缀
_PREF_MSG = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
            'public/bbs/getnoteid_student.jsp?course_id='
_PREF_INFO = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
             'lesson/student/course_info.jsp?course_id='
_PREF_FILES = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
              'lesson/student/download.jsp?course_id='
_PREF_LIST = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
             'lesson/student/ware_list.jsp?course_id='
_PREF_WORK = 'http://learn.tsinghua.edu.cn/MultiLanguage/' \
             'lesson/student/hom_wk_brw.jsp?course_id='

loop = asyncio.get_event_loop()
_session = aiohttp.ClientSession(loop=loop)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def timing(f):
    """function timing wrapper"""

    def wrapper(*arg, **kw):
        t1 = time.time()
        ret = f(*arg, **kw)
        t2 = time.time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
              (f.__name__, arg, kw, t2 - t1))
        return ret

    return wrapper


def run(coroutine):
    r = loop.run_until_complete(coroutine)
    return r


async def make_soup(url):
    logger.debug("make_soup start %s" % url)
    try:
        r = await _session.get(url)
    except aiohttp.errors.ServerDisconnectedError:
        print(url)
        raise Exception("error in makesoup")
    soup = BeautifulSoup(await r.text(), "html.parser")
    logger.debug("make_soup done")
    return soup


def login(user_id=None, user_pass=None):
    """
    login to get cookies in _session
    :parm user_id: your Tsinghua id "keh13" for example
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

    async def get_resp(data):
        r = await _session.post(_URL_LOGIN, data=data)
        content = await r.text()
        return content

    r = loop.run_until_complete(get_resp(data))
    if len(r) > 120:
        raise RuntimeError(r)


class Semester:
    def __init__(self, current=True):
        if current is True:
            self.url = _URL_CURRENT_SEMESTER
        else:
            self.url =_URL_PAST_SEMESTER
        self.soup = run(make_soup(self.url))

    @property
    async def courses(self):
        async def get_course(j):
            # 一个异步地请求一个课程
            i = j.find('a')
            url = i['href']
            if url.startswith('/Mult'):
                url = _URL_BASE + url
            else:  # !!important!! ignore the new WebLearning Courses At This moment
                return None
            name = re.sub(r'\([^\(\)]+\)$', '', re.sub(r'[\n\r\t ]', '', i.contents[0]))
            id = url[-6:]
            return Course(name=name, url=url, id=id)

        async def get_courses(soup):
            # 异步地请求序列
            tasks = [get_course(i) for i in self.soup.find_all('tr', class_=['info_tr', 'info_tr2'])]
            courses = [c for c in await asyncio.gather(*tasks) if c is not None]
            return courses

        return await get_courses(self.soup)


class Course:
    def __init__(self, name, url, id):
        self.id = id
        self.name = name
        self.url = url

    @property
    async def works(self):
        async def get_work(item):
            tds = item.find_all('td')
            url = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/' \
                  + item.find('a')['href']
            id = re.search(r'(\d+)', url).group(0)
            title = item.find('a').contents[0]
            start_time = tds[1].contents[0]
            end_time = tds[2].contents[0]
            submitted = ("已经提交" in tds[3].contents[0])
            return Work(id, title, url, start_time, end_time, submitted)

        async def get_works(soup):
            tasks = [get_work(i) for i in soup.find_all('tr', class_=['tr1', 'tr2'])]
            works = await asyncio.gather(*tasks)
            return works

        works_url = _PREF_WORK + self.id
        works_soup = await make_soup(works_url)
        works = await get_works(works_soup)
        return works

    @property
    async def messages(self):
        async def get_message(item):
            tds = item.find_all('td')
            title = tds[1].contents[1].text
            url = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/' + tds[1].contents[1]['href']
            date = tds[3].text
            return Message(title=title, url=url, date=date)

        async def get_messages(soup):
            tasks = [get_message(i) for i in soup.find_all('tr', class_=['tr1', 'tr2'])]
            messages = await asyncio.gather(*tasks)
            return messages

        msg_url = _PREF_MSG + self.id
        msg_soup = await make_soup(msg_url)
        messages = await get_messages(msg_soup)
        return messages

    @property
    async def files(self):
        return []


class Work:
    def __init__(self, id, title, url, start_time, end_time, submitted):
        self.id = id
        self.title = title
        self.url = url
        self.start_time = start_time
        self.end_time = end_time
        self.submitted = submitted

    @property
    async def details(self):
        soup = await make_soup(self.url)
        try:
            details = soup.find_all('td', class_='tr_2')[1].textarea.contents[0]
        except IndexError:
            details = None
        return details


class Message:
    def __init__(self, title, url, date):
        self.title = title
        self.url = url
        self.date = date

    @property
    async def details(self):
        soup = await make_soup(self.url)
        details = soup.find_all('td', class_='tr_l2')[1].text.replace('\xa0', ' ')
        details = re.sub('(\\xa0)+', ' ', details)
        details = re.sub('\n+', '\n', details)
        return details


@timing
def main():
    import json
    with open("secret.json", "r") as f:
        secrets = json.loads(f.read())
    login(user_id=secrets['username'], user_pass=secrets['password'])
    # courses
    semester = Semester(False)





def test():
    # make soup
    url = "http://www.zhihu.com/question/37191376"
    soup = loop.run_until_complete(make_soup(url))
    # make soups
    soup = run(make_soup(url))
    # login
    import json
    with open("secret.json", "r") as f:
        secrets = json.loads(f.read())
    login(user_id=secrets['username'], user_pass=secrets['password'])
    # courses
    semester = Semester()
    async def foo():
        courses = await semester.courses
        messages = [item for sublist in await asyncio.gather(*[course.messages for course in courses])
                    for item in sublist]
        details = await  asyncio.gather(*[message.details for message in messages])
        for detail in details:
            print(detail[:5])

    loop.run_until_complete(foo())

if __name__ == '__main__':
    # test()
    main()
    _session.close()
