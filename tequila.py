import difflib
import os.path
import subprocess

from ansible.parsing.vault import VaultLib
import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
def cli():
    pass


@cli.command(context_settings=CONTEXT_SETTINGS,
             short_help="Run a playbook for a given environment.")
@click.argument('environment')
@click.argument('playbook', default='site')
def play(environment, playbook):
    if not playbook.endswith('.yml'):
        playbook = '{}.yml'.format(playbook)
    playbook_path = os.path.join('deployment', 'playbooks', playbook)
    environment_path = os.path.join('deployment', 'environments', environment)
    inventory = os.path.join(environment_path, 'inventory')

    subprocess.call(['ansible-playbook', '-i', inventory, playbook_path])


@cli.command(context_settings=CONTEXT_SETTINGS,
             short_help="Install the Ansible roles in the requirements file.")
def install_roles():
    requirements_path = os.path.join('deployment', 'requirements.yml')
    subprocess.call(['ansible-galaxy', 'install', '-i', '-r', requirements_path])


def read_git(ref, secrets_path):
    if ref == '.':
        # This is a placeholder for the working tree, read from the concrete file
        with open(secrets_path, 'rb') as f:
            ciphertext = f.read()
    else:
        # Read from a file at the point in the history specified by 'ref'
        path_spec = ':'.join((ref, secrets_path))
        ciphertext = subprocess.check_output(['git', 'show', path_spec])

    return ciphertext


@cli.command(context_settings=CONTEXT_SETTINGS,
             short_help="Examine the secrets for an environment.")
@click.argument('environment')
@click.argument('ref', default='.')
@click.option('--diff', metavar='REF', help="Git reference to compare against")
def secrets(environment, ref, diff):
    environment_path = os.path.join('deployment', 'environments', environment)
    secrets_path = os.path.join(environment_path, 'group_vars', 'all', 'secrets.yml')

    with open('.vault_pass', 'rb') as f:
        password = f.read().strip()

    vault = VaultLib(password)

    secrets = [read_git(ref, secrets_path)]
    if diff is not None:
        secrets.append(read_git(diff, secrets_path))

    # Decrypt the ciphertext
    plaintext = [vault.decrypt(x).decode('utf-8') for x in secrets]

    if diff is None:
        click.echo(plaintext[0])
    else:
        click.echo(
            ''.join(difflib.unified_diff(plaintext[1].splitlines(True),
                                         plaintext[0].splitlines(True),
                                         fromfile=':'.join((diff, secrets_path)),
                                         tofile=':'.join((ref, secrets_path))))
        )
