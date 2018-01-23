import random, os

from fabric.contrib.files import append, exists, sed
from fabric.api import cd, env, local, run


REPO_URL = 'https://github.com/sana256/superlists.git'

def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_file()
        _update_database()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local("git log -n 1 --format=%H", capture=True)
    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if not exists('venv/bin/pip'):
        run(f'virtualenv -p /usr/bin/python3.6 venv')
    run('./venv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv():
    append('.env', 'DJANGO_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        chars = 'abcdefghijklmnoprstuvwxyz0123456789!@#$%^&*()_+=-'
        new_secret = ''.join(random.SystemRandom().choices(chars, k=50))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')
    email_password = os.environ['EMAIL_PASSWORD']
    append('.env', f'EMAIL_PASSWORD={email_password}')


def _update_static_file():
    run('./venv/bin/python manage.py collectstatic --noinput')


def _update_database():
    run('./venv/bin/python manage.py migrate --noinput')
