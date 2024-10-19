
from .dashboard import blueprint as DashboardModule
from .site import blueprint as SiteModule
from .task import blueprint as TaskModule
from .config import blueprint as ConfigModule
from .logs import blueprint as LogsModule
from .files import blueprint as FilesModule

def get_submodules():
    return [
        DashboardModule,
        SiteModule,
        TaskModule,
        LogsModule,
        FilesModule,
        ConfigModule
    ]
