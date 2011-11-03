#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
import time, sys, traceback
start = time.time()
from webapp.models import DirectoryEntry, initialize_sql
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import asc
# I had to patch pymysql to work with sphinx. it expects more "mysql"-ness of sphinx than mysqldb
import pymysql
from pymysql.err import ProgrammingError
from gevent.pool import Pool

engine = engine_from_config({'sqlalchemy.url' : 'mysql+pymysql://dmozsearch:dmozsearch@127.0.0.1:3306/dmozsearch?charset=utf8'}, 'sqlalchemy.')
initialize_sql(engine)

RT_QUERY = u"REPLACE INTO directory_search_index VALUES "

pool = Pool(size=10)
TOTAL = 0
DONE = 0

def get_sphinx_conn(host='127.0.0.1', port=9306, charset='utf8'):
    cxn = pymysql.connect(port=9306, host='127.0.0.1', charset='utf8')
    cur = cxn.cursor()
    return (cxn, cur)

def get_mysql_session():
    Session = sessionmaker(bind=engine)
    return Session()

def mysql_dir_entry_query(session):
    return session.query(DirectoryEntry).order_by(asc(DirectoryEntry.id))

def mysql_fetch_entries(offset, limit):
    session = get_mysql_session()
    query = mysql_dir_entry_query(session)
    return (session, query.offset(offset).limit(limit))

def mysql_dir_entry_count():
    session = get_mysql_session()
    query = mysql_dir_entry_query(session)
    count = query.filter(DirectoryEntry.id > 0).count() # WHERE clause makes count faster
    session.close()
    return count

def sphinx_update_index(query):
    cxn, cur = get_sphinx_conn()
    try:
        cur.execute(query)
    except ProgrammingError, e:
        print ""
        print insert_query
        traceback.print_exc()
    cxn.close()

def report_progress():
    global DONE, TOTAL
    now = time.time()
    seconds = now-start
    sys.stdout.write("\rprocessed %d records @ %d records/sec -- %d%% done"%(DONE, DONE/seconds, float(DONE)*100/TOTAL))
    sys.stdout.flush()

def process_batch(offset, limit):
    session, rs = mysql_fetch_entries(offset, limit)
    entries = []
    for row in rs:
        entry_str = u"(%d,'%s','%s','%s','%s')" % (
                                                    row.id,
                                                    row.title.replace(u"\\", u"\\\\").replace(r"'", u"\\'"),
                                                    row.description.replace(u"\\", u"\\\\").replace(r"'", u"\\'"),
                                                    row.url.replace(u"\\", u"\\\\").replace(r"'", u"\\'"),
                                                    row.topic.replace(u"\\", u"\\\\").replace(r"'", u"\\'")
        )
        entries.append(entry_str)
    session.close()
    
    insert_query = RT_QUERY + u", ".join(entries)
    insert_query = insert_query.encode('ascii', 'replace')
    sphinx_update_index(insert_query)
    global DONE
    DONE += limit
    report_progress()

if __name__ == '__main__':
    print "starting up"
    total = mysql_dir_entry_count()
    TOTAL = total

    print "entries to be indexed: %d items" % total
    offset = 0
    limit = 10000

    report_progress()
    while offset < total:
        pool.spawn(process_batch, offset, limit)
        offset += limit
    pool.join()

    finish = time.time()
    seconds = finish-start
    print ''
    print "took %d seconds or %0.2f minutes or %0.2f hours" % (seconds, seconds/60, seconds/3600)
