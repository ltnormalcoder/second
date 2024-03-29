# -*- coding: utf-8 -*-
from sina_iask import SinaIaskSpider
import xlrd
from datetime import date,datetime
from sina_iask import SinaIaskSpider
import random
import time
import sina_iask_Model 
from sina_iask_Model import  QuestionAnswer
from sina_iask_Model import  Question_answer_data
from sina_iask_Model import  Config

def import_question_answer():
    file = 'res/question_answer.xls'
    # 1、打开文件
    x1 = xlrd.open_workbook(file)
    # 获取sheet的汇总数据
    sheet1 = x1.sheet_by_name("Sheet1")
    data_qa=Question_answer_data()
    for x in xrange(0,sheet1.nrows):
        data_qa.question=sheet1.row(x)[0].value
        data_qa.answer=sheet1.row(x)[1].value
        sina_iask_Model.question_answer_data_update(data_qa)
def main_function():
    if __name__ == '__main__':
        user_select = raw_input("输入选项 import_questionAnswer/submit_all_question/submit_all_answer :".decode('utf-8').encode('gbk'))
        if user_select == 'submit_all_question':
            spider = SinaIaskSpider()
            data_qa=Question_answer_data()
            Ques= QuestionAnswer.select().where(QuestionAnswer.question_status==None)
            for x in Ques:
                data={}
                data['value']=Config.get(Config.name=='acount_list_num').value
                question_account=spider.account_ls[int(data['value'])]
                data_qa.question=x.question
                data_qa.question_status='已提问'
                data_qa.question_account=question_account.username
                if (len(spider.account_ls)-1)<=data['value']:
                    data['value']=int(data['value'])+1
                else:
                    data['value']=0
                data_qa.answer_account=spider.account_ls[int(data['value'])].username
                spider.post_question(question_account,x.question)
                sina_iask_Model.question_answer_data_update(data_qa)
                sina_iask_Model.update_config('acount_list_num',data)
                time.sleep(1)
            print '提交问题成功！'.decode('utf-8').encode('gbk')
    elif user_select == 'submit_all_answer':
        spider = SinaIaskSpider()
        data_qa=Question_answer_data()
        Ques= QuestionAnswer.select().where(QuestionAnswer.question_status=='查看并处理')
        for x in Ques:
            if x.answer and x.answer_status=='':
                for idx,value in enumerate(spider.account_ls):
                    if value.username==x.answer_accoun:
                        answer_account=spider.account_ls[idx]
                data_qa.question=x.question
                data_qa.answer_status='已回答'
                spider.post_answer(answer_account,x.answer)
                sina_iask_Model.question_answer_data_update(data_qa)
                time.sleep(1)
    elif user_select == 'import_questionAnswer':
        import_question_answer()
        print '导入问答数据成功！'.decode('utf-8').encode('gbk')
