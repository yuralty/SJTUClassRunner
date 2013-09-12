# -*- coding: utf-8 -*- 
import time, threading
import cookielib, urllib, urllib2, re
from bs4 import BeautifulSoup

class ClassRunner(object):
    """docstring for ClassRunner"""
    def __init__(self, subject):
        self.cookiejar = cookielib.LWPCookieJar('aaa.txt')
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        self.header = [ ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.65 Safari/537.36'), ]
        self.opener.addheaders = self.header
        self.viewstate = 0
        self.eventvalidation = 0
        self.sub1, self.sub2 = subject
        
        # User infomation
        self.username = '5110309746'
        self.psword = '08221019'


        # URLs       
        self.homeurl = 'http://electsys.sjtu.edu.cn/edu/'
        self.loginurl = 'http://electsys.sjtu.edu.cn/edu/index.aspx'
        self.mainurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/warning.aspx?&xklc=3&lb=1'
        self.commonurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/speltyRequiredCourse.aspx'
        self.commonsuburl = 'http://electsys.sjtu.edu.cn/edu/student/elect/speltyCommonCourse.aspx'
        self.classurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/speltyCommonCourse.aspx'
        self.saveurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/speltyCommonCourse.aspx?yxdm=&nj=%u65e0&kcmk=-1&txkmk=&tskmk=450'


        self.__fail = 0


    def getPage(self, url):
        response = self.opener.open(url)
        page = response.read()
        response.close()
        return page

    def postPage(self, url, data):
        """docstring for postPage"""
        response = self.opener.open(url, data)
        page = response.read()
        response.close()
        return page

    def refreshState(self, page):
        """docstring for refreshState"""
        self.viewstate = re.findall('<input[^>]*name=\"__VIEWSTATE\"[^>]*value=\"([^"]*)\"[^>]*>', page, re.S)
        self.eventvalidation = re.findall('<input[^>]*name=\"__EVENTVALIDATION\"[^>]*value=\"([^"]*)\"[^>]*>', page, re.S)
        

    def login(self):
        """docstring for login"""
        page = self.getPage(self.homeurl)
        self.refreshState(page)
        values = {'__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'txtUserName': self.username, 'txtPwd': self.psword, 'rbtnLst': '1', 'Button1': '登录'}
        data = urllib.urlencode(values)
        page = self.postPage(self.loginurl, data)
        return page

    def goThirdRoundCommon(self):
        """docstring for goThirdRound"""
        """no input params, return spelty page"""
        page = self.getPage(self.mainurl)
        
        self.refreshState(page)
        values = {'__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'SpeltyRequiredCourse1$btnTxk': '通识课' }
        data = urllib.urlencode(values)
        page = self.postPage(self.commonurl, data)
        return page
        
    def trySelect(self, page, grade, classID):
        """docstring for trySelect"""
        """
        input params: department:string, classID:string
        """
        self.refreshState(page)
        values = {'__EVENTTARGET': 'gridGModule$ctl'+ self.sub1+'$radioButton', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'gridGModule$ctl'+ self.sub1 + '$radioButton':'radioButton', 'gridGModule$ctl' + self.sub2 + '$radioButton':'radioButton'}
        data = urllib.urlencode(values)
        page = self.postPage(self.commonsuburl, data)
        self.refreshState(page)
        values = {'__EVENTTARGET': '', '__EVENTARGUMENT': '', '__LASTFOCUS': '', '__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'gridGModule$ctl' + self.sub1 + '$radioButton':'radioButton', 'myradiogroup': classID, 'lessonArrange': '课程安排'} 
        data = urllib.urlencode(values)
        page = self.postPage(self.classurl, data)
        self.refreshState(page)
        soup = BeautifulSoup(page)
        myradiogroup = soup.findAll('input', type='radio')[0]['value']
        values = {'__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'myradiogroup': myradiogroup, 'LessonTime1$btnChoose': '选定此教师'}
        data = urllib.urlencode(values)
        selecturl = 'http://electsys.sjtu.edu.cn/edu/lesson/viewLessonArrange.aspx?kcdm=' + classID + '&xklx=%u901a%u8bc6&redirectForm=speltyCommonCourse.aspx&yxdm=&tskmk=420&kcmk=-1&nj=%u65e0'
        page = self.postPage(selecturl, data)
        return page
    
    def saveClass(self, page, grade):
        """docstring for saveClass"""
        self.refreshState(page)
        values = {'__EVENTTARGET' : '', '__EVENTARGUMENT': '', '__LASTFOCUS':'', '__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'btnSubmit': '选课提交'}
        data = urllib.urlencode(values)
        page = self.postPage(self.saveurl, data)
        return page
        

    def run(self, grade, classID):
        """docstring for run"""
        self.login()
        page = self.goThirdRoundCommon()
        page = self.trySelect(page, grade, classID)
        count = 1
        while '该课该时间段人数已满' in page:
            print 'Current Thread: %s' % classID
            print 'Tried %d times.' % count
            #print 'Web failed %d times' % self.__fail
            count += 1
            time.sleep(5)
            page = self.goThirdRoundCommon()
            page = self.trySelect(page, grade, classID)
        if '网页已过期，请重新登陆！' in page:
            self.run(grade, classID)
            self.__fail += 1
        page = self.saveClass(page, grade)

class Request(object):
    """docstring for Request"""
    def __init__(self, subject, grade, classID):
        dict = {'human': ('02', '05'),
                'social': ('03', '02'),
                'physics': ('04', '03'),
                'math': ('05', '04')
                }
        self.subject, self.grade, self.classID = dict[subject], grade, classID
        


def threadRunner(request):
    """docstring for  thread"""
    cr = ClassRunner(request.subject)
    grade = request.grade
    classID = request.classID
    cr.run(grade, classID)


if __name__ == '__main__':
    cl = []
    cl.append(Request('human', '2011', 'CH901'))
    cl.append(Request('human', '2011', 'CL914'))

    threadlist = []
    for request in cl:
        threadlist.append(threading.Thread(target=threadRunner, args=(request,)))
    for t in threadlist:
        t.start()
        
    
    #cr = ClassRunner(dict['human'])

    #grade = '2011'
    #classID = 'CH901'
    #cr.run(grade, classID)
