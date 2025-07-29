import sys

import lms.api.group.listgroupmembers
import lms.cli.common
import lms.config

OUTPUT_KEYS = [
    ('login_id', 'email', 'Email'),
    ('name', 'name', 'Name'),
    ('id', 'lms_id', 'LMS ID'),
    ('sis_user_id', 'student_id', 'Student ID'),
]

def run_cli(**kwargs):
    users = lms.api.group.listgroupmembers.request(**kwargs)

    return lms.cli.common.cli_list(users, OUTPUT_KEYS,
            collective_name = 'users', sort_key = 'name',
            **kwargs)

def main():
    config = lms.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List the members of a single group.'

    lms.cli.common.add_output_args(parser)

    parser.add_argument('group',
        action = 'store', type = str,
        help = 'The query for the group to list.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
