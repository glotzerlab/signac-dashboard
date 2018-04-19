# Copyright (c) 2018 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.

from flask import session, redirect, request, url_for, send_file, flash, abort
import re


def home(dashboard):
    return redirect(url_for('jobs_list'))


def search(dashboard):
    query = request.args.get('q', None)
    jobs = []
    try:
        if request.method != 'GET':
            # Someday we may support search via POST, returning json
            raise NotImplementedError('Unsupported search method.')
        jobs = dashboard.job_search(query)
        if not jobs:
            flash('No jobs found for the provided query.', 'warning')
    except Exception as error:
        return dashboard._render_error(error)
    else:
        pagination = dashboard._setup_pagination(jobs)
        job_details = dashboard.get_job_details(
                pagination.paginate(jobs))
        title = 'Search: {}'.format(query)
        subtitle = pagination.item_counts()
        return dashboard._render_job_view(default_view='list',
                                          jobs=job_details,
                                          query=query,
                                          title=title,
                                          subtitle=subtitle,
                                          pagination=pagination)


def jobs_list(dashboard):
    jobs = dashboard.get_all_jobs()
    pagination = dashboard._setup_pagination(jobs)
    if not jobs:
        flash('No jobs found.', 'warning')
    job_details = dashboard.get_job_details(
            pagination.paginate(jobs))
    project_title = dashboard.project.config.get('project', None)
    title = '{}: Jobs'.format(
        project_title) if project_title else 'Jobs'
    subtitle = pagination.item_counts()
    return dashboard._render_job_view(default_view='list',
                                      jobs=job_details,
                                      title=title,
                                      subtitle=subtitle,
                                      pagination=pagination)


def show_job(dashboard, jobid):
    try:
        job = dashboard.project.open_job(id=jobid)
    except KeyError:
        abort(404, 'The job id requested could not be found.')
    else:
        job_details = dashboard.get_job_details([job])
        title = job_details[0]['title']
        subtitle = job_details[0]['subtitle']
        return dashboard._render_job_view(default_view='grid',
                                          jobs=job_details,
                                          title=title,
                                          subtitle=subtitle)


def get_file(dashboard, jobid, filename):
    try:
        job = dashboard.project.open_job(id=jobid)
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


def change_modules(dashboard):
    enabled_modules = set(session.get('enabled_modules', []))
    for i, module in enumerate(session.get('modules', [])):
        if request.form.get('modules[{}]'.format(i)) == 'on':
            enabled_modules.add(i)
        else:
            enabled_modules.discard(i)
    session['enabled_modules'] = list(enabled_modules)
    return redirect(request.form.get('redirect', url_for('home')))


def page_not_found(dashboard, error):
    return dashboard._render_error(str(error))
