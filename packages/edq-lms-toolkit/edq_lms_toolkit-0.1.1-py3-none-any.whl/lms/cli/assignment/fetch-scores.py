import sys

import lms.api.assignment.fetchscores
import lms.cli.common
import lms.config

def run_cli(skip_headers = lms.cli.common.DEFAULT_SKIP_HEADERS, **kwargs):
    submissions = lms.api.assignment.fetchscores.request(**kwargs)

    if (len(submissions) == 0):
        print("No submissions found.", file = sys.stderr)
        return 0

    if (not skip_headers):
        header = "%s (%s)" % (submissions[0]['assignment']['name'], str(submissions[0]['assignment']['id']))
        print("\t".join(['email', header]))

    submissions = list(sorted(submissions, key = lambda submission: submission['user']['email']))
    for submission in submissions:
        score = submission.get('score', '')
        if (score is None):
            score = ''

        print("\t".join(map(str, [submission['user']['email'], score])))

    return 0

def main():
    config = lms.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List scores for an assignment.'

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = lms.cli.common.DEFAULT_SKIP_HEADERS,
        help = 'Skip headers (default: %(default)s).')

    parser.add_argument('assignment',
        action = 'store', type = str,
        help = 'The query for the assignment to fetch information about.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
