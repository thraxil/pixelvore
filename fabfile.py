from fabric.api import run, sudo, local, cd, env, roles, execute, runs_once

env.hosts = ['orlando.thraxil.org', 'condor.thraxil.org']
nginx_hosts = ['north.thraxil.org']
env.user = 'anders'

env.roledefs = {
    'celery': ['condor.thraxil.org'],
    'web': ['orlando.thraxil.org'],
}

code_dir = "/var/www/pixelvore/pixelvore"

@roles('web')
def restart_gunicorn():
    sudo("/sbin/restart pixelvore", shell=False)

@roles('celery')
def restart_celery():
    sudo("/sbin/restart pixelvore-celery", shell=False)

def prepare_deploy():
    local("make test")

@roles('web')
def staticfiles():
    with cd(code_dir):
        run("make collectstatic")
        run("make compress")

@runs_once
def migrate():
    with cd(code_dir):
        run("make migrate")

def deploy():
    with cd(code_dir):
        run("git pull origin master")
        run("make")
    migrate()
    staticfiles()
    execute(restart_gunicorn)
    execute(restart_celery)
