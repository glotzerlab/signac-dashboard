#!/usr/bin/env python3

from flask import Flask, redirect, url_for, render_template, send_file
import jinja2
from flask_assets import Environment, Bundle

import os
import re

import signac
from signac import get_project
from collections import OrderedDict

class Dashboard():

    def __init__(self, config=None):
        self.app = self.create_app(config)

        if self.app.config['PROJECT_DIR'] is not None:
            self.project = get_project(self.app.config['PROJECT_DIR'])
        else:
            self.project = get_project()
        self.simplified_keys = self._simplified_keys()

        self.assets = self.create_assets()
        self.register_routes()

    def create_app(self, config=None):
        app = Flask('signac-dashboard')
        app.config.update(dict(
            PROJECT_DIR=None,
            DEBUG=True,
            SECRET_KEY=b'NlHFEbC89JkfGLC3Lpk8'
        ))
        app.config.update(config or {})
        app.config.from_envvar('SIGNAC_DASHBOARD_SETTINGS', silent=True)

        dashboard_path = os.path.dirname(__file__)
        app.static_folder = dashboard_path + '/static'
        app.template_folder = dashboard_path + '/templates'

        dashboard_paths = [dashboard_path]
        if 'DASHBOARD_DIR' in app.config:
            dashboard_paths.append(app.config.DASHBOARD_DIR)

        template_loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader((
                dashpath + '/templates' for dashpath in dashboard_paths
            )),
            app.jinja_loader
        ])
        app.jinja_loader = template_loader

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

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)

    def _simplified_keys(self):
        sps = list(self.project.find_statepoints())
        varied_keys = list()
        for key in sps[0]:
            same_for_all = True # This key has the same value for all statepoints
            for sp in sps:
                if sps[0][key] != sp[key]:
                    same_for_all = False
                    break
            if not same_for_all:
                varied_keys.append(key)
        return varied_keys


    def job_title(self, job, subtitle=False):
        jobid = str(job)
        sp = self.project.get_statepoint(jobid)
        title = ', '.join(list(('{}={}'.format(k, sp[k]) for k in self.simplified_keys)))
        #title = str('{} φ={:.2f} {} r={:.2f}'.format(sp['mode'], sp['phi'], get_shape_name(sp['shape_id']), sp['sphero_radius']))
        if subtitle:
            subtitle = jobid
            return title, subtitle
        else:
            return title

    def job_url(self, job):
        jobid = str(job)
        return url_for('show_job', jobid=jobid)

    def job_sorter(self, job):
        jobid = str(job)
        sp = self.project.get_statepoint(jobid)
        return str(jobid) #str('{} {:.2f} {}'.format(get_shape_name(sp['shape_id']), sp['phi'], sp['mode']))

    def is_figure(self, filename):
        _, ext = os.path.splitext(filename)
        return ext in ['.png', '.jpg', '.gif']

    def ellipsis_string(self, string, length=60):
        half = int(length/2)
        return string if len(string) < length else string[:half]+"..."+string[-half:]

    def register_routes(self):
        @self.app.context_processor
        def injections():
            sps = list(self.project.find_statepoints())
            injections = {
                'APP_NAME': 'signac-dashboard',
                'PROJECT_NAME': self.project.config['project'],
                'PROJECT_DIR': self.app.config['PROJECT_DIR'],
                'PROJECT_DIR_SHORT': self.ellipsis_string(self.app.config['PROJECT_DIR']),
                'statepoints': sps,
                'num_statepoints': len(sps),
            }
            return injections

        @self.app.route('/')
        def home():
            return redirect(url_for('dashboard'))

        @self.app.route('/dashboard')
        def dashboard():
            return render_template('dashboard.html')

        @self.app.route('/jobs/')
        def jobs_list():
            jobs = sorted(self.project.find_jobs(), key=lambda job: self.job_sorter(job))
            jobs_detailed = [{
                'id': str(j),
                'title': self.job_title(j),
                'url': self.job_url(j)} for j in jobs]
            return render_template('jobs.html', jobs=jobs_detailed)

        @self.app.route('/jobs/<jobid>')
        def show_job(jobid):
            sp = OrderedDict(sorted(self.project.get_statepoint(jobid).items(), key=lambda t: t[0]))
            job = self.project.open_job(id=jobid)
            job_files = os.listdir(job.workspace())
            files = list()
            for filename in job_files:
                files.append({
                    'name': filename,
                    'url': url_for('get_file', jobid=jobid, filename=filename)
                })
            figs = list(filter(lambda file: self.is_figure(file['name']), files))
            files = sorted(files, key=lambda file: file['name'])
            doc = OrderedDict(sorted(job.document.items(), key=lambda t: t[0]))
            jobtitle, jobsubtitle = self.job_title(job, subtitle=True)
            return render_template('job2.html', jobtitle=jobtitle, jobsubtitle=jobsubtitle, jobid=jobid, sp=sp, files=files, figs=figs, doc=doc)

        @self.app.route('/jobs/<jobid>/file/<filename>')
        def get_file(jobid, filename):
            job = self.project.open_job(id=jobid)
            if(job.isfile(filename)):
                # Return job-compress.o827643 and similar files as plain text
                print(filename)
                if(re.match('job-.*\.[oe][0-9]*',filename) is not None):
                    return send_file(job.fn(filename), mimetype='text/plain')
                else:
                    return send_file(job.fn(filename))
            else:
                return 'File not found.', 404
