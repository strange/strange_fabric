from fabric.api import *

from strange_fabric import conf

def restart():
    conf.setup_env()
    sudo('supervisorctl restart %(supervisor_app)s' % env)
