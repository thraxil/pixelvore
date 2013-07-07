from fabric.api import run, sudo, local, cd, env, roles, execute, runs_once

env.hosts = ['oolong.thraxil.org', 'maru.thraxil.org', 'tardar.thraxil.org']
env.user = 'anders'

env.roledefs = {
    'celery': ['tardar.thraxil.org'],
    'web': ['maru.thraxil.org', 'oolong.thraxil.org'],
}


@roles('web')
def restart_gunicorn():
    sudo("restart pixelvore")

@roles('celery')
def restart_celery():
    sudo("restart pixelvore-celery")

def prepare_deploy():
    local("./manage.py test")

@runs_once
def migrate():
    with cd(code_dir):
        run("./manage.py migrate")

def deploy():
    code_dir = "/var/www/pixelvore/pixelvore"
    with cd(code_dir):
        run("git pull origin master")
        run("./bootstrap.py")
    migrate()
    execute(restart_gunicorn)
    execute(restart_celery)
