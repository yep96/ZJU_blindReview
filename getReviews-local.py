import requests, re, zlib, time, pickle
from bs4 import BeautifulSoup as bs
requests.packages.urllib3.disable_warnings()


class getBlindReviews:
    def __init__(self, user, passwd, pushKey, basePath='.'):
        self.pushKey = str(pushKey)
        self.user = str(user)
        self.passwd = str(passwd)
        if basePath[-1] != '/': basePath += '/'
        self.getPath = lambda x: basePath + x
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'accept-language': 'zh-CN,zh;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
        }
        try:
            self.check()
        except Exception as e:
            self.send('盲审通知', '查询失败 ' + str(e) + time.strftime('%D'))

    def send(self, title='', text=''):
        # pushplus 在短时间内无法重复发送相似信息
        msg = f'{title}-{text}\n'
        with open(self.getPath(self.user+'.history'), 'a+') as history:
            history.seek(0)
            if all(msg != line for line in history):
                data = {'token': self.pushKey, 'title': title, 'content':text, 'template':'markdown'}
                requests.post(url='https://www.pushplus.plus/send', headers={'Content-Type': 'application/json'}, json=data)
                history.write(msg)

    def login(self):
        self.session = requests.session()
        login_url = 'https://zjuam.zju.edu.cn/cas/login?service=https://service.zju.edu.cn'
        res = self.session.get(url=login_url, headers=self.headers, verify=False)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.session.get(url='https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers=self.headers, verify=False).json()
        M_str, e_str = res['modulus'], res['exponent']
        password_bytes = bytes(self.passwd, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        M_int = int(M_str, 16)
        result_int = pow(password_int, e_int, M_int)
        encrypt_password = hex(result_int)[2:].rjust(128, '0')
        data = {
            'username': self.user,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit',
            'rememberMe': True
        }
        res = self.session.post(url=login_url, headers=self.headers, data=data, verify=False)
        assert '注销' in res.text
        with open(self.getPath(self.user), 'wb') as f:
            pickle.dump(self.session, f)

    def getReviews(self):
        # 通过统一认证生成grs的cookies
        self.session.get('https://grs.zju.edu.cn/ssohome', headers=self.headers, verify=False)
        res = self.session.get('http://grs.zju.edu.cn/degree/page/xwsq/stu_xwsq_result.htm', headers=self.headers)
        reviews = bs(res.text, features='lxml').select('#d1_form > div > div:nth-child(15)')[0]
        reviews = reviews.find_all('li')[1:-2]
        markdown, text = '' if reviews else '空', ''
        for review in reviews:
            tmp = ','.join(review.text.split()[1:])
            text += '(' + tmp + ')  '
            tmp = f'[{tmp}](http://grs.zju.edu.cn{review.a.get("href")})'
            markdown += '（' + tmp + '） '
        self.send('盲审通知', '盲审意见：'+markdown)
        print(time.strftime('%Y-%m-%d %H:%M:%S'), text)

    def check(self):
        try:
            with open(self.getPath(self.user), 'rb') as f:
                self.session = pickle.load(f)
            self.getReviews()
        except Exception:
            print(time.strftime('%Y-%m-%d %H:%M:%S'), '重新登录')
            self.login()
            self.getReviews()


if __name__ == '__main__':
    # 用户学号列表，可以同时查询多个用户，用英文,隔开
    userList = ['学号1']
    # 用户密码列表
    passwdList = ['密码1']
    # pushplus推送token列表
    pushKeyList = ['token1']
    # 保存相关文件的绝对路径
    basePath = 'absolutePath'
    for user, passwd, pushKey in zip(userList, passwdList, pushKeyList):
        getBlindReviews(user, passwd, pushKey, basePath)