#!/usr/bin/env python3
from signac_dashboard import Dashboard
config = {
    'PROJECT_DIR': '/path/to/signac/directory'
}
dashboard = Dashboard(config)
dashboard.run(host='localhost', port=8888, debug=True)
