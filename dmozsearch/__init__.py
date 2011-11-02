from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from dmozsearch.models import initialize_sql

from pyramid.view import view_config

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'dmozsearch:static', cache_max_age=3600)

    config.add_route('home', '/')
    config.add_view('dmozsearch.views.not_found_view', context='pyramid.httpexceptions.HTTPNotFound', renderer='404.jinja2')
    config.add_view('dmozsearch.views.search',
                    route_name='home',
                    renderer='search_page.jinja2')

    return config.make_wsgi_app()

