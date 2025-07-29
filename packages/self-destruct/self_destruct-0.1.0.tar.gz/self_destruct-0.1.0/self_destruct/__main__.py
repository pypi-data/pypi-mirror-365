import sys
import subprocess

from .explosives import self_destruct

args = sys.argv[1:]
terminate = True

try:
    if args[0] == '-o':
        if args[1] == 'stop':
            terminate = False
        args = args[2:]
    subprocess.run([sys.executable] + args)
except Exception:  # noqa
    print("User-defined Python code failed to run due to malformed command. "
          "Terminating instance...")
self_destruct(terminate=terminate)
