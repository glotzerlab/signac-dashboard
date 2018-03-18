# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.
from flask import Flask, redirect, request, url_for, render_template, \
    send_file, flash, abort
from werkzeug import url_encode
import jinja2
from flask_assets import Environment, Bundle
from flask_cache import Cache
from flask_turbolinks import turbolinks
import os
import re
import logging
import shlex
from functools import lru_cache
import numbers
import json
import signac
from .pagination import Pagination

logger = logging.getLogger(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})
DEFAULT_CACHE_TIME = 60 * 5


class Dashboard:

    def __init__(self, config=None, project=None, modules=None):
        if config is None:
            config = {}
        config['PAGINATION'] = config.get('PAGINATION', True)
        config['PER_PAGE'] = config.get('PER_PAGE', 25)
        self.config = config
        self.app = self.create_app(config)

        cache.init_app(self.app)

        if modules is None:
            modules = []

        if project is None:
            self.project = signac.get_project()
        else:
            self.project = project

        # Try to update the project cache. Requires signac 0.9.2 or later.
        try:
            self.project.update_cache()
        except Exception:
            pass

        self.assets = self.create_assets()
        self.register_routes(self)

        self.modules = modules
        for module in self.modules:
            module.register_assets(self)
            module.register_routes(self)

    def create_app(self, config=None):
        app = Flask('signac-dashboard')
        app.config.update(dict(
            SECRET_KEY=b'NlHFEbC89JkfGLC3Lpk8'
        ))

        # Load the provided config
        app.config.update(config or {})

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
        # The paths in DASHBOARD_DIRS give the preferred order of template
        # loading
        loader_list = []
        for dashpath in list(app.config.get('DASHBOARD_PATHS', [])):
            logger.warning("Adding '{}' to dashboard paths.".format(dashpath))
            loader_list.append(
                jinja2.FileSystemLoader(dashpath + '/templates'))

        # The default loader goes last and is overridden by any custom paths
        loader_list.append(app.jinja_loader)

        app.jinja_loader = jinja2.ChoiceLoader(loader_list)

        # Add pagination support from http://flask.pocoo.org/snippets/44/
        def url_for_other_page(page):
            args = request.args.copy()
            args['page'] = page
            return url_for(request.endpoint, **args)
        app.jinja_env.globals['url_for_other_page'] = url_for_other_page

        turbolinks(app)

        return app

    def create_assets(self):
        assets = Environment(self.app)
        # JavaScript is combined into one file and minified
        js_all = Bundle('js/*.js', filters='jsmin', output='gen/app.min.js')
        # SCSS (Sassy CSS) is compiled to CSS and minified
        scss_all = Bundle('scss/app.scss',
                          filters='libsass,cssmin',
                          output='gen/app.min.css')
        assets.register('js_all', js_all)
        assets.register('scss_all', scss_all)
        return assets

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

    @cache.memoize(timeout=DEFAULT_CACHE_TIME)
    def _project_basic_index(self, include_job_document=False):
        index = []
        for item in self.project.index(
            include_job_document=include_job_document
        ):
            index.append(item)
        return index

    @cache.cached(timeout=DEFAULT_CACHE_TIME, key_prefix='_schema_variables')
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
            elif isinstance(num, numbers.Real):
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

    @cache.cached(timeout=DEFAULT_CACHE_TIME,
                  key_prefix='_project_min_len_unique_id')
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

    @cache.cached(timeout=DEFAULT_CACHE_TIME, key_prefix='get_all_jobs')
    def get_all_jobs(self):
        all_jobs = sorted(self.project.find_jobs(),
                          key=lambda job: self.job_sorter(job))
        return all_jobs

    @cache.memoize(timeout=DEFAULT_CACHE_TIME)
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
                    flash("Search string interpreted as '{}'.".format(f))
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
            'url': url_for('show_job', jobid=job._id)
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

    def register_routes(self, dashboard):
        @dashboard.app.context_processor
        def injections():
            injections = {
                'APP_NAME': 'signac-dashboard',
                'PROJECT_NAME': self.project.config['project'],
                'PROJECT_DIR': self.project.config['project_dir'],
                'modules': self.modules,
                'enabled_modules': [i for i in range(len(self.modules))
                                    if self.modules[i].is_enabled()]
            }
            return injections

        @dashboard.app.template_global()
        def modify_query(**new_values):
            args = request.args.copy()
            for key, value in new_values.items():
                args[key] = value
            return '{}?{}'.format(request.path, url_encode(args))

        @dashboard.app.route('/')
        def home():
            return redirect(url_for('jobs_list'))

        @dashboard.app.route('/search')
        def search():
            query = request.args.get('q', None)
            jobs = []
            try:
                if request.method != 'GET':
                    # Someday we may support search via POST, returning json
                    raise NotImplementedError('Unsupported search method.')
                jobs = self.job_search(query)
                if not jobs:
                    flash('No jobs found for the provided query.', 'warning')
            except Exception as error:
                return self._render_error(error)
            else:
                pagination = self._setup_pagination(jobs)
                job_details = self.get_job_details(
                        pagination.paginate(jobs))
                title = 'Search: {}'.format(query)
                subtitle = pagination.item_counts()
                return self._render_job_view(default_view='list',
                                             jobs=job_details,
                                             query=query,
                                             title=title,
                                             subtitle=subtitle,
                                             pagination=pagination)

        @dashboard.app.route('/jobs/')
        def jobs_list():
            jobs = self.get_all_jobs()
            pagination = self._setup_pagination(jobs)
            if not jobs:
                flash('No jobs found.', 'warning')
            job_details = self.get_job_details(
                    pagination.paginate(jobs))
            project_title = self.project.config.get('project', None)
            title = '{}: Jobs'.format(
                project_title) if project_title else 'Jobs'
            subtitle = pagination.item_counts()
            return self._render_job_view(default_view='list',
                                         jobs=job_details,
                                         title=title,
                                         subtitle=subtitle,
                                         pagination=pagination)

        @dashboard.app.route('/jobs/<jobid>')
        def show_job(jobid):
            try:
                job = self.project.open_job(id=jobid)
            except KeyError:
                abort(404, 'The job id requested could not be found.')
            else:
                job_details = self.get_job_details([job])
                title = job_details[0]['title']
                subtitle = job_details[0]['subtitle']
                return self._render_job_view(default_view='grid',
                                             jobs=job_details,
                                             title=title,
                                             subtitle=subtitle)

        @dashboard.app.route('/jobs/<jobid>/file/<filename>')
        def get_file(jobid, filename):
            try:
                job = self.project.open_job(id=jobid)
            except KeyError:
                abort(404, 'The job id requested could not be found.')
            else:
                if job.isfile(filename):
                    # Return job-compress.o827643 (and similar) as plaintext
                    textfile_regexes = ['job-.*\.[oe][0-9]*',
                                        '.*\.log',
                                        '.*\.dat']
                    for regex in textfile_regexes:
                        if re.match('job-.*\.[oe][0-9]*',
                                    filename) is not None:
                            return send_file(job.fn(filename),
                                             mimetype='text/plain')
                    return send_file(job.fn(filename))
                else:
                    abort(404, 'The file requested does not exist.')

        @dashboard.app.route('/modules', methods=['POST'])
        def change_modules():
            for i, module in enumerate(self.modules):
                if request.form.get('modules[{}]'.format(i)) == 'on':
                    module.enable()
                else:
                    module.disable()
            return redirect(request.form.get('redirect', url_for('home')))

        @dashboard.app.errorhandler(404)
        def page_not_found(error):
            return self._render_error(str(error))
