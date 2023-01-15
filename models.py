from sqlalchemy import Column
from sqlalchemy import Integer, String, Boolean, Date
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Task(Base):
    __tablename__ = "Tasks"

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    date = Column(Date)
    task = Column(String)
    completed = Column(Boolean, default=False)


class TaskTable(Base):
    __tablename__ = "TaskTables"

    chat_id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=True, default=None)

if __name__ == '__main__':
    engine = create_engine("sqlite:///base.sqlite3", echo=True)
    Base.metadata.create_all(engine)