from gbdxtools import Interface
import os
from gbdxrun.local_task import LocalTask
from gbdxrun.local_workflow import LocalWorkflow


HOST = os.environ.get('GBDXTOOLS_HOST', None)
CONFIG = os.environ.get('GBDXTOOLS_PROFILE', None)

config_kwargs = {}
if HOST:
    config_kwargs['host'] = HOST
elif CONFIG:
    config_kwargs['config_file'] = CONFIG

gbdx = Interface(**config_kwargs)

gbdx.Task = LocalTask
gbdx.Workflow = LocalWorkflow


class LocalWorkflowError(Exception):
    pass
