from peewee import *

database = MySQLDatabase('sina_iask', **{'host': 'localhost', 'charset': 'utf8', 'user': 'root', 'use_unicode': True})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class QuestionAnswer(BaseModel):
    answer_status = CharField(null=True)
    answer_account = CharField(null=True)
    answer = CharField(null=True)
    question = CharField(null=True)
    question_account = CharField(null=True)
    question_id = CharField(null=True)
    question_status = CharField(null=True)

    class Meta:
        table_name = 'question_answer'
class Question_answer_data(object):
    def __init__(self):
        self.question_id=''
        self.question=''
        self.question_status=''
        self.answer=''
        self.question_account=''
        self.answer_account=''
        self.answer_status=''
    def keys(self):
        return ('question_id','question','question_status','answer','question_account','answer_account','answer_status')
    def __getitem__(self, item):
        return getattr(self, item)
def question_answer_data_update(data_qa):
    data={}
    for key,value in dict(data_qa).items():
        if value:
            data[key]=value
    try:
        Ques= QuestionAnswer.get(QuestionAnswer.question==data['question'])
    except Exception as e:
        Ques_id = QuestionAnswer.insert(data).execute()
    else:
        Ques= QuestionAnswer.update(data).where(QuestionAnswer.question ==data['question']).execute()