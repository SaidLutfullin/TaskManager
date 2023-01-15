from sqlalchemy import create_engine
from models import Task, TaskTable
from sqlalchemy.orm import Session

engine = create_engine("sqlite:///base.sqlite3", echo=False)
session = Session(bind=engine)

def add_task (chat_id, date, task):
    task = Task(chat_id = chat_id, date=date, task=task)
    session.add(task)
    session.commit()

def get_day(chat_id, date):
    day = session.query(Task).filter(Task.chat_id==chat_id, Task.date==date).all()
    return(day)

def change_completed(chat_id, task_id):
    task = session.query(Task).filter(Task.chat_id==chat_id, Task.id==task_id).first()
    task.completed = not task.completed
    session.add(task)
    session.commit()

def delete_task(chat_id, task_id):
    task = session.query(Task).filter(Task.chat_id==chat_id, Task.id==task_id).first()
    session.delete(task)
    session.commit()

def set_message_id(chat_id, message_id):
    task_table = session.query(TaskTable).get(chat_id)
    if task_table is None:
        task_table = TaskTable(chat_id = chat_id)
    task_table.message_id = message_id
    session.add(task_table)
    session.commit()

def get_message_id(chat_id):
    task_table = session.query(TaskTable).get(chat_id)
    return task_table.message_id

def get_last_date(chat_id):
    date = session.query(Task).filter(Task.chat_id==chat_id).order_by(Task.date.desc()).first().date
    return date
