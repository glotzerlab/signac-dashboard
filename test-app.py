from signac_dashboard import VDashboard
from signac_dashboard.modules import *

if __name__ == "__main__":
    v = VDashboard()
    v.run()
    # d.add_url('my_custom_view', url_rules=['/custom-url'],
    #                   import_file='my_views')
    # d.main()