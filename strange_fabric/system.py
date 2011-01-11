import os

from fabric.api import *
from fabric import utils
from fabric.contrib import files

from strange_fabric import conf
from strange_fabric import distros

def install():
    conf.require_config()
    system_settings()
    require('hosts', 'user')
    if env.strange_config['remote_distro'] == distros.DEBIAN:
        sudo('apt-get update')
        sudo('apt-get -y install build-essential')
        sudo('apt-get -y install git-core')
        sudo('apt-get -y install nginx')
        sudo('apt-get -y install supervisor')
        sudo('apt-get -y install python-setuptools')
        sudo('apt-get -y install python-virtualenv')

def add_user():
    """Create a project user."""
    conf.require_config()
    system_settings()
    require('hosts', 'user')

    if not env.strange_config.has_key('public_key') or \
       env.strange_config['public_key'] is None:
        sys.stderr.write('No public key found')
        sys.exit(1)

    def chown(dirname):
        cmd = 'chown %(project_user)s:%(project_user)s %%s' % env.strange_config
        sudo(cmd % dirname)

    sudo('adduser %(project_user)s --gecos "%(project_user_description)s" '
         '--disabled-password' % env.strange_config)

    ssh_path = os.path.join('/home/', env.strange_config['project_user'],
                            '.ssh')
    sudo('mkdir -p %s' % ssh_path)
    chown(ssh_path)
    sudo('chmod 700 %s' % ssh_path)
        
    with cd(ssh_path):
        sudo('echo "%(public_key)s" >> authorized_keys' % env.strange_config)
        chown('authorized_keys')
        sudo('chmod 600 authorized_keys')

def nginx_config():
    conf.require_config()
    system_settings()
    require('hosts')
    config = """
server {
    listen %(nginx_port)s;
    client_max_body_size 2G;
    server_name %(nginx_servername)s;

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://127.0.0.1:%(nginx_proxy_port)s;
    }

    location /media/ {
        root %(nginx_media_root)s;
    }
}
    """ % env.strange_config
    available = os.path.join('/etc/nginx/sites-available',
                             env.strange_config['projectname'])
    enabled = os.path.join('/etc/nginx/sites-enabled',
                           env.strange_config['projectname'])
    files.append(config, available, True, False)
    sudo("ln -s %s %s" % (available, enabled))
    sudo('service nginx reload')

def supervisor_gunicorn_config():
    conf.require_config()
    system_settings()
    require('hosts')
    config = """
[program:%(projectname)s]
command=%(virtualenv_python_path)s manage.py run_gunicorn
directory=/home/%(project_user)s/%(projectname)s/%(projectname)s
user=%(project_user)s
autostart=true
autorestart=true
redirect_stderr=True
    """ % env.strange_config
    filename = os.path.join('/etc/supervisor/conf.d',
                            '%s.conf' % env.strange_config['projectname'])
    files.append(config, filename, True, False)
    sudo('service supervisor start')

def restart_supervisor():
    conf.require_config()
    system_settings()
    require('hosts')
    sudo('service supervisor stop')
    sudo('service supervisor start')

def restart_gunicorn():
    conf.require_config()
    system_settings()
    require('hosts')
    run('supervisorctl restart %(projectname)s' % env.strange_config)


def system_settings():
    """Autheticate as system user with sudo privs."""
    if env.strange_config.has_key('system_user'):
        env.user = env.strange_config['system_user']
