import requests
import aiohttp
import asyncio
import time

urls = [
    "http://www.zhihu.com/question/34427479",
    "http://www.zhihu.com/question/37546129",
    "http://www.zhihu.com/question/37659720",
    "http://www.zhihu.com/question/37740839",
    "http://www.zhihu.com/question/28575864",
    "http://www.zhihu.com/question/37740839",
    "http://www.zhihu.com/question/37767644",
    "http://www.zhihu.com/question/37721533"]

urls = urls[:3]




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



async def get_body(url):
    print("Start request")
    response = await aiohttp.get(url)
    html = await response.read()
    print("End request")
    return html

async def par():
    tasks = [get_body(url) for url in urls]
    for body in await asyncio.gather(*tasks):
        print(body[:16])


@timing
def run_asyncio():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(par())


@timing
def run_normal():
    for url in urls:
        print("Start request")
        body = requests.get(url).content
        print("End request")
        print(body[:16])


if __name__ == '__main__':
    run_asyncio()
    run_normal()
