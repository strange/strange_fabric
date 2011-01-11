import os
import sys

from fabric.api import *

from strange_fabric import conf

def project_init():
    conf.require_config()
    project_settings()
    require('hosts')
    run('mkdir -p media')
    run('mkdir -p %(deploy_path)s' % env.strange_config)
    run('mkdir -p %(virtualenvs_path)s' % env.strange_config)
    with cd(env.strange_config['virtualenvs_path']):
        run('virtualenv %(projectname)s' % env.strange_config)

def deploy():
    """Create a git archive and deploy it."""
    conf.require_config()
    project_settings()
    require('hosts')
    local('git archive --format=tar HEAD | gzip > %(local_archive_path)s' %
          env.strange_config)
    put(env.strange_config['local_archive_path'],
        env.strange_config['remote_archive_path'])
    with cd(env.strange_config['deploy_path']):
        run('tar zxf %(remote_archive_path)s' % env.strange_config)
        virtualenv('pip install -E %(virtualenv_path)s -r '
                   'requirements.txt' % env.strange_config)

    # TODO: not very nice
    staticdir = os.path.join(env.strange_config['deploy_path'], 'static')
    run('ln -f -s %s ./media/static' % staticdir)

# Helpers

def project_settings():
    """Autheticate as project-specific user with private key."""
    env.user = env.strange_config['project_user']
    env.key_filename = env.strange_config['private_key_path']

def virtualenv(command):
    """Execute command after loading a virtual env."""
    conf.require_config()
    project_settings()
    require('hosts')
    path = os.path.join(env.strange_config['virtualenv_path'], 'bin',
                        'activate')
    run('source %s && %s' % (path, command))
