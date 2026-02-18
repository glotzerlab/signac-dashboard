"""Re-imlpementation of the Dashboard class using Vue Components."""

import signac
from flask import Flask, jsonify, request
from flask_cors import CORS

class VDashboard:
    def __init__(self, port=5001):
        # Set attributes
        self.project = signac.get_project(".")
        self.app = Flask("signac-dashboard")
        self.app.config.update(port=5001)
        self._schema = None

        # Enable CORS
        CORS(self.app, resources={r'/*': {'origins': '*'}})

        # Register routes
        self._register_routes()

    # ------------------------------- PROPERTIES -------------------------------

    @property
    def schema(self):
        """The current project schema, cached for better performance."""
        if self._schema is None:
            self._schema = self.project.detect_schema()
            return self._schema
        else:
            return self._schema

    def reset_schema(self):
        """Recalculate the current project schema."""
        self._schema = self.project.detect_schema()

    # ------------------------------ CALCULATIONS ------------------------------



    # ------------------------------ APPLICATION -------------------------------

    def _register_routes(self):
        """Assign routes for the API endpoints."""    
        
        @self.app.route("/project_schema", methods=["GET"])
        def get_schema():
            """Send the current project's schema in JSON-friendly format."""
            response_object = {"status": "success"}
            payload = {}
            for name, d in self.schema.items():
                # number of data types are included for convenience
                data = {"n_types": len(d)}
                for data_type, values in d.items():
                    data[data_type.__name__] = sorted(values)
                payload[name] = data
            
            response_object["schema"] = payload
            
            return jsonify(response_object)
        
        # @self.app.route("/job/<job")
        # def get_job_sp():
            """Get the statepoint for the job with a provided ID."""


    def run(self):
        """Run the Flask application."""
        self.app.run()

