#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
"""
This is an import script for dmoz data.
It does multiple passes on the file and its ugly.

But its a one-off... right?
"""
import time,sys
start = time.time()
from lxml import etree
from webapp.models import DirectoryEntry, initialize_sql, DBSession
from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

engine = engine_from_config({'sqlalchemy.url' : 'mysql://dmozsearch:dmozsearch@127.0.0.1:3306/dmozsearch?charset=utf8'}, 'sqlalchemy.', pool_size=10)
initialize_sql(engine)
Session = sessionmaker(bind=engine)
session = Session()

NS_DMOZ_URL = 'http://dmoz.org/rdf/'
NS_ELEM_URL = "http://purl.org/dc/elements/1.0/"
TAG_DIR_ENTRY = "{%s}ExternalPage" % NS_DMOZ_URL


root = etree.iterparse('./content.rdf.u8', tag=TAG_DIR_ENTRY, encoding='UTF-8')

if __name__ == '__main__':
    print "starting import"

    record_count = 0
    try:
        for action,elem in root:
            record_count += 1
            sys.stdout.write("\rrecord: %d"%record_count)
            sys.stdout.flush()

            try:
                url = unicode(elem.attrib.get('about', ''))
                title = unicode(elem.xpath('./d:Title[1]', namespaces={'d' : NS_ELEM_URL})[0].text)
                description = unicode(elem.xpath('./d:Description[1]', namespaces={'d' : NS_ELEM_URL})[0].text)
                topic_name = unicode(elem.xpath('./d:topic[1]', namespaces={'d' : NS_DMOZ_URL})[0].text)

                # verify if all is valid
                # if the url does not already exist, create it
                if url and title and description and topic_name:
                    try:
                        _ = session.query(DirectoryEntry).filter(DirectoryEntry.url == url).one()
                    except NoResultFound:
                        entry = DirectoryEntry(title, description, url, topic_name)
                        try:
                            session.add(entry)
                            session.commit()
                        except IntegrityError:
                            # duplicate url or something
                            session.rollback()
            except IndexError:
                pass

            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            del elem
    except etree.XMLSyntaxError, e:
        # some charactors not supported apparently.
        print ''
        print e

    finish = time.time()
    seconds = finish-start
    print ''
    print "took %d seconds or %0.2f minutes or %0.2f hours" % (seconds, seconds/60, seconds/3600)
