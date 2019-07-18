# -*- coding: utf-8 -*-
import xlrd
from datetime import date,datetime
from sina_iask import SinaIaskSpider

file = 'res/question_answer.xls'

# 1、打开文件
x1 = xlrd.open_workbook(file)

# 获取sheet的汇总数据
sheet1 = x1.sheet_by_name("Sheet1")

spider = SinaIaskSpider()
for x in xrange(0,sheet1.nrows):
	spider.question_answer_data_update(66,sheet1.row(x)[0].value,'未提问',sheet1.row(x)[1].value,6,6)
	print sheet1.row(x)[0].value  # get sheet all columns number