#!/usr/bin/env python
import time, sys, traceback
start = time.time()
from webapp.models import DirectoryEntry, initialize_sql
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import asc
import MySQLdb
from _mysql_exceptions import ProgrammingError

engine = engine_from_config({'sqlalchemy.url' : 'mysql+mysqldb://dmozsearch:dmozsearch@127.0.0.1:3306/dmozsearch?charset=utf8'}, 'sqlalchemy.', pool_size=10)
initialize_sql(engine)
Session = sessionmaker(bind=engine)
session = Session()

sphinx_cxn = MySQLdb.connect(port=9306, host='127.0.0.1', charset='utf8')
sphinx_cur = sphinx_cxn.cursor()
INDEX_NAME = 'directory_search_index'
ENCODING = 'utf8'

if __name__ == '__main__':
    print "starting up"
    query = session.query(DirectoryEntry).order_by(asc(DirectoryEntry.id))
    total = query.filter(DirectoryEntry.id > 0).count() # WHERE clause makes count faster

    print "entries to be indexed: %d items" % total
    offset = 0
    limit = 10000
    query = query.limit(limit)
    rt_query = u"REPLACE INTO %s VALUES " % INDEX_NAME

    while offset < total:

        now = time.time()
        seconds = now-start
        sys.stdout.write("\rprocessed %d records @ %d records/sec -- %d%% done"%(offset, offset/seconds, float(offset)*100/total))
        sys.stdout.flush()

        rs = query.offset(offset)
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
        
        insert_query = rt_query + u", ".join(entries)
        insert_query = insert_query.encode('ascii', 'replace')
        try:
            sphinx_cur.execute(insert_query)
        except ProgrammingError, e:
            print ''
            print insert_query
            traceback.print_exc()
            break
        offset += limit

    finish = time.time()
    seconds = finish-start
    print ''
    print "took %d seconds or %0.2f minutes or %0.2f hours" % (seconds, seconds/60, seconds/3600)
