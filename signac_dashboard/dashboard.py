from flask import Flask, redirect, request, url_for, render_template, send_file
import jinja2
from flask_assets import Environment, Bundle
from flask_cache import Cache
from flask_turbolinks import turbolinks
import os
import re
import json
import logging
import signac
from collections import OrderedDict
from .util import *

logger = logging.getLogger(__name__)
cache = Cache(config={'CACHE_TYPE': 'simple'})

class Dashboard():

    def __init__(self, config=None, project=None, modules=None):
        self.app = self.create_app(config)
        cache.init_app(self.app)

        if project:
            self.project = project
        else:
            self.project = signac.get_project()

        self.modules = modules

        self.assets = self.create_assets()
        self.register_routes()

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

        # Set up signac-dashboard static and template paths
        dashboard_path = os.path.dirname(__file__)
        app.static_folder = dashboard_path + '/static'
        app.template_folder = dashboard_path + '/templates'

        # Set up custom template paths
        dashboard_paths = [dashboard_path]
        for custom_path in list(app.config.get('DASHBOARD_DIRS', [])):
            dashboard_paths.append(custom_path)
        template_loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(
                (dashpath + '/templates' for dashpath in dashboard_paths)
            ),
            app.jinja_loader
        ])
        app.jinja_loader = template_loader

        turbolinks(app)

        return app

    def create_assets(self):
        assets = Environment(self.app)
        # JavaScript is combined into one file and minified
        js_all = Bundle('js/*.js', filters='jsmin', output='gen/app.min.js')
        # SCSS (Sassy CSS) is compiled to CSS and minified
        scss_all = Bundle('scss/app.scss', filters='libsass,cssmin', output='gen/app.min.css')
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


    def job_title(self, job):
        # Overload this method with a function that returns
        # a human-readable form of the job title.
        return str(job)

    def job_subtitle(self, job):
        # Overload this method with a function that returns
        # a human-readable form of the job subtitle.
        return str(job)

    def job_sorter(self, job):
        # Overload this method to return a value that
        # can be used as a sorting index.
        return self.job_title(job)

    @cache.cached(timeout=60*5, key_prefix='all_jobs')
    def get_all_jobs(self):
        all_jobs = sorted(self.project.find_jobs(), key=lambda job: self.job_sorter(job))
        print(all_jobs)
        return all_jobs

    def job_search(self, query):
        f = signac.contrib.filterparse._parse_json(query)
        print('Filter: {}'.format(f))
        return self.project.find_job_ids(filter=f)

    def register_routes(self):
        @self.app.context_processor
        def injections():
            injections = {
                'APP_NAME': 'signac-dashboard',
                'PROJECT_NAME': self.project.config['project'],
                'PROJECT_DIR': self.project.config['project_dir'],
                'PROJECT_DIR_SHORT': ellipsis_string(self.project.config['project_dir'], length=60)
            }
            return injections

        @self.app.route('/')
        def home():
            return redirect(url_for('dashboard'))

        @self.app.route('/dashboard')
        def dashboard():
            return render_template('dashboard.html')

        @self.app.route('/search')
        def search():
            json_query = request.args.get('q', None)
            try:
                if request.method != 'GET':
                    raise NotImplementedError('Unsupported search method.')
                if json_query is None:
                    raise ValueError('No search query provided.')
                query = json.loads(json_query)
                jobs = self.job_search(query)
                return str(jobs)
            except Exception as e:
                return 'Invalid search: {}'.format(e)

        @self.app.route('/jobs/')
        def jobs_list():
            jobs = self.get_all_jobs()
            jobs_detailed = [{
                'title': self.job_title(job),
                'subtitle': self.job_subtitle(job),
                'labels': job.document['stages'] if 'stages' in job.document else [],
                'url': url_for('show_job', jobid=str(job))} for job in jobs]
            return render_template('jobs.html', jobs=jobs_detailed)

        @self.app.route('/jobs/<jobid>')
        def show_job(jobid):
            job = self.project.open_job(id=jobid)
            jobtitle = self.job_title(job)
            jobsubtitle = self.job_subtitle(job)
            return render_template('job.html', modules=self.modules, job=job, jobtitle=jobtitle, jobsubtitle=jobsubtitle)

        @self.app.route('/jobs/<jobid>/file/<filename>')
        def get_file(jobid, filename):
            job = self.project.open_job(id=jobid)
            if(job.isfile(filename)):
                # Return job-compress.o827643 and similar files as plain text
                textfile_regexes = ['job-.*\.[oe][0-9]*', '.*\.log', '.*\.dat']
                for regex in textfile_regexes:
                    if(re.match('job-.*\.[oe][0-9]*',filename) is not None):
                        return send_file(job.fn(filename), mimetype='text/plain')
                return send_file(job.fn(filename))
            else:
                return 'File not found.', 404
