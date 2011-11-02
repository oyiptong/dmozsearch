import transaction

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import UnicodeText
from sqlalchemy import ForeignKey

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import mysql

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class DirectoryEntry(Base):
    __tablename__ = 'directory_entry'
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)
    title = Column(UnicodeText)
    description = Column(UnicodeText)
    url = Column(Unicode(255), unique=True)
    topic = Column(UnicodeText)

    def __init__(self, title, description, url, topic):
        self.title = title
        self.description = description
        self.url = url
        self.topic = topic

class DirectorySearchIndex(Base):
    __tablename__ = 'dmoz_sphinxse'
    __table_args = {'mysql_engine': 'sphinx'}

    id = Column(mysql.INTEGER(unsigned=True), primary_key=True, nullable=False)
    weight = Column(Integer, nullable=False)
    query = Column(Unicode(3072), nullable=False)
    title = Column(Unicode(3072))
    description = Column(Unicode(3072))
    url = Column(Unicode(255))
    topic = Column(Unicode(3072))

    def __init__(self, title, description, url, topic):
        self.title = title
        self.description = description
        self.url = url
        self.topic = topic

def populate():
    # seed data
    pass

def initialize_sql(engine):
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all(engine)
    try:
        populate()
    except IntegrityError:
        transaction.abort()
