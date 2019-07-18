# -*- coding: utf-8 -*-
import time
import logging
import hashlib
import itertools
from sina_iask_Model import  QuestionAnswer
import random

import requests
from requests import Session
from bs4 import BeautifulSoup
import sina_iask_Model

account_ls=[]
sina_iask_Model.somelist('res/account.txt')
for idx,x in enumerate(sina_iask_Model.somelist('res/account.txt')):
    account_ls.append(x.split(','))

class SinaIaskSpider(object):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
    }

    class Account(object):

        def __init__(self, username, session):
            self.username = username
            self.session = session
            self.proxy = {}

        def set_proxy(self, proxy):
            self.proxy = proxy

        def get(self, *args, **kwargs):
            while True:
                try:
                    r = self.session.get(*args, headers=kwargs.get('headers'), data=kwargs.get('data'),
                                         files=kwargs.get('files'), proxies=self.proxy, timeout=(5, 5))
                    return r
                except Exception as err:
                    print("%s" % err)
                    time.sleep(0.5)

        def post(self, *args, **kwargs):
            while True:
                try:
                    r = self.session.post(*args, headers=kwargs.get('headers'), data=kwargs.get('data'),
                                          files=kwargs.get('files'), proxies=self.proxy, timeout=(5, 5))
                    return r
                except Exception as err:
                    print("%s" % err)
                    time.sleep(0.5)

    def __init__(self, proxy_on=False):
        self.account_ls = [self.create_account(*account) for account in account_ls]
        self.proxy_on = proxy_on
        self.proxy_api = open("res/proxyapi.txt", "r").readline() if self.proxy_on else ''

    def create_account(self, username, password):
        s = Session()
        s.headers = self.headers
        login_url = "https://m.iask.sina.com.cn/cas-api/ppLogin"
        params = {
            'terminal': 'M',
            'businessSys': 'iask',
            'mobile': username,
            'password': self.str2md5(password),
        }

        while True:
            try:
                r = s.get(login_url, params=params, timeout=(5, 5))
                s.cookies.set('cuk', r.json()['data']['sessionId'], domain=".sina.com.cn")
                s.cookies.set('lsdt', r.json()['data']['syncTime'], domain=".sina.com.cn")

                user_url = "https://m.iask.sina.com.cn/checkUserLogin"
                r = s.post(user_url, timeout=(5, 5))
                username = r.json()['jsonData']['mobile']
                break
            except Exception as err:
                print("%s" % err)
                time.sleep(1)

        page = 1
        myquestions = []
        while True:
            myquestions_url = "https://iask.sina.com.cn/question/myquestions"
            data = {
                'pageNum': page,
                'pageSize': 10,
                'isNew': 'true',
                'source': 'WEIWEN'
            }
            r = s.post(myquestions_url, data=data)
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.find_all(class_='tab_kj1'):

                myquestions.append([item.find(class_='doid1').get_text().strip(),
                                    item.find(class_='ckbcl').get_text().strip(),''])
                if myquestions[-1][1] != u'审核未通过':
                    myquestions[-1][2] = "%s" % item.find(class_='doid1').attrs.get('href').replace(
                        'https://iask.sina.com.cn/b/', '').replace('.html?kindof=IQ', '')
            time.sleep(0.5)
            if not soup.find(id="currentPage") or not soup.find(class_="paging"):
                break
            if int(soup.find(id="currentPage").attrs['currentpage']) >= \
                    int(soup.find(class_="paging").attrs['pagecount']):
                break
            page += 1
        data_orgin=sina_iask_Model.Question_answer_data()
        for question in myquestions:
            data_qa=data_orgin
            data_qa.question_id=question[2]
            data_qa.question=question[0]
            data_qa.question_status=question[1]
            if len(data_qa.question)<=255:
                sina_iask_Model.question_answer_data_update(data_qa)
        page = 1
        myquestions = []
        while True:
            myquestions_url = "https://iask.sina.com.cn/question/myanswered"
            data = {
                'pageNum': page,
                'pageSize': 10,
                'isNew': 'true',
                'source': 'WEIWEN'
            }
            r = s.post(myquestions_url, data=data)
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.find_all(class_='answer'):
                if not item.find(class_='answer_cn'):
                    continue
                myquestions.append([item.find(class_='dldoi').get_text().strip(),
                                    item.find(class_='answer_cn').get_text().strip(),
                                    item.find(class_='answer_right').get_text().strip(),''])
                if myquestions[-1][1]:
                    myquestions[-1][3] = "%s" % item.find("a").attrs.get('href').replace(
                        'https://iask.sina.com.cn/b/', '').replace('.html?kindof=IQ', '').replace('.html?kindof=MA', '')
            time.sleep(0.5)
            if not soup.find(id="currentPage") or not soup.find(class_="paging"):
                break
            if int(soup.find(id="currentPage").attrs['currentpage']) >= \
                    int(soup.find(class_="paging").attrs['pagecount']):
                break
            page += 1
        for question in myquestions:
            data_qa=data_orgin
            data_qa.question_id=question[3]
            data_qa.question=question[0]
            data_qa.answer=question[1]
            data_qa.answer_status=question[2]
            if len(data_qa.question)<=255:
                sina_iask_Model.question_answer_data_update(data_qa)
        return self.Account(username, s)

    @staticmethod
    def str2md5(s):
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        return m.hexdigest()
    @staticmethod
    def get_questions(account, page):
        letters = "abcdefghijklmnopqrstuvwxyz"
        questions_url = "https://iask.sina.com.cn/map/q-%s-%s.html" % (letters[page // 100], page % 100)
        while True:
            try:
                r = account.post(questions_url)
                soup = BeautifulSoup(r.content, "html.parser")
                questions = []
                for item in soup.find(class_="indexing-list").find_all("li"):
                    questions.append("https://m.iask.sina.com.cn" + item.find("a")['href'])
                return questions
            except Exception as err:
                logging.error(err)
                time.sleep(1)

    @staticmethod
    def search_questions(account, keyword, page):
        search_url = "https://iask.sina.com.cn/search?searchWord=%s" % (keyword,)
        headers = {
            'Referer': "https://iask.sina.com.cn/search?searchWord=%E7%88%B1%E5%A5%87%E8%89%BA&page=1"
        }
        if page == 1:
            search_url += "&record=%s" % page
        else:
            search_url += "&page=%s" % page
        while True:
            try:
                r = account.get(search_url, headers=headers)
                soup = BeautifulSoup(r.content, "html.parser")
                questions = []
                if soup.find(class_="error-404"):
                    return []
                for item in soup.find(class_="iask-search-list").find_all("li"):
                    questions.append("https://m.iask.sina.com.cn" + item.find("a")['href'])
                return questions
            except Exception as err:
                logging.error(err)
                time.sleep(1)

    @staticmethod
    def post_question(account, content):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
            'Referer': 'https://m.iask.sina.com.cn/ask?content=',
            'Upgrade-Insecure-Requests': '1'
        }
        post_url = "https://m.iask.sina.com.cn/question/askq"
        data = {
            'title': content,
            'content': content,
            'reward': 0,
            'anon': 'N',
            'syn': 'N',
        }
        files = {'uploadedFile': ('', '')}
        account.post(post_url, headers=headers, data=data, files=files)
    @staticmethod
    def post_answer(account, content,question_id):
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0',
                'Referer': 'https://m.iask.sina.com.cn/question/sanswer',
                'Upgrade-Insecure-Requests': '1'
            }
            post_url = "https://m.iask.sina.com.cn/question/sanswer"
            data = {
                'content': content,
                'anon': 'N',
                'pageRefer':'' ,
                'syn': 'Y',
                'questionId': question_id,
                'questionSourceType': 'IMPORTDATA_Q_BUSINESS',
                'pageType': 'gerenzhongxin',
            }
            #r =requests.post(post_url,data,headers)
            account.post(post_url, headers=headers, data=data)
    @staticmethod
    def get_question_details(account, que_url):
        while True:
            r = account.get(que_url)
            soup = BeautifulSoup(r.content, "html.parser")
            if r.status_code != 200:
                return None
            break
        if soup.find(class_="m-b-question"):
            details = {
                'que': (soup.find(class_="m-b-text").get_text().strip().replace('\n', '').replace('\r', '') or
                        soup.find(class_="m-b-question-title").get_text().strip().replace('\n', '').replace('\r', '')),
                'ans': soup.find_all(class_="m-b-text")[1].get_text().strip().replace('\n', '').replace('\r', ''),
            }
        else:
            details = {
                'que': soup.find_all(class_="qs_cont")[-1].get_text().strip().replace('\n', '').replace('\r', '')
                if soup.find(class_="qs_cont") else
                soup.find(class_="qs_title").get_text().strip().replace('\n', '').replace('\r', ''),
                'ans': soup.find(class_="answer_lit").get_text().strip().replace('\n', '').replace('\r', '')
                if soup.find(class_="answer_lit") else
                soup.find(class_="answer-less-con").get_text().strip().replace('\n', '').replace('\r', ''),
            }
        return details

    def crawl(self):
        page = 1
        count = 1
        account_iter = itertools.cycle(self.account_ls)
        keyword = raw_input("输入搜索关键词:".decode('utf-8').encode('gbk'))
        while True:
            if keyword:
                questions = self.search_questions(next(account_iter), keyword, page)
                if not questions:
                    break
            else:
                questions = self.get_questions(next(account_iter), page)
            if not questions:
                time.sleep(1)
                continue
            for que_url in questions:
                account = next(account_iter)
                try:
                    question = self.get_question_details(account, que_url)
                except Exception as err:
                    continue
                if question is None:
                    continue
                print("[%s] que: %s ans: %s" % (account.username, question['que'], question['ans']))
                count += 1
                time.sleep(0.5)
            page += 1


if __name__ == '__main__':
    SinaIaskSpider(proxy_on=True).crawl()
