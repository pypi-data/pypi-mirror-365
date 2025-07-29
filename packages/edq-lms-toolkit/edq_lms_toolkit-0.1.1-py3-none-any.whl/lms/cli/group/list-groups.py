import sys

import lms.api.group.listgroups
import lms.cli.common
import lms.config

OUTPUT_KEYS = [
    ('name', 'name', 'Name'),
    ('id', 'lms_id', 'LMS ID'),
]

def run_cli(**kwargs):
    groups = lms.api.group.listgroups.request(**kwargs)

    return lms.cli.common.cli_list(groups, OUTPUT_KEYS,
            collective_name = 'groups', sort_key = 'name',
            **kwargs)

def main():
    config = lms.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List groups withing a grouping in a course.'

    lms.cli.common.add_output_args(parser)

    parser.add_argument('grouping',
        action = 'store', type = str, nargs = '?', default = None,
        help = ('The optional query for the grouping (aka "group set" or "group category") to list.'
                + ' If not provided, all groups in the course will be listed.'))

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
