__all__ = ('setup_env', )

import os
import sys

from fabric.api import *

from strange_fabric import distros

DEFAULTS = {
    'remote_distro': distros.DEBIAN,
    'local_tmp': '/tmp',
    'remote_tmp': '/tmp',
    'project_deploy_dir': '~',
    'projectname': None,
    'public_key_path': None,
    'private_key_path': None,
    'deploy_path': None,
    'project_user': None,
    'project_user_description': 'No description',

    'virtualenvs_path': '~/.virtualenvs',
    'virtualenv_path': None,
    'virtualenv_python_path': None,

    'nginx_port': None,
    'nginx_servername': None,
    'nginx_proxy_port': None,
    'nginx_media_root': None,
}

def setup_env(settings=None):
    if hasattr(env, 'strange_config'):
        return

    config = DEFAULTS.copy()
    config.update(settings or {})

    if config.has_key('hosts'):
        env.hosts = config['hosts']

    if config['projectname'] is None:
        die('Missing projectname')

    if config['project_user'] is None:
        config['project_user'] = config['projectname']

    # virtualenv config

    if config['virtualenv_path'] is None:
        config['virtualenv_path'] = os.path.join(config['virtualenvs_path'],
                                                 config['projectname'])
    if config['virtualenv_python_path'] is None:
        config['virtualenv_python_path'] = os.path.join(config['virtualenv_path'],
                                                        'bin/python')


    # deploy configs

    if config['deploy_path'] is None:
        config['deploy_path'] = os.path.join(config['project_deploy_dir'],
                                             config['projectname'])

    archivename = '%s.tar.gz' % config['projectname']
    local_archive_path = os.path.join(config['local_tmp'], archivename)
    config['local_archive_path'] = os.path.expanduser(local_archive_path)
    config['remote_archive_path'] = os.path.join(config['remote_tmp'],
                                                 archivename)

    # key configs

    if config['public_key_path'] is not None:
        config['public_key_path'] = os.path.expanduser(config['public_key_path'])

        config['public_key'] = read_public_key(config['public_key_path'])
        if config['public_key'] is None:
            die('Unable to read public key')

        if config['private_key_path'] is None:
            private_key_path = config['public_key_path'].replace('.pub', '')
            config['private_key_path'] = private_key_path 

    # nginx config

    if config['nginx_port'] is None:
        config['nginx_port'] = 80

    if config['nginx_servername'] is None:
        config['nginx_servername'] = '_'

    if config['nginx_proxy_port'] is None:
        config['nginx_proxy_port'] = 8000

    if config['nginx_media_root'] is None:
        config['nginx_media_root'] = os.path.join('/home',
                                                  config['project_user'])

    env['strange_config'] = config

def die(msg):
    sys.stderr.write(msg)
    sys.stderr.write('\n')
    sys.exit(1)

def read_public_key(path):
    try:
        f = open(path, 'r')
        key_contents = f.read()
        f.close()
        return key_contents
    except IOError, e:
        return None

def require_config():
    if not hasattr(env, 'strange_config'):
        die('Unable to load config')

# def set_if_not_set(k, v):
#     if not env.has_key(k):
#         env[k] = v
# 
# def setup_env_old():
#     require('project_name')
#     # directory used to temporarily store files on the move
#     set_if_not_set('local_tmp', '/tmp')
#     set_if_not_set('remote_tmp', '/tmp')
# 
#     # distribution of remote server
#     set_if_not_set('remote_distro', distros.DEBIAN)
# 
#     # path to virtual environment
#     set_if_not_set('virtualenvs_path', '~/.virtualenvs')
#     set_if_not_set('virtualenv_name', env.project_name)
# 
#     # path to deployed project
#     set_if_not_set('deploy_path',
#                    os.path.join('~/checkouts', env.project_name))
# 
#     set_if_not_set('local_archive_path',
#                    os.path.join(env.local_tmp,'%(project_name)s.tar.gz' % env))
#     set_if_not_set('remote_archive_path', env.local_archive_path)
# 
#     # ssh-related configurations
#     set_if_not_set('local_key_path', '~/.ssh')
#     set_if_not_set('remote_key_path', '~/.ssh')
# 
#     # path to gunicorn pid file
#     set_if_not_set('gunicorn_pid_path',
#                    os.path.join('$HOME', '%(project_name)s.pid') % env)
# 
#     # supervisor
#     set_if_not_set('supervisor_app', env.project_name)
# 
