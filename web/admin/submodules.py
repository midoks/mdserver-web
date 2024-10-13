
from .dashboard import blueprint as DashboardModule

def get_submodules():
    return [
        DashboardModule,
    ]
