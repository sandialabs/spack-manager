import argparse

import manager_cmds.create_env as create_env
import manager_cmds.develop

import spack.environment as ev


def develop(args):
	"""
	wrapper around manager.develop
	"""
	parser = argparse.ArgumentParser('dummy')
	sub_parser = parser.add_subparsers()
	manager_cmds.develop.add_command(sub_parser, {})
	args = parser.parse_args(['develop', args])
	manager_cmds.develop.manager_develop(parser, args)


def create_dev_env(parser, args):
	env_path = create_env.create_env(parser, args)
	env = ev.Environment(env_path)
	ev.activate(env)
	for s in args.spec:
		if 'trilinos' not in s:
			develop(s)
		else:
			develop('-rb', 'git@github.com:trilinos/trilinos.git', 'develop', s)


def add_command(parser, command_dict):
	sub_parser = parser.add_parser(
		'create-dev-env', help='create a developer focused environment where all root specs are develop specs')
	create_env.setup_parser_args(sub_parser)
	command_dict['create-dev-env'] = create_dev_env
