# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.

from flask import (
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from os.path import split

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
        return dashboard._render_job_view(default_view="list")


def jobs_list(dashboard):
    jobs = dashboard._get_all_jobs()
    g.pagination = dashboard._setup_pagination(jobs)
    if not jobs:
        flash("No jobs found.", "warning")
    g.jobs = dashboard._get_job_details(g.pagination.paginate(jobs))
    project_path = dashboard.project.config["project_dir"]
    _, project_folder = split(project_path)
    g.title = f"jobs of signac project in {project_path}"
    #g.title = f"{project_title}: Jobs" if project_title else "Jobs"
    g.subtitle = g.pagination.item_counts()
    return dashboard._render_job_view(default_view="list")


def project_info(dashboard):
    g.project = dashboard.project
    project_path = dashboard.project.config["project_dir"]
    _, project_folder = split(project_path)
    g.title = f"signac project in {project_folder}"
    num_jobs = len(dashboard.project)
    g.subtitle = f"{num_jobs} jobs"
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
        return dashboard._render_job_view(default_view="grid")


def get_file(dashboard, filename, jobid=None):
    if jobid is not None:
        try:
            job_or_project = dashboard.project.open_job(id=jobid)
        except KeyError:
            abort(404, "The job id requested could not be found.")
        except LookupError:
            dashboard.project.find_jobs()
            abort(404, "Multiple jobs match the requested job id.")
    else:
        job_or_project = dashboard.project
    if job_or_project.isfile(filename):
        directory = job_or_project.fn("")
        mimetype = None
        max_age = 0
        download_name = request.args.get("download_name", filename)
        return send_from_directory(
            directory=directory,
            path=filename,
            mimetype=mimetype,
            max_age=max_age,
            conditional=True,
            download_name=download_name,
        )
    else:
        abort(404, "The file requested does not exist.")


def change_modules(dashboard):
    enabled_module_indices = session.get(
        "enabled_module_indices", dashboard._setup_enabled_module_indices()
    )
    enabled_module_indices = {
        k: set(v) for k, v in enabled_module_indices.items()
    }  # remove duplicates
    context = session.get("context", "JobContext")

    for i, module in enumerate(dashboard._modules_by_context[context]):
        if request.form.get(f"modules[{i}]") == "on":
            enabled_module_indices[context].add(i)
        else:
            enabled_module_indices[context].discard(i)

    session["enabled_module_indices"] = {
        k: list(v) for k, v in enabled_module_indices.items()
    }
    return redirect(request.form.get("redirect", url_for("home")))


def settings(dashboard):
    g.active_page = "settings"
    return render_template("settings.html")


def page_not_found(dashboard, error):
    return dashboard._render_error(str(error))
