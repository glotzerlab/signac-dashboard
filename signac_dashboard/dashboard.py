# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.

from flask import Flask, session, request, url_for, render_template, flash, g
from werkzeug import url_encode
import jinja2
from flask_assets import Environment, Bundle
from flask_turbolinks import turbolinks
import os
import sys
import logging
import warnings
import shlex
import argparse
from importlib import import_module
from functools import lru_cache
from numbers import Real
import json
import signac

from .version import __version__
from .module import ModuleEncoder
from .pagination import Pagination
from .util import LazyView

logger = logging.getLogger(__name__)


class Dashboard:

    def __init__(self, config={}, project=None, modules=[]):
        if project is None:
            self.project = signac.get_project()
        else:
            self.project = project

        try:
            # This dashboard document is read-only
            dash_doc = self.project.document.dashboard()
        except AttributeError:
            dash_doc = {}
        self.config = config or dash_doc.get('config', {})
        self.modules = modules or Dashboard.decode_modules(
            dash_doc.get('module_views', {}).get('Default', []))

        # Try to update the project cache. Requires signac 0.9.2 or later.
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            try:
                self.project.update_cache()
            except Exception:
                pass

    @classmethod
    def encode_modules(cls, modules, target='dict'):
        json_modules = json.dumps(modules, cls=ModuleEncoder,
                                  sort_keys=True, indent=4)
        if target == 'json':
            return json_modules
        else:
            return json.loads(json_modules)

    @property
    def encoded_modules(self):
        return Dashboard.encode_modules(self.modules)

    @classmethod
    def decode_modules(cls, json_modules, enabled_modules=None):
        modules = []
        if type(json_modules) == str:
            json_modules = json.loads(json_modules)
        logger.info("Loading modules: {}".format(json_modules))
        if enabled_modules is None:
            enabled_modules = list(range(len(json_modules)))
        for i, module in enumerate(json_modules):
            if type(module) == dict and \
                    '_module' in module and \
                    '_moduletype' in module:
                try:
                    _module = module['_module']
                    _moduletype = module['_moduletype']
                    modulecls = getattr(import_module(_module), _moduletype)
                    module = modulecls(
                        **{k: v for k, v in module.items()
                           if not k.startswith('_')})
                    if i in enabled_modules:
                        module.enable()
                    else:
                        module.disable()
                    modules.append(module)
                except Exception as e:
                    logger.error(e)
                    logger.warning('Could not import module:', module)
        return modules

    def create_app(self, config={}):
        app = Flask('signac-dashboard')
        app.config.update({
            'SECRET_KEY': os.urandom(24),
            'SEND_FILE_MAX_AGE_DEFAULT': 300,  # Cache control for static files
        })

        # Load the provided config
        app.config.update(config)

        # Enable profiling
        if app.config.get('PROFILE'):
            logger.warning("Application profiling is enabled.")
            from werkzeug.contrib.profiler import ProfilerMiddleware
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[10])

        # Set up default signac-dashboard static and template paths
        signac_dashboard_path = os.path.dirname(__file__)
        app.static_folder = signac_dashboard_path + '/static'
        app.template_folder = signac_dashboard_path + '/templates'

        # Set up custom template paths
        # The paths in DASHBOARD_PATHS give the preferred order of template
        # loading
        loader_list = []
        for dashpath in list(app.config.get('DASHBOARD_PATHS', [])):
            logger.warning("Adding '{}' to dashboard paths.".format(dashpath))
            loader_list.append(
                jinja2.FileSystemLoader(dashpath + '/templates'))

        # The default loader goes last and is overridden by any custom paths
        loader_list.append(app.jinja_loader)

        app.jinja_loader = jinja2.ChoiceLoader(loader_list)

        turbolinks(app)

        return app

    def create_assets(self):
        assets = Environment(self.app)
        # jQuery is served as a standalone file
        jquery = Bundle('js/jquery-*.min.js', output='gen/jquery.min.js')
        # JavaScript is combined into one file and minified
        js_all = Bundle('js/js_all/*.js',
                        filters='jsmin',
                        output='gen/app.min.js')
        # SCSS (Sassy CSS) is compiled to CSS and minified
        scss_all = Bundle('scss/app.scss',
                          filters='libsass,cssmin',
                          output='gen/app.min.css')
        assets.register('jquery', jquery)
        assets.register('js_all', js_all)
        assets.register('scss_all', scss_all)
        return assets

    def register_module_asset(self, asset):
        self.module_assets.append(asset)

    def prepare(self):
        # Set configuration defaults and save to the project document
        self.config.setdefault('PAGINATION', True)
        self.config.setdefault('PER_PAGE', 25)

        self.project.document.setdefault('dashboard', {})

        # This dash_doc is synced to the project document
        dash_doc = self.project.document.dashboard
        dash_doc.setdefault('config', self.config)
        dash_doc.setdefault('module_views', {})

        # Set the Default module view to the modules provided by the user
        dash_doc['module_views']['Default'] = self.encoded_modules

        self.app = self.create_app(self.config)

        self.assets = self.create_assets()
        self.register_routes()

        self.module_assets = []
        for module in self.modules:
            try:
                module.register_assets(self)
                module.register_routes(self)
            except Exception as e:
                logger.error('Error while registering {} module: {}'.format(
                    module.name, e))
                logger.error('Removing module {} from dashboard.'.format(
                    module.name))
                self.modules.remove(module)

    def run(self, host='localhost', port=8888, *args, **kwargs):

        max_retries = 5
        for _ in range(max_retries):
            try:
                self.app.run(host, port, *args, **kwargs)
                break
            except OSError as e:
                logger.warning(e)
                if port:
                    port += 1
                pass

    @lru_cache()
    def _project_basic_index(self, include_job_document=False):
        index = []
        for item in self.project.index(
            include_job_document=include_job_document
        ):
            index.append(item)
        return index

    @lru_cache()
    def _schema_variables(self):
        _index = self._project_basic_index()
        sp_index = self.project.build_job_statepoint_index(
            exclude_const=True, index=_index)
        schema_variables = []
        for keys, _ in sp_index:
            schema_variables.append(keys)
        return schema_variables

    def job_title(self, job):
        # Overload this method with a function that returns
        # a human-readable form of the job title.

        def _format_num(num):
            if isinstance(num, bool):
                return str(num)
            elif isinstance(num, Real):
                return str(round(num, 2))
            return str(num)

        try:
            s = []
            for keys in sorted(self._schema_variables()):
                v = job.statepoint()[keys[0]]
                try:
                    for key in keys[1:]:
                        v = v[key]
                except KeyError:  # Particular key is present in overall
                    continue      # schema, but not this state point.
                else:
                    s.append('{}={}'.format('.'.join(keys), _format_num(v)))
            return ' '.join(s)
        except Exception as error:
            logger.warning(
                "Error while generating job title: '{}'. "
                "Returning job-id as fallback.".format(error))
            return str(job)

    @lru_cache()
    def _project_min_len_unique_id(self):
        return self.project.min_len_unique_id()

    def job_subtitle(self, job):
        # Overload this method with a function that returns
        # a human-readable form of the job subtitle.
        return str(job)[:max(8, self._project_min_len_unique_id())]

    def job_sorter(self, job):
        # Overload this method to return a value that
        # can be used as a sorting index.
        return self.job_title(job)

    @lru_cache()
    def get_all_jobs(self):
        all_jobs = sorted(self.project.find_jobs(),
                          key=lambda job: self.job_sorter(job))
        return all_jobs

    @lru_cache(maxsize=100)
    def job_search(self, query):
        querytype = 'statepoint'
        if query[:4] == 'doc:':
            query = query[4:]
            querytype = 'document'

        try:
            if query is None:
                f = None
            else:
                try:
                    f = json.loads(query)
                except json.JSONDecodeError as error:
                    query = shlex.split(query)
                    f = signac.contrib.filterparse.parse_filter_arg(query)
                    flash("Search string interpreted as '{}'.".format(
                        json.dumps(f)))
            if querytype == 'document':
                jobs = self.project.find_jobs(doc_filter=f)
            else:
                jobs = self.project.find_jobs(filter=f)
            return sorted(jobs, key=lambda job: self.job_sorter(job))
        except json.JSONDecodeError as error:
            flash('Failed to parse query argument. '
                  'Ensure that \'{}\' is valid JSON!'.format(query),
                  'warning')
            raise error

    @lru_cache(maxsize=65536)
    def _job_details(self, job, show_labels=False):
        return {
            'job': job,
            'title': self.job_title(job),
            'subtitle': self.job_subtitle(job),
            'labels': job.document['stages']
            if show_labels and 'stages' in job.document else [],
        }

    def _setup_pagination(self, jobs):
        total_count = len(jobs) if isinstance(jobs, list) else 0
        try:
            page = int(request.args.get('page', 1))
            assert page >= 1
        except Exception as e:
            flash('Pagination Error. Defaulting to page 1.', 'danger')
            page = 1
        pagination = Pagination(page, self.config['PER_PAGE'], total_count)
        try:
            assert page <= pagination.pages
        except Exception as e:
            page = pagination.pages
            flash('Pagination Error. Displaying page {}.'.format(page),
                  'danger')
            pagination = Pagination(
                    page, self.config['PER_PAGE'], total_count)
        return pagination

    def _render_job_view(self, *args, **kwargs):
        g.active_page = 'jobs'
        view_mode = request.args.get('view', kwargs.get(
            'default_view', 'list'))
        if view_mode == 'grid':
            return render_template('jobs_grid.html', *args, **kwargs)
        elif view_mode == 'list':
            return render_template('jobs_list.html', *args, **kwargs)
        else:
            return self._render_error(
                    ValueError('Invalid view mode: {}'.format(view_mode)))

    def _render_error(self, error):
        if isinstance(error, Exception):
            error_string = "{}: {}".format(type(error).__name__, error)
            logger.error(error_string)
            flash(error_string, 'danger')
        else:
            logger.error(error)
            flash(error, 'danger')
        return render_template('error.html')

    def get_job_details(self, jobs):
        show_labels = self.config.get('labels', False)
        return [self._job_details(job, show_labels) for job in list(jobs)]

    def url(self, import_name, url_rules=[], import_file='signac_dashboard',
            **options):
        if import_file is not None:
            import_name = import_file + '.' + import_name
        view = LazyView(dashboard=self,
                        import_name=import_name)
        for url_rule in url_rules:
            self.app.add_url_rule(url_rule, view_func=view, **options)

    def register_routes(self):
        dashboard = self

        @dashboard.app.after_request
        def prevent_caching(response):
            if 'Cache-Control' not in response.headers:
                response.headers['Cache-Control'] = 'no-store'
            return response

        @dashboard.app.context_processor
        def injections():
            session.setdefault('modules', self.encoded_modules)
            session.setdefault('enabled_modules',
                               [i for i in range(len(self.modules))
                                if self.modules[i].enabled])
            return {
                'APP_NAME': 'signac-dashboard',
                'APP_VERSION': __version__,
                'PROJECT_NAME': self.project.config['project'],
                'PROJECT_DIR': self.project.config['project_dir'],
                'modules': Dashboard.decode_modules(
                    session['modules'], session['enabled_modules']),
                'enabled_modules': session['enabled_modules'],
                'module_assets': self.module_assets
            }

        # Add pagination support from http://flask.pocoo.org/snippets/44/
        @dashboard.app.template_global()
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for(request.endpoint, **args)

        @dashboard.app.template_global()
        def modify_query(**new_values):
            args = request.args.copy()
            for key, value in new_values.items():
                args[key] = value
            return '{}?{}'.format(request.path, url_encode(args))

        @dashboard.app.errorhandler(404)
        def page_not_found(error):
            return self._render_error(str(error))

        self.url('views.home', ['/'])
        self.url('views.settings', ['/settings'])
        self.url('views.search', ['/search'])
        self.url('views.jobs_list', ['/jobs/'])
        self.url('views.show_job', ['/jobs/<jobid>'])
        self.url('views.get_file', ['/jobs/<jobid>/file/<filename>'])
        self.url('views.change_modules', ['/modules'], methods=['POST'])

    def main(self):
        """Call this function to use the dashboard command line interface."""

        def _run(args):
            kwargs = vars(args)
            host = kwargs.pop('host')
            port = kwargs.pop('port')
            self.config['PROFILE'] = kwargs.pop('profile')
            self.config['DEBUG'] = kwargs.pop('debug')
            self.prepare()
            self.run(host=host, port=port)

        parser = argparse.ArgumentParser(
            description="signac-dashboard is a web-based data visualization "
                        "and analysis tool, part of the signac framework.")
        parser.add_argument(
            '--debug',
            action='store_true',
            help="Show traceback on error for debugging.")
        parser.add_argument(
            '--version',
            action='store_true',
            help="Display the version number and exit.")
        subparsers = parser.add_subparsers()

        parser_run = subparsers.add_parser('run')
        parser_run.add_argument(
            '-p', '--profile',
            action='store_true',
            help='Enable flask performance profiling.')
        parser_run.add_argument(
            '-d', '--debug',
            action='store_true',
            help='Enable flask debug mode.')
        parser_run.add_argument(
            '--host', type=str,
            default='localhost',
            help='Host (binding address). Default: localhost')
        parser_run.add_argument(
            '--port', type=int,
            default=8888,
            help='Port to listen on. Default: 8888')
        parser_run.set_defaults(func=_run)

        # This is a hack, as argparse itself does not
        # allow to parse only --version without any
        # of the other required arguments.
        if '--version' in sys.argv:
            print('signac-dashboard', __version__)
            sys.exit(0)

        args = parser.parse_args()

        if args.debug:
            logger.setLevel(logging.DEBUG)

        if not hasattr(args, 'func'):
            parser.print_usage()
            sys.exit(2)
        try:
            args.func(args)
        except KeyboardInterrupt:
            logger.error("Interrupted.")
            if args.debug:
                raise
            sys.exit(1)
        except RuntimeWarning as warning:
            logger.warning("Warning: {}".format(warning))
            if args.debug:
                raise
            sys.exit(1)
        except Exception as error:
            logger.error('Error: {}'.format(error))
            if args.debug:
                raise
            sys.exit(1)
        else:
            sys.exit(0)
