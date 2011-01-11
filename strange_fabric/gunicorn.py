from strange_fabric.config import setup_env

def start_gunicorn():
    require('hosts', 'user')
    setup_env()
    stop_gunicorn()
    with cd(env.deploy_path):
        virtualenv('django-admin.py run_gunicorn '
                   '--workers=1 '
                   '--pid=%(pid_path)s '
                   '--daemon '
                   '--settings=%(project_name)s.settings' % env)

def stop_gunicorn():
    require('hosts', 'user')
    setup_env()
    run('test -e %(pid_path)s && '
        'test "$(ps -p $(cat %(pid_path)s) | grep $(cat %(pid_path)s))" && '
        'kill -9 $(cat %(pid_path)s) || exit 0' % env)
    run('rm -f %(pid_path)s' % env)
