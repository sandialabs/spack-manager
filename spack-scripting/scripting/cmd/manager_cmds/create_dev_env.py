import argparse

import manager_cmds.create_env as create_env
import manager_cmds.develop

import llnl.util.tty as tty

import spack.environment as ev


def develop(args):
    """
    wrapper around manager.develop
    """
    parser = argparse.ArgumentParser('develop')
    sub_parser = parser.add_subparsers()
    manager_cmds.develop.add_command(sub_parser, {})
    args = parser.parse_args(['develop', *args])
    manager_cmds.develop.manager_develop(parser, args)


def create_dev_env(parser, args):
    if not args.spec:
        tty.die(
            '\nERROR: specs are a required argument for '
            'spack manager create-dev-env.\n')
    for s in args.spec:
        # check that all specs were concrete
        if '@' not in s:
            tty.die(
                '\nERROR: All specs must be concrete to use '
                '\'spack manager create-dev-env\' i.e. at '
                'least [package]@[version].\nTo learn what versions are'
                ' available type \'spack info [package]\''
                '\nSome common exawind versions are: exawind@master, '
                'amr-wind@main and nalu-wind@master\n')
    env_path = create_env.create_env(parser, args)
    env = ev.Environment(env_path)
    ev.activate(env)
    for s in env.user_specs:
        dev_args = []
        # kind of hacky, but spack will try to re-clone
        # if we don't give the --path argument even though
        # it is already in the spack.yaml
        if env.is_develop(s) and 'path' in env.yaml[
                'spack']['develop'][str(s.name)]:
            dev_args.extend([
                '--path', env.yaml['spack']['develop'][str(s.name)]['path']])
        if 'trilinos' in str(s.name):
            dev_args.extend(['-rb', 'git@github.com:trilinos/trilinos.git',
                             str(s.version)])
        dev_args.append(str(s))
        develop(dev_args)
    ev.deactivate()


def add_command(parser, command_dict):
    sub_parser = parser.add_parser(
        'create-dev-env',
        help='create a developer focused environment where all root specs are'
        ' develop specs and they are automatically cloned from the default'
        ' branches')
    create_env.setup_parser_args(sub_parser)
    command_dict['create-dev-env'] = create_dev_env
