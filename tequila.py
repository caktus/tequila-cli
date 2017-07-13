import os.path
import subprocess

from ansible.parsing.vault import VaultLib
import click


@click.group()
def cli():
    pass


@cli.command(short_help="Run a playbook for a given environment.")
@click.argument('environment')
@click.argument('playbook', default='site')
def play(environment, playbook):
    if not playbook.endswith('.yml'):
        playbook = '{}.yml'.format(playbook)
    playbook_path = os.path.join('deployment', 'playbooks', playbook)
    environment_path = os.path.join('deployment', 'environments', environment)
    inventory = os.path.join(environment_path, 'inventory')

    subprocess.call(['ansible-playbook', '-i', inventory, playbook_path])


@cli.command(short_help="Install the Ansible roles in the requirements file.")
def install_roles():
    requirements_path = os.path.join('deployment', 'requirements.yml')
    subprocess.call(['ansible-galaxy', 'install', '-i', '-r', requirements_path])


@cli.command(short_help="Examine the secrets for an environment.")
@click.argument('environment')
def secrets(environment):
    environment_path = os.path.join('deployment', 'environments', environment)
    secrets_path = os.path.join(environment_path, 'group_vars', 'all', 'secrets.yml')

    with open('.vault_pass', 'rb') as f:
        password = f.read().strip()

    vault = VaultLib(password)

    ## Read from a concrete file:

    with open(secrets_path, 'rb') as f:
        ciphertext = f.read()

    ## Read from a file in the git history

    # path_spec = ':'.join((revision, secrets_path))
    # try:
    #     ciphertext = subprocess.check_output(['git', 'show', path_spec])
    # except Exception as e:
    #     raise

    ## Decrypt the ciphertext

    try:
        plaintext = vault.decrypt(ciphertext)
    except Exception as e:
        raise  # FIXME

    click.echo(plaintext)

    ## Alternate decryption

    # subprocess.call(['ansible-vault', 'decrypt', '-'])
