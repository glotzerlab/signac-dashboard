# Copyright (c) 2022 The Regents of the University of Michigan
# All rights reserved.
# This software is licensed under the BSD 3-Clause License.

import argparse
import inspect
import json
import logging
import os
import secrets
import shlex
import sys
import warnings
from functools import lru_cache
from itertools import groupby
from numbers import Real

import flask_login
import jinja2
import natsort
import signac
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_assets import Bundle, Environment
from flask_turbolinks import turbolinks
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from werkzeug.urls import url_encode

from .pagination import Pagination
from .util import LazyView
from .version import __version__

logger = logging.getLogger(__name__)


class _FileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, dashboard):
        self.dashboard = dashboard

    def on_modified(self, event):
        if os.path.realpath(event.src_path) == os.path.realpath(
            self.dashboard.project.workspace
        ):
            self.dashboard.update_cache()


class User(flask_login.UserMixin):
    """User class for flask_login.

    The default implementation of `UserMixin` assumes that all instantiated User
    classes are active and logged in.
    """

    def __init__(self, id):
        self.id = id


class Dashboard:
    """A dashboard application to display a :py:class:`signac.Project`.

    The Dashboard class is designed to be used as a base class for a child
    class such as :code:`MyDashboard` which can be customized and launched via
    its command line interface (CLI). The CLI is invoked by calling
    :py:meth:`.main` on an instance of this class.

    **Configuration options:** The :code:`config` dictionary recognizes the
    following options:

    - **HOST**: Sets binding address (default: localhost).
    - **PORT**: Sets port to listen on (default: 8888).
    - **DEBUG**: Enables debug mode if :code:`True` (default: :code:`False`).
    - **PROFILE**: Enables the profiler
      :py:class:`werkzeug.middleware.profiler.ProfilerMiddleware` if
      :code:`True` (default: :code:`False`).
    - **PER_PAGE**: Maximum number of jobs to show per page
      (default: 25).
    - **CARDS_PER_ROW**: Cards to show per row in the desktop view. Must be a
      factor of 12 (default: 3).
    - **ACCESS_TOKEN**: The access token required to login to the dashboard.
      Set to :code:`None` to disable authentication (not recommended on multi-user
      systems).
    - **SECRET_KEY**: This must be specified to run via WSGI with multiple
      workers, so that sessions remain intact. See the
      `Flask docs <http://flask.pocoo.org/docs/1.0/config/#SECRET_KEY>`_
      for more information.
    - **ALLOW_WHERE**: If True, search queries can include :code:`$where`
      statements, which potentially allows arbitrary code execution from user
      input. *Caution:* This should only be enabled in trusted environments,
      never on a publicly-accessible server (default: :code:`False`).

    :param config: Configuration dictionary (default: :code:`{}`).
    :type config: dict
    :param project: signac project (default: :code:`None`, autodetected).
    :type project: :py:class:`signac.Project`
    :param modules: List of :py:class:`~.Module` instances to display.
    :type modules: list
    """

    def __init__(self, config={}, project=None, modules=[]):
        if project is None:
            self.project = signac.get_project()
        else:
            self.project = project

        self.config = config
        self.modules = modules

        self.event_handler = _FileSystemEventHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.project.workspace)

        # Prepare this dashboard instance to run.

        # Set configuration defaults
        self.config.setdefault("HOST", "localhost")
        self.config.setdefault("DEBUG", False)
        self.config.setdefault("PORT", 8888)
        self.config.setdefault("PAGINATION", True)
        self.config.setdefault("PER_PAGE", 25)
        self.config.setdefault("CARDS_PER_ROW", 3)
        if 12 % self.config["CARDS_PER_ROW"] != 0:
            raise ValueError(
                "The value of CARDS_PER_ROW must be a factor of 12. Got "
                f"{self.config['CARDS_PER_ROW']}."
            )

        self.config.setdefault("ACCESS_TOKEN", secrets.token_urlsafe())

        # Create and configure the Flask application
        self.app = self._create_app(self.config)

        # Initialize the login manager
        self.login_manager = flask_login.LoginManager()
        self.login_manager.init_app(self.app)

        @self.login_manager.user_loader
        def user_loader(identifier):
            if self.config["ACCESS_TOKEN"] is None:
                return User("None")

            if secrets.compare_digest(identifier, self.config["ACCESS_TOKEN"]):
                return User(identifier)

            return None

        @self.login_manager.request_loader
        def load_user_from_request(request):
            if self.config["ACCESS_TOKEN"] is None:
                return User("None")

            return None

        # Add assets and routes
        self.assets = self._create_assets()
        self._register_routes()

        # Add module assets and routes
        self._module_assets = []
        for module in self.modules:
            try:
                module.register(self)
            except Exception as e:
                logger.error(f"Error while registering {module.name} module: {e}")
                logger.error(f"Removing module {module.name} from dashboard.")
                self.modules.remove(module)

        # Clear dashboard and project caches.
        self.update_cache()

        # Group modules to track enabled state
        def keyfunc(module):
            return module.context

        grouped = groupby(sorted(self.modules, key=keyfunc), key=keyfunc)
        modules_by_context = {}
        for context_key, context_group in grouped:
            modules_by_context[context_key] = [m for m in context_group]
        self._modules_by_context = modules_by_context

    def _create_app(self, config={}):
        """Creates a Flask application.

        :param config: Dictionary of configuration parameters.
        """
        app = Flask("signac-dashboard")
        app.config.update(
            {
                "SECRET_KEY": os.urandom(24),
                "SEND_FILE_MAX_AGE_DEFAULT": 300,  # Cache control for static files
            }
        )

        # Load the provided config
        app.config.update(config)

        # Enable profiling
        if app.config.get("PROFILE"):
            logger.warning("Application profiling is enabled.")
            from werkzeug.contrib.profiler import ProfilerMiddleware

            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[10])

        # Set up default signac-dashboard static and template paths
        signac_dashboard_path = os.path.dirname(__file__)
        app.static_folder = signac_dashboard_path + "/static"
        app.template_folder = signac_dashboard_path + "/templates"

        # Set up custom template paths
        # The paths in DASHBOARD_PATHS give the preferred order of template
        # loading
        loader_list = []
        for dash_path in list(app.config.get("DASHBOARD_PATHS", [])):
            logger.warning(f"Adding '{dash_path}' to dashboard paths.")
            loader_list.append(jinja2.FileSystemLoader(dash_path + "/templates"))

        # The default loader goes last and is overridden by any custom paths
        loader_list.append(app.jinja_loader)

        app.jinja_loader = jinja2.ChoiceLoader(loader_list)

        turbolinks(app)

        return app

    def _create_assets(self):
        """Add assets for inclusion in the dashboard HTML."""

        assets = Environment(self.app)
        # jQuery is served as a standalone file
        jquery = Bundle("js/jquery-*.min.js", output="gen/jquery.min.js")
        # JavaScript is combined into one file and minified
        js_all = Bundle("js/js_all/*.js", filters="jsmin", output="gen/app.min.js")
        # SCSS (Sassy CSS) is compiled to CSS
        scss_all = Bundle("scss/app.scss", filters="libsass", output="gen/app.css")
        assets.register("jquery", jquery)
        assets.register("js_all", js_all)
        assets.register("scss_all", scss_all)
        return assets

    def register_module_asset(self, asset):
        """Register an asset required by a dashboard module.

        Some modules require special scripts or stylesheets, like the
        :py:class:`signac_dashboard.modules.Notes` module. It is recommended to
        use a namespace for each module that matches the example below:

        .. code-block:: python

            dashboard.register_module_asset({
                'file': 'templates/my-module/js/my-script.js',
                'url': '/module/my-module/js/my-script.js'
            })

        :param asset: A dictionary with keys :code:`'file'` and :code:`'url'`.
        :type asset: dict
        """
        self._module_assets.append(asset)

    def run(self, *args, **kwargs):
        """Runs the dashboard webserver.

        Use :py:meth:`~.main` instead of this method for the command-line
        interface. Arguments to this function are passed directly to
        :py:meth:`flask.Flask.run`.
        """
        host = self.config["HOST"]
        port = self.config["PORT"]
        debug = self.config["DEBUG"]
        max_retries = 5

        for _ in range(max_retries):
            try:
                self.app.run(host=host, port=port, debug=debug, *args, **kwargs)
                break
            except OSError as e:
                logger.warning(e)
                if port:
                    port += 1
                pass

    @lru_cache
    def _schema_variables(self):
        schema = self.project.detect_schema(exclude_const=True)
        return [key for key in schema]

    @lru_cache
    def _project_min_len_unique_id(self):
        return self.project.min_len_unique_id()

    def job_title(self, job):
        """Override this method for custom job titles.

        This method generates job titles. By default, the title is a pretty
        (but verbose) form of the job state point, based on the project schema.

        :param job: The job being titled.
        :type job: :py:class:`signac.contrib.job.Job`
        :returns: Title to be displayed.
        :rtype: str
        """

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
                    continue  # schema, but not this state point.
                else:
                    s.append("{}={}".format(".".join(keys), _format_num(v)))
            return " ".join(s)
        except Exception as error:
            logger.debug(
                "Error while generating job title: '{}'. "
                "Returning job-id as fallback.".format(error)
            )
            return str(job)

    def job_subtitle(self, job):
        """Override this method for custom job subtitles.

        This method generates job subtitles. By default, the subtitle is a
        minimal unique substring of the job id.

        :param job: The job being subtitled.
        :type job: :py:class:`signac.contrib.job.Job`
        :returns: Subtitle to be displayed.
        :rtype: str
        """
        return str(job)[: max(8, self._project_min_len_unique_id())]

    def job_sorter(self, job):
        """Override this method for custom job sorting.

        This method returns a key that can be compared to sort jobs. By
        default, the sorting key is based on :py:func:`Dashboard.job_title`,
        with natural sorting of numbers. Good examples of such keys are
        strings or tuples of properties that should be used to sort.

        :param job: The job being sorted.
        :type job: :py:class:`signac.contrib.job.Job`
        :returns: Key for sorting.
        :rtype: any comparable type
        """
        key = natsort.natsort_keygen(key=self.job_title, alg=natsort.REAL)
        return key(job)

    @lru_cache
    def _get_all_jobs(self):
        return sorted(self.project.find_jobs(), key=self.job_sorter)

    @lru_cache(maxsize=100)
    def _job_search(self, query):
        if "$where" in query and not self.config.get("ALLOW_WHERE", False):
            flash(
                "Searches using $where allow arbitrary code execution and "
                "are only allowed when the configuration option "
                "'ALLOW_WHERE' is enabled. See also: <a href=\"https://docs.signac.io/projects/dashboard/en/latest/security.html\">Security Guidelines</a>",  # noqa:E501
                "warning",
            )
            raise RuntimeError("ALLOW_WHERE must be enabled for this query.")

        try:
            if query is None:
                f = None
            else:
                try:
                    f = json.loads(query)
                except json.JSONDecodeError:
                    query = shlex.split(query)
                    f = signac.contrib.filterparse.parse_filter_arg(query)
                    flash(f"Search string interpreted as '{json.dumps(f)}'.")
            jobs = self.project.find_jobs(filter=f)
            return sorted(jobs, key=lambda job: self.job_sorter(job))
        except json.JSONDecodeError as error:
            flash(
                "Failed to parse query argument. "
                "Ensure that '{}' is valid JSON!".format(query),
                "warning",
            )
            raise error

    @lru_cache(maxsize=65536)
    def _job_details(self, job):
        return {
            "job": job,
            "title": self.job_title(job),
            "subtitle": self.job_subtitle(job),
        }

    def _setup_pagination(self, jobs):
        total_count = len(jobs) if isinstance(jobs, list) else 0
        page = request.args.get("page", 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
            flash(f"Pagination Error. Displaying page {page}.", "danger")
        try:
            per_page = int(request.args.get("per_page", self.config["PER_PAGE"]))
            if per_page < 1:
                raise ValueError("At least one job is required per page.")
        except ValueError:
            flash(
                f"Pagination Error. Displaying {per_page} jobs per page.",
                "danger",
            )
        pagination = Pagination(page, per_page, total_count)
        if pagination.page < 1 or pagination.page > pagination.pages:
            pagination.page = max(1, min(pagination.page, pagination.pages))
            if pagination.pages > 0:
                flash(
                    f"Pagination Error. Displaying page {pagination.page}.",
                    "danger",
                )
        return pagination

    def _setup_enabled_module_indices(self):
        enabled_module_indices = {}
        for context_name, context_modules in self._modules_by_context.items():
            enabled_module_indices[context_name] = [
                i for i, m in enumerate(context_modules) if m.enabled
            ]
        return enabled_module_indices

    def _render_job_view(self, *args, **kwargs):
        g.active_page = "jobs"
        session["context"] = "JobContext"
        session.setdefault(
            "enabled_module_indices", self._setup_enabled_module_indices()
        )
        view_mode = request.args.get("view", kwargs.get("default_view", "list"))
        if view_mode == "grid":
            if (
                len(session.get("enabled_module_indices", {}).get("JobContext", []))
                == 0
            ):
                flash("No modules for the JobContext are enabled.", "info")
            return render_template("jobs_grid.html", *args, **kwargs)
        elif view_mode == "list":
            return render_template("jobs_list.html", *args, **kwargs)
        else:
            return self._render_error(ValueError(f"Invalid view mode: {view_mode}"))

    def _render_project_view(self, *args, **kwargs):
        g.active_page = "project"
        session["context"] = "ProjectContext"
        session.setdefault(
            "enabled_module_indices", self._setup_enabled_module_indices()
        )
        if (
            len(session.get("enabled_module_indices", {}).get("ProjectContext", []))
            == 0
        ):
            flash("No modules for the ProjectContext are enabled.", "info")
        return render_template("project_info.html", *args, **kwargs)

    def _render_error(self, error):
        if isinstance(error, Exception):
            error_string = f"{type(error).__name__}: {error}"
        else:
            error_string = error
        logger.error(error_string)
        flash(error_string, "danger")
        return render_template("error.html")

    def _get_job_details(self, jobs):
        return [self._job_details(job) for job in list(jobs)]

    def add_url(
        self, import_name, url_rules=[], import_file="signac_dashboard", **kwargs
    ):
        """Add a route to the dashboard.

        This method allows custom view functions to be triggered for specified
        routes. These view functions are imported lazily, when their route
        is triggered. For example, write a file :code:`my_views.py`:

        .. code-block:: python

            def my_custom_view(dashboard):
                return 'This is a custom message.'

        Then, in :code:`dashboard.py`:

        .. code-block:: python

            from signac_dashboard import Dashboard

            class MyDashboard(Dashboard):
                pass

            if __name__ == '__main__':
                dashboard = MyDashboard()
                dashboard.add_url('my_custom_view', url_rules=['/custom-url'],
                                  import_file='my_views')
                dashboard.main()

        Finally, launching the dashboard with :code:`python dashboard.py run`
        and navigating to :code:`/custom-url` will show the custom
        message. This can be used in conjunction with user-provided jinja
        templates and the method :py:func:`flask.render_template` for extending
        dashboard functionality.

        :param import_name: The view function name to be imported.
        :type import_name: str
        :param url_rules: A list of URL rules, see
            :py:meth:`flask.Flask.add_url_rule`.
        :type url_rules: list
        :param import_file: The module from which to import (default:
            :code:`'signac_dashboard'`).
        :type import_file: str
        :param \\**kwargs: Additional keyword arguments to pass to
            :py:meth:`flask.Flask.add_url_rule`.
        """
        if import_file is not None:
            import_name = import_file + "." + import_name
        view = LazyView(dashboard=self, import_name=import_name)
        for url_rule in url_rules:
            self.app.add_url_rule(
                rule=url_rule,
                view_func=view,
                **kwargs,
            )

    def _register_routes(self):
        """Registers routes with the Flask application.

        This method configures context processors, templates, and sets up
        routes for a basic Dashboard instance. Additionally, routes declared by
        modules are registered by this method.
        """
        dashboard = self

        @dashboard.app.after_request
        def prevent_caching(response):
            if "Cache-Control" not in response.headers:
                response.headers["Cache-Control"] = "no-store"
            return response

        @dashboard.app.context_processor
        def injections():
            # inject new variables into the template context
            session.setdefault(
                "enabled_module_indices", self._setup_enabled_module_indices()
            )
            return {
                "APP_NAME": "signac-dashboard",
                "APP_VERSION": __version__,
                "CARDS_PER_ROW": self.config["CARDS_PER_ROW"],
                "modules": self.modules,
                "modules_by_context": self._modules_by_context,
                "enabled_module_indices": session["enabled_module_indices"],
                "module_assets": self._module_assets,
            }

        # Add pagination support from http://flask.pocoo.org/snippets/44/
        @dashboard.app.template_global()
        def url_for_other_page(page):
            args = request.args.copy()
            args["page"] = page
            return url_for(request.endpoint, **args)

        @dashboard.app.template_global()
        def modify_query(**new_values):
            args = request.args.copy()
            for key, value in new_values.items():
                args[key] = value
            return f"{request.path}?{url_encode(args)}"

        @dashboard.app.errorhandler(404)
        def page_not_found(error):
            return self._render_error(str(error))

        @dashboard.login_manager.unauthorized_handler
        def unauthorized_handler():
            return self._render_error("Access token is required.")

        @dashboard.app.route("/login")
        def login():
            provided_token = request.args.get("token")
            if provided_token == self.config["ACCESS_TOKEN"]:
                user = User(provided_token)
                flask_login.login_user(user)
                return redirect("/")

            return self._render_error("Invalid token")

        @dashboard.app.route("/favicon.ico")
        @flask_login.login_required
        def favicon():
            return url_for("static", filename="favicon.ico")

        # These routes are protected within the LazyView utility class
        self.add_url("views.home", ["/"])
        self.add_url("views.settings", ["/settings"])
        self.add_url("views.search", ["/search"])
        self.add_url("views.project_info", ["/project/"])
        self.add_url("views.jobs_list", ["/jobs/"])
        self.add_url("views.show_job", ["/jobs/<jobid>"])
        self.add_url(
            "views.get_file",
            ["/jobs/<jobid>/file/<path:filename>", "/project/file/<path:filename>"],
        )
        self.add_url("views.change_modules", ["/modules"], methods=["POST"])

    def update_cache(self):
        """Clear project and dashboard server caches.

        The dashboard relies on caching for performance. If the data space is
        altered, this method may need to be called before the dashboard
        reflects those changes.
        """
        # Try to update signac project cache. Requires signac 0.9.2 or later.
        with warnings.catch_warnings():
            warnings.simplefilter(action="ignore", category=FutureWarning)
            try:
                self.project.update_cache()
            except Exception:
                pass

        # Clear caches of all dashboard methods
        members = inspect.getmembers(self, predicate=inspect.ismethod)
        for func in filter(
            lambda f: hasattr(f, "cache_clear"), map(lambda x: x[1], members)
        ):
            func.cache_clear()

    def __call__(self, environ, start_response):
        """Call the dashboard as a WSGI application."""
        return self.app(environ, start_response)

    def main(self, command_args=None):
        """Runs the command line interface.

        Call this function to use signac-dashboard from its command line
        interface. For example, save this script as :code:`dashboard.py`:

        .. code-block:: python

            from signac_dashboard import Dashboard

            class MyDashboard(Dashboard):
                pass

            if __name__ == '__main__':
                MyDashboard().main()

        Then the dashboard can be launched with:

        .. code-block:: bash

            python dashboard.py run

        :param command_args: List of CLI arguments to pass, e.g.
            ``["--debug", "--port", "8889"]`` (default: None).
        :type command_args: list
        """

        if command_args is not None and len(command_args) == 0:
            command_args = None

        def _run(args):
            kwargs = vars(args)
            if kwargs.get("host", None) is not None:
                self.config["HOST"] = kwargs.pop("host")
            if kwargs.get("port", None) is not None:
                self.config["PORT"] = kwargs.pop("port")
            self.config["PROFILE"] = kwargs.pop("profile")
            self.config["DEBUG"] = kwargs.pop("debug")

            if self.config["ACCESS_TOKEN"] is not None:
                print(
                    f"To access this server, connect to: "
                    f"http://{self.config['HOST']}:{self.config['PORT']}/"
                    f"login?token={self.config['ACCESS_TOKEN']}"
                )

            self.run()

        parser = argparse.ArgumentParser(
            description="signac-dashboard is a web-based data visualization "
            "and analysis tool, part of the signac framework."
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Show traceback on error for debugging.",
        )
        parser.add_argument(
            "--version",
            action="store_true",
            help="Display the version number and exit.",
        )
        subparsers = parser.add_subparsers()

        parser_run = subparsers.add_parser("run")
        parser_run.add_argument(
            "-p",
            "--profile",
            action="store_true",
            help="Enable flask performance profiling.",
        )
        parser_run.add_argument(
            "-d", "--debug", action="store_true", help="Enable flask debug mode."
        )
        parser_run.add_argument(
            "--host", type=str, help="Host (binding address). Default: localhost"
        )
        parser_run.add_argument(
            "--port", type=int, help="Port to listen on. Default: 8888"
        )
        parser_run.set_defaults(func=_run)

        # This is a hack, as argparse itself does not
        # allow to parse only --version without any
        # of the other required arguments.
        if "--version" in sys.argv:
            print("signac-dashboard", __version__)
            sys.exit(0)

        args = parser.parse_args(command_args)

        if args.debug:
            logger.setLevel(logging.DEBUG)

        if not hasattr(args, "func"):
            parser.print_usage()
            sys.exit(2)
        try:
            self.observer.start()
            args.func(args)
        except RuntimeWarning as warning:
            logger.warning(f"Warning: {warning}")
            if args.debug:
                raise
            sys.exit(1)
        except Exception as error:
            logger.error(f"Error: {error}")
            if args.debug:
                raise
            sys.exit(1)
        finally:
            self.observer.stop()
            self.observer.join()
