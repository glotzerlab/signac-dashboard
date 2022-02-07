# Copyright (c) 2019 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.

import re

from flask import (
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)


def home(dashboard):
    return redirect(url_for("project_info"))


def search(dashboard):
    g.query = request.args.get("q", None)
    jobs = []
    try:
        if request.method != "GET":
            # Someday we may support search via POST, returning json
            raise NotImplementedError("Unsupported search method.")
        jobs = dashboard._job_search(g.query)
        if not jobs:
            flash("No jobs found for the provided query.", "warning")
    except Exception as error:
        return dashboard._render_error(error)
    else:
        g.pagination = dashboard._setup_pagination(jobs)
        g.jobs = dashboard._get_job_details(g.pagination.paginate(jobs))
        g.title = f"Search: {g.query}"
        g.subtitle = g.pagination.item_counts()
        session["context"] = "JobContext"
        return dashboard._render_job_view(default_view="list")


def jobs_list(dashboard):
    jobs = dashboard._get_all_jobs()
    g.pagination = dashboard._setup_pagination(jobs)
    if not jobs:
        flash("No jobs found.", "warning")
    g.jobs = dashboard._get_job_details(g.pagination.paginate(jobs))
    project_title = dashboard.project.config.get("project", None)
    g.title = f"{project_title}: Jobs" if project_title else "Jobs"
    g.subtitle = g.pagination.item_counts()
    session["context"] = "JobContext"
    return dashboard._render_job_view(default_view="list")


def project_info(dashboard):
    g.project = dashboard.project
    project_title = dashboard.project.config["project"]
    schema_version = dashboard.project.config["schema_version"]
    project_dir = dashboard.project.config["project_dir"]
    g.title = f"{project_title} - schema version {schema_version}"
    g.subtitle = f"Project directory: {project_dir}"
    session["context"] = "ProjectContext"
    return dashboard._render_project_view()


def show_job(dashboard, jobid):
    try:
        job = dashboard.project.open_job(id=jobid)
    except KeyError:
        abort(404, "The job id requested could not be found.")
    else:
        g.jobs = dashboard._get_job_details([job])
        g.title = g.jobs[0]["title"]
        g.subtitle = g.jobs[0]["subtitle"]
        session["context"] = "JobContext"
        return dashboard._render_job_view(default_view="grid")


def get_file(dashboard, jobid, filename):
    try:
        job = dashboard.project.open_job(id=jobid)
    except KeyError:
        abort(404, "The job id requested could not be found.")
    else:
        if job.isfile(filename):
            mimetype = None
            cache_timeout = 0
            # Return logs as plaintext
            textfile_regexes = ["job-.*\\.[oe][0-9]*", ".*\\.log", ".*\\.dat"]
            for regex in textfile_regexes:
                if re.match(regex, filename) is not None:
                    mimetype = "text/plain"
            return send_file(
                job.fn(filename),
                mimetype=mimetype,
                cache_timeout=cache_timeout,
                conditional=True,
            )
        else:
            abort(404, "The file requested does not exist.")

def get_project_file(dashboard, filename):
    if dashboard.project.isfile(filename):
        mimetype = None
        cache_timeout = 0
        # Return logs as plaintext
        textfile_regexes = ["job-.*\\.[oe][0-9]*", ".*\\.log", ".*\\.dat"]
        for regex in textfile_regexes:
            if re.match(regex, filename) is not None:
                mimetype = "text/plain"
        return send_file(
            dashboard.project.fn(filename),
            mimetype=mimetype,
            cache_timeout=cache_timeout,
            conditional=True,
        )
    else:
        abort(404, "The file requested does not exist.")

def change_modules(dashboard):
    enabled_modules = set(session.get("enabled_modules", []))
    context = session.get("context")
    for i, module in enumerate(dashboard.modules):
        if module.context == context:
            if request.form.get(f"modules[{i}]") == "on":
                enabled_modules.add(i)
            else:
                enabled_modules.discard(i)
    session["enabled_modules"] = list(enabled_modules)
    return redirect(request.form.get("redirect", url_for("home")))


def settings(dashboard):
    g.active_page = "settings"
    return render_template("settings.html")


def page_not_found(dashboard, error):
    return dashboard._render_error(str(error))
