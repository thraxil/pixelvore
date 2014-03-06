from fabric.api import run, sudo, local, cd, env, roles, execute, runs_once

env.hosts = ['orlando.thraxil.org', 'tardar.thraxil.org']
nginx_hosts = ['lolrus.thraxil.org']
env.user = 'anders'
env.forward_agent = True

env.roledefs = {
    'celery': ['orlando.thraxil.org'],
    'web': ['maru.thraxil.org'],
}

code_dir = "/var/www/pixelvore/pixelvore"

@roles('web')
def restart_gunicorn():
    sudo("restart pixelvore")

@roles('celery')
def restart_celery():
    sudo("restart pixelvore-celery")

def prepare_deploy():
    local("./manage.py test")

@roles('web')
def staticfiles():
    with cd(code_dir):
        run("./manage.py collectstatic --noinput --settings=pixelvore.settings_production")
        for n in nginx_hosts:
            run(("rsync -avp --delete media/ "
                 "%s:/var/www/pixelvore/pixelvore/media/") % n)

@runs_once
def migrate():
    with cd(code_dir):
        run("./manage.py migrate")

def deploy():
    with cd(code_dir):
        run("git pull origin master")
        run("./bootstrap.py")
    migrate()
    staticfiles()
    execute(restart_gunicorn)
    execute(restart_celery)
