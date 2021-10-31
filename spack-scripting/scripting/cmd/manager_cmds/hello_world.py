def hello_world(parser, args):
    print('Hello World. I am Spack-Manager. Inside manager')


def add_command(parser, command_dict):
    parser.add_parser('hello-world', help='simple call to hello-world')
    command_dict['hello-world'] = hello_world
