import argparse
from recipe_cluster import cli

def main():
    parser = argparse.ArgumentParser(description="ReCIPE Command Line Interface")
    subparsers = parser.add_subparsers(title="ReCIPE Commands", dest="cmd")
    subparsers.required = True

    modules = {
        "cook": (cli.cook_main, cli.cook_parser),
    }

    for name, (main_func, args_func) in modules.items():
        sp = subparsers.add_parser(name, description=args_func.__doc__)
        args_func(sp)
        sp.set_defaults(main_func=main_func)

    args = parser.parse_args()
    args.main_func(args)

if __name__ == "__main__":
    main()
