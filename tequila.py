import difflib
import os
import os.path
import subprocess
import sys

from ansible.parsing.vault import VaultLib
import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
def cli():
    pass


class PlayCommand(click.Command):
    def get_environments(self, ctx):
        environments_path = os.path.join('deployment', 'environments')
        return list(sorted(os.listdir(environments_path)))

    def get_playbooks(self, ctx):
        playbooks_path = os.path.join('deployment', 'playbooks')
        playbooks = []
        for item in sorted(os.listdir(playbooks_path)):
            if not item.endswith('.yml'):
                continue
            item = item[:-4]
            if item == 'site':
                item = 'site (default)'
            playbooks.append(item)

        return playbooks

    def format_environments(self, ctx, formatter):
        envs = [(env, '') for env in self.get_environments(ctx)]
        if envs:
            with formatter.section('Environments'):
                formatter.write_dl(envs)

    def format_playbooks(self, ctx, formatter):
        playbooks = [(playbook, '') for playbook in self.get_playbooks(ctx)]
        if playbooks:
            with formatter.section('Playbooks'):
                formatter.write_dl(playbooks)

    def format_help(self, ctx, formatter):
        """Writes the help into the formatter if it exists.
        This calls into the following methods:
        -   :meth:`format_usage`
        -   :meth:`format_help_text`
        -   :meth:`format_environments`
        -   :meth:`format_playbooks`
        -   :meth:`format_options`
        -   :meth:`format_epilog`
        """
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_environments(ctx, formatter)
        self.format_playbooks(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)


@cli.command(cls=PlayCommand,
             context_settings=CONTEXT_SETTINGS,
             short_help="Run a playbook for a given environment.")
@click.argument('environment')
@click.argument('playbook', default='site')
@click.option('--user', '-u', metavar='REMOTE_USER',
              help="connect as this user (default=None)")
@click.option('--ask-pass', '-k', flag_value='ask_pass', default=False,
              help=(
                  "Prompt for the connection password, if it is needed for the"
                  "transport used. For example, using ssh and not having a key-based"
                  "authentication with ssh-agent."
              ))
@click.option('--private-key', '--key-file', metavar='PRIVATE_KEY_FILE',
              help="use this file to authenticate the connection")
def play(environment, playbook, user, ask_pass, key_file):
    if not playbook.endswith('.yml'):
        playbook = '{}.yml'.format(playbook)
    playbook_path = os.path.join('deployment', 'playbooks', playbook)
    environment_path = os.path.join('deployment', 'environments', environment)
    inventory = os.path.join(environment_path, 'inventory')

    command = ['ansible-playbook', '-i', inventory, playbook_path]
    if user:
        command.extend(('--user', user))
    if ask_pass:
        command.append('--ask-pass')
    if key_file:
        command.extend(('--private-key', key_file))

    sys.exit(subprocess.call(command))


@cli.command(context_settings=CONTEXT_SETTINGS,
             short_help="Install the Ansible roles in the requirements file.")
def install_roles():
    requirements_path = os.path.join('deployment', 'requirements.yml')
    sys.exit(subprocess.call(['ansible-galaxy', 'install', '-i', '-r', requirements_path]))


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
