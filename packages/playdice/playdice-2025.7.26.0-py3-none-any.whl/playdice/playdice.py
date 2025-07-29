"""Play dice with the command-line arguments.

When no arguments are given, simulate casting a die.
"""
import sys
import re
import argparse
import random
from pathlib import PurePath
from typing import Optional

# Colour support is optional
try:
    from termcolor import colored
except ModuleNotFoundError:
    def colored(_, *pargs, **kwargs):
        return _

class Dice:

    def __init__(self,
                 me: Optional[str] = PurePath(__file__).stem,
                 purpose: Optional[str] = __doc__) -> None:
        """Kick off scanning the command-line"""
        me = re.sub(r'^play', '', me)
        self.args = self.parse_cmd_line(me, purpose)

    def parse_cmd_line(self, me: str, purpose: str) -> Optional[argparse.Namespace]:
        """
        Read options, show help
        """
        try:
            parser = argparse.ArgumentParser(
                prog=me,
                description=purpose,
                epilog=None,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            )
            parser.add_argument(
                'items',
                nargs='*',
                help='the items to pseudo-randomly select from',
            )
            parser.add_argument(
                '-e', '--eyes',
                type=int,
                default='6',
                help='the number of eyes of the die',
            )
            return parser.parse_args()
        except argparse.ArgumentError as exc:
            raise ValueError('The command line is indecipherable') from exc

    def cast_die(self) -> int:
        """
        Roll it
        """
        if not self.args.items:
            self.args.items = range(1, self.args.eyes + 1)
        cast = random.choice(self.args.items)
        print(colored('{cast}', 'green', None, ['bold']).format(cast=cast))
        return 0

    def __call__(self) -> int:
        """Do this when we get called"""
        return self.cast_die()

def __main() -> int:
    """Run the show"""
    D = Dice()
    sys.exit(D())

def main() -> int:
    """Entry point for the package"""
    try:
        sys.exit(__main())
    except Exception as exc:
        import traceback
        print(traceback.format_exc(), file=sys.stderr, end='')
        sys.exit(2)
    except KeyboardInterrupt:
        print('\rInterrupted by user', file=sys.stderr)
        sys.exit(3)

if __name__ == '__main__':
    sys.exit(main())
