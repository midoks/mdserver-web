
from .dashboard import blueprint as DashboardModule
from .site import blueprint as SiteModule
from .task import blueprint as TaskModule

def get_submodules():
    return [
        DashboardModule,
        SiteModule,
        TaskModule,
    ]
