# THULearn
清华大学网络学堂爬虫

## 简单使用
```
- import thu_learn
- 使用login函数（根据返回值可以判断是否登录成功True/False）
- 初始实例化一个学期对象
semester = Semester() //当前学期
semester = Semester(current=False) //之前所有学期
- 直接点号访问对象的子元素，相同当子元素数量大于一时返回为iterable
for course in semester.courses:
    course.name
    course.url
    course.id
    for work in course.works:
        work.title
        work.url
        ....
    for file in course.files:
        file.save(path)
        ...
```


欢迎编辑WIKI [https://github.com/kehao95/THULearn/wiki](https://github.com/kehao95/THULearn/wiki)
欢迎fork+PR


### 目前可用功能
请参照Wiki[网络学堂基本元素结构](https://github.com/kehao95/THULearn/wiki/%E7%BD%91%E7%BB%9C%E5%AD%A6%E5%A0%82%E5%9F%BA%E6%9C%AC%E5%85%83%E7%B4%A0%E7%BB%93%E6%9E%84)

- Semester
    - courses
- Course
    - name
    - id
    - works
    - files
- Work
    - id
    - url
    - title
    - start_time
    - end_time
    - file
- File
    - name
    - note
    - url
    - save
- Message
    - title
    - url
    - details
    - date
