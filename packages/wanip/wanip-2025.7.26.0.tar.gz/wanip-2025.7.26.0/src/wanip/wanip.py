"""Ask a provider for your ip with which you connect to it, then print it out"""

import subprocess
import sys
import argparse
from pathlib import PurePath
from typing import Optional

from .providers import Public_Providers, Providers

class Wanip:

    def __init__(self,
                 me: Optional[str] = PurePath(__file__).stem,
                 purpose : Optional[str] = __doc__) -> None:
        """Kick off scanning the command-line"""
        self.args = self.parse_cmd_line(me, purpose)
        self.args.ipv4 = '--ipv4' if self.args.ipv4 else str()
        self.args.ipv6 = '--ipv6' if self.args.ipv6 else str()

    def curlme(self, provider: str) -> None:
        """Use curl to get hold of my WANIP"""
        # Construct curl command; note that -4 and -6 cannot be used together but since the
        # ArgumentParser takes care of at most one having survived in the args, their
        # representations "can" in the f-string.
        curl_cmd = f'curl {self.args.ipv4} {self.args.ipv6} --fail --show-error --silent {provider}'

        # Obtain data & report
        result = subprocess.run(curl_cmd, shell=True, capture_output=True)
        if result.returncode != 0:
            print(f'Cannot retrieve your WAN IP address from "{provider}"', file=sys.stderr)
            print(f'The error message is this: {result.stderr.decode()}', end='', file=sys.stderr)
        else:
            print('{output}'.format(output=result.stdout.decode().rstrip()))

    def parse_cmd_line(self, me: str, purpose: str) -> Optional[argparse.Namespace]:
        """Read options, show help"""
        # Parse the command line
        try:
            parser = argparse.ArgumentParser(
                prog=me,
                description=purpose,
                epilog='Respect the netiquette when contacting the provider.',
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            parser.add_argument(
                '-p', '--provider',
                type=str,
                help='''
                    the provider to contact, instead of pseudo-randomly auto-selecting one from a
                    pre-built internal list
                    ''',
            )
            group = parser.add_mutually_exclusive_group()
            group.add_argument(
                '-4', '--ipv4',
                action='store_true',
                help='''
                    force the usage of IPv4
                    ''',
            )
            group.add_argument(
                '-6', '--ipv6',
                action='store_true',
                help='''
                    force the usage of IPv6
                    ''',
            )
            parser.add_argument(
                '-n', '--dry-run',
                action='store_true',
                help='''
                    do everything apart from contacting the provider
                    ''',
            )
            parser.add_argument(
                '-v', '--verbose',
                action='count',
                default=0,
                help='''
                    used once: show which provider will be contacted; used twice (or more often):
                    display contactable providers as well (i.e., the pre-built internal list)
                    ''',
            )
            return parser.parse_args()
        except argparse.ArgumentError as exc:
            raise ValueError('The command-line is indecipherable')

    def __call__(self) -> int:
        """Run the show

        The LEGB scoping rule means that in order to overwrite the Public_Providers (a sensible
        thing to do in case the -p/--provider option has been specified), we must declare it as
        global.
        """
        global Public_Providers

        if self.args.provider:
            Public_Providers = Providers(self.args.provider)
        self.args.provider = Public_Providers()

        if self.args.verbose > 1: print(Public_Providers)
        if self.args.verbose >= 1: print('Trying {provider}'.format(provider=self.args.provider))

        if not self.args.dry_run:
            self.curlme(self.args.provider)
        return 0

def __main() -> int:

    W = Wanip()
    sys.exit(W())

def main() -> int:
    try:
        sys.exit(__main())
    except Exception:
        import traceback
        print(traceback.format_exc(), file=sys.stderr, end='')
        sys.exit(2)
    except KeyboardInterrupt:
        print('\rInterrupted by user', file=sys.stderr, end='')
        sys.exit(3)

if __name__ == '__main__':
    sys.exit(main())
