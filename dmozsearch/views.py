from dmozsearch.models import DBSession
from dmozsearch.models import DirectoryEntry, DirectorySearchIndex
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPNotFound

@view_config(renderer='search_page.jinja2')
def search(request):
    if request.method == 'POST':
        request.charset = 'utf8'
        params = request.POST
        query_str = params.get('q', None)
        if query_str:
            dbsession = DBSession()
            q = dbsession.query(DirectoryEntry).join(DirectorySearchIndex, DirectoryEntry.id==DirectorySearchIndex.id).filter(DirectorySearchIndex.query==query_str)
            return {"results" : q, "query_str": query_str}

    return {}

def not_found_view(request):
    return {}
