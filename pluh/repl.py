import sys
from traceback import print_exc
from typing import Callable


def _print_prompt(prompt: str) -> None:
    print(prompt, end="")
    sys.stdout.flush()


def repl(prompt: str, callback: Callable[[str], None]) -> None:
    _print_prompt(prompt)
    for line in sys.stdin:
        try:
            callback(line)
        except Exception:
            print_exc()
        _print_prompt(prompt)
