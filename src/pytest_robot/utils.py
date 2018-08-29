import re


def change_case(name, lower=True, space="_", camel2snake=True):
    if lower:
        name = name.lower()
    name = name.replace(" ",space)
    if camel2snake:
        name = camel_to_snake_case(name)
    return name


def camel_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def is_robot_var(arg):
    return arg[:2] == "${"


def get_var_name(string):
    return change_case(string[2:-1])


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def stringize(arg):
    """ If argument is not number, put it around quotes """
    if "=" in arg:
        arg_split = arg.split("=")
        arg_name, arg_val = [item.rstrip().lstrip() for item in arg_split]
        pre_template = '{}='.format(arg_name)
        arg = arg_val
    else:
        pre_template = ''

    if is_robot_var(arg):
        arg = get_var_name(arg)
        template = '{}'
    elif is_number(arg):
        template = '{}'
    else:
        template = '"{}"'

    return pre_template+template.format(arg)

def format_robot_args(arglist):
    args = map(stringize, arglist)
    return ", ".join(args)
