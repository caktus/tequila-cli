import os.path
import subprocess

import click


@click.group()
def cli():
    pass


@cli.command()
@click.argument('environment')
@click.argument('playbook', default='site')
def play(environment, playbook):
    if not playbook.endswith('.yml'):
        playbook = '{}.yml'.format(playbook)
    playbook_path = os.path.join('deployment', 'playbooks', playbook)
    environment_path = os.path.join('deployment', 'environments', environment)
    inventory = os.path.join(environment_path, 'inventory')

    subprocess.call(['ansible-playbook', '-i', inventory, playbook_path])


@cli.command()
def install_roles():
    requirements_path = os.path.join('deployment', 'requirements.yml')
    subprocess.call(['ansible-galaxy', 'install', '-i', '-r', requirements_path])
