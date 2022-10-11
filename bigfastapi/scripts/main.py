import sys

from .args import HELPERS


def print_commands():
    print("Available Commands: ")
    for x_helper in HELPERS:
        print(x_helper + ": " + HELPERS[x_helper][1])


def main(argv=None):
    arguments = sys.argv

    if arguments is not None and len(arguments) > 1:
        helper = arguments[1]
        print("Running: ", helper)
        if helper in HELPERS:
            command = HELPERS[helper][0]
            arguments = arguments[2:]
            command().run(args=arguments)

        else:
            print("Command " + helper + " is not a valid command.")
            print_commands()
    else:
        print_commands()
