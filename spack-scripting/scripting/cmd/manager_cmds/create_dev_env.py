import argparse
import sys
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
		print("\tCalling spack manager develop for", s)
		if '@' not in s:
			sys.stderr.write(
				'\nERROR: All specs must be concrete to use '
				'\'spack manager create-dev-env\' i.e. at '
				'least [package]@[version].\nTo learn what versions are'
				' available type \'spack info [package]\''
				'\nSome common exawind versions are: exawind@master, '
				'amr-wind@main and nalu-wind@master\n')
			exit(1)
		if 'trilinos' not in s:
			develop(s)
		else:
			develop('-rb', 'git@github.com:trilinos/trilinos.git', 'develop', s)
	if args.print_path:
		print('Env created at:\n', env_path)


def add_command(parser, command_dict):
	sub_parser = parser.add_parser(
		'create-dev-env', help='create a developer focused environment where all root specs are develop specs')
	create_env.setup_parser_args(sub_parser)
	sub_parser.add_argument('-p', '--print_path', action='store_true',
	                        help='print the environment location to the command line')
	sub_parser.set_defaults(print_path=False)
	command_dict['create-dev-env'] = create_dev_env
