
from .dashboard import blueprint as DashboardModule
from .site import blueprint as SiteModule
from .task import blueprint as TaskModule
from .config import blueprint as ConfigModule
from .logs import blueprint as LogsModule
from .files import blueprint as FilesModule
from .soft import blueprint as SoftModule
from .plugins import blueprint as PluginsModule
from .crontab import blueprint as CrontabModule
from .firewall import blueprint as FirewallModule
from .control import blueprint as ControlModule

def get_submodules():
    return [
        DashboardModule,
        SiteModule,
        TaskModule,
        LogsModule,
        FilesModule,
        SoftModule,
        PluginsModule,
        CrontabModule,
        FirewallModule,
        ControlModule,
        ConfigModule,
    ]
