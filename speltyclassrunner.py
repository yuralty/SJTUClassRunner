
# -*- coding: utf-8 -*- 
import time, threading
import cookielib, urllib, urllib2, re
from bs4 import BeautifulSoup

class ClassRunner(object):
    """docstring for ClassRunner"""
    def __init__(self):
        self.cookiejar = cookielib.LWPCookieJar('aaa.txt')
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
        self.header = [ ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.65 Safari/537.36'), ]
        self.opener.addheaders = self.header
        self.viewstate = 0
        self.eventvalidation = 0
        
        # User infomation
        self.username = '5110309810'
        self.psword = '03110211'


        # URLs       
        self.homeurl = 'http://electsys.sjtu.edu.cn/edu/'
        self.loginurl = 'http://electsys.sjtu.edu.cn/edu/index.aspx'
        self.mainurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/warning.aspx?&xklc=3&lb=1'
        self.speltyurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/speltyRequiredCourse.aspx'
        self.departmenturl = 'http://electsys.sjtu.edu.cn/edu/student/elect/outSpeltyEP.aspx'
        self.classurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/outSpeltyEP.aspx'
        self.returnurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/outSpeltyEp.aspx?yxdm=09000&nj=2011&kcmk=-1&txkmk=-1&tskmk='
        self.saveurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/secondRoundFP.aspx'


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

    def goThirdRoundSpelty(self):
        """docstring for goThirdRound"""
        """no input params, return spelty page"""
        page = self.getPage(self.mainurl)
        self.refreshState(page)
        values = {'__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'SpeltyRequiredCourse1$btnXuanXk': '任选课' }
        data = urllib.urlencode(values)
        page = self.postPage(self.speltyurl, data)
        return page
        
    def trySelect(self, page, department, grade, classID):
        """docstring for trySelect"""
        """
        input params: department:string, classID:string
        """
        self.refreshState(page)
        values = {'__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'OutSpeltyEP1$dpYx': department, 'OutSpeltyEP1$dpNj': grade, 'OutSpeltyEP1$btnQuery': '查 询'}
        data = urllib.urlencode(values)
        page = self.postPage(self.departmenturl, data)
        self.refreshState(page)
        values = {'__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'OutSpeltyEP1$dpNj': grade, 'myradiogroup': classID,
            'OutSpeltyEP1$lessonArrange': '课程安排' }
        data = urllib.urlencode(values)
        page = self.postPage(self.classurl, data)
        self.refreshState(page)
        soup = BeautifulSoup(page)
        myradiogroup = soup.findAll('input', type='radio')[0]['value']
        values = {'__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'myradiogroup': myradiogroup, 'LessonTime1$btnChoose': '选定此教师'}
        data = urllib.urlencode(values)
        selecturl = 'http://electsys.sjtu.edu.cn/edu/lesson/viewLessonArrange.aspx?kcdm=' + classID + '&xklx=%u9009%u4fee&redirectForm=outSpeltyEp.aspx&yxdm=' + department + '&nj=' + grade + '&kcmk=-1&txkmk=-1'
        page = self.postPage(selecturl, data)
        self.returnurl = 'http://electsys.sjtu.edu.cn/edu/student/elect/outSpeltyEp.aspx?yxdm=' + department + '&nj=' + grade + '&kcmk=-1&txkmk=-1&tskmk='
        page = self.getPage(self.returnurl)
        return page
    
    def saveClass(self, page, department, grade):
        """docstring for saveClass"""
        self.refreshState(page)
        
        values = {'__EVENTTARGET' : '', '__EVENTARGUMENT': '', '__VIEWSTATE': self.viewstate[0], '__EVENTVALIDATION': self.eventvalidation[0], 'btnSubmit': '选课提交'}
        data = urllib.urlencode(values)
        page = self.postPage(self.returnurl, data)
        #print page
        return page
        

    def run(self, department, grade, classID):
        """docstring for run"""
        page = self.login()
        page = self.goThirdRoundSpelty()
        page = self.trySelect(page, department, grade, classID)
        count = 1
        while '该课该时间段人数已满' in page:
            print 'Tried %d times.' % count
            print 'Web failed %d times' % self.__fail
            count += 1
            time.sleep(5)
            page = self.goThirdRoundSpelty()
            page = self.trySelect(page, department, grade, classID)
        if '网页已过期，请重新登陆！' in page:
            self.run(department, grade, classID)
            self.__fail += 1
        page = self.saveClass(page, department, grade)

class Request(object):
    """docstring for Request"""
    def __init__(self, department, grade, classID):
        
        self.department, self.grade, self.classID = department, grade, classID
        

def threadRunner(request):
    """docstring for  thread"""
    cr = ClassRunner()
    department = request.department
    grade = request.grade
    classID = request.classID
    cr.run(department,grade, classID)
        


if __name__ == '__main__':
    cl = []
    cl.append(Request('09000', '2011', 'PL015'))

    threadlist = []
    for request in cl:
        threadlist.append(threading.Thread(target=threadRunner, args=(request,)))
    for t in threadlist:
        t.start()
        
    #cr = ClassRunner()
    #department = '09000'
    #grade = '2011'
    #classID = 'PL015'
    #cr.run(department, grade, classID)
