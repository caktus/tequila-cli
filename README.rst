tequila-cli
===========

Tequila-cli is a command-line tool that (mostly) wraps Ansible,
providing for some less verbose deployment workflows.


Getting Started
---------------

These instructions will get you a copy of the project running on your
local machine for development and use.


Prerequisites
~~~~~~~~~~~~~

You will need a Django project set up according to Tequila conventions
in order to make use of the tequila-cli tool.  Tequila-cli will work
with either Python 2.7 or Python 3.


Installing
~~~~~~~~~~

For development purposes, create a virtualenv and clone the repo to
your local machine and pip install it ::

    $ mkvirtualenv tequila -p $(which python3)

    $ pip install ansible click

    $ git clone git+git@github.com:caktus/tequila-cli.git

    $ pip install -e tequila-cli/


Usage
~~~~~

To get the main help page, run with the ``--help`` flag ::

    $ tequila --help
    Usage: tequila [OPTIONS] COMMAND [ARGS]...

    Options:
      --help  Show this message and exit.

    Commands:
      install_roles  Install the Ansible roles in the requirements file.
      play           Run a playbook for a given environment.
      secrets        Examine the secrets for an environment.


The ``install_roles`` subcommand will install the Ansible roles
included in your project's requirements.yml file, by convention
located at deployment/requirements.yml, into the default location for
roles.  It is recommended for Tequila projects that you define an
ansible.cfg file at the root of the project, and specify a path within
the project directories for the roles to be placed in,
e.g. ``roles_path = deployment/roles/``.

This subcommand takes no other options, other than the help flag ::

    $ tequila install_roles --help
    Usage: tequila install_roles [OPTIONS]

    Options:
      -h, --help  Show this message and exit.

The ``play`` subcommand is used to wrap calls to ``ansible-playbook``.
It makes use of the conventions of Tequila projects to shorten the
needed commands, e.g. ``$ ansible-playbook -i
deployment/environments/staging/inventory
deployment/playbooks/web.yml`` into ``$ tequila play staging web``.

The help page will dynamically list the available environments that
can be deployed to, and the playbooks that can be used, as long as
they are in the conventional locations (deployment/environments/ and
deployment/playbooks/, respectively) ::

    $ tequila play --help
    Usage: tequila play [OPTIONS] ENVIRONMENT [PLAYBOOK]

    Environments:
      production
      staging
      vagrant

    Playbooks:
      bootstrap_db
      bootstrap_python
      common
      db
      search
      site (default)
      web

    Options:
      -u, --user REMOTE_USER          connect as this user (default=None)
      -k, --ask-pass                  Prompt for the connection password, if it is
                                      needed for thetransport used. For example,
                                      using ssh and not having a key-
                                      basedauthentication with ssh-agent.
      --private-key, --key-file PRIVATE_KEY_FILE
                                      use this file to authenticate the connection
      -h, --help                      Show this message and exit.

If your project has secrets encrypted using ansible-vault, you will
need to have the appropriate vault password file set up in order to
successfully deploy.

The ``secrets`` subcommand can be used to examine your project's
encrypted secrets files in-place, without overwriting the files with
the decrypted version ::

    $ tequila secrets --help
    Usage: tequila secrets [OPTIONS] ENVIRONMENT [REF]

    Options:
      --diff REF  Git reference to compare against
      -h, --help  Show this message and exit.

So, in order to see the current working version of the secrets for the
staging environment, you would do ::

    $ tequila secrets staging

and it will display the plaintext of the secrets on stdout.  One can
also see the decrypted secrets from some other git reference, such as
a different branch, without explicitly checking it out ::

    $ tequila secrets staging feature-branch

Finally, it is possible to compare the decrypted versions of two
different git references (or a git reference against the current
working version).  This is useful for comparing a re-encrypted changed
working copy of the secrets against the last committed version, like
so ::

    $ tequila secrets staging --diff HEAD

A git-style unified diff of the secrets will be displayed to stdout.


Built With
----------

- `Click <http://click.pocoo.org/5/>`_ - a Python library for creating
  command line interfaces
- `Ansible <http://docs.ansible.com/ansible/latest/index.html>`_ - a
  radically simple IT automation system


License
-------

This project is released under the BSD License.  See the `LICENSE
<https://github.com/caktus/tequila-cli/blob/master/LICENSE>`_ file
for more details.
