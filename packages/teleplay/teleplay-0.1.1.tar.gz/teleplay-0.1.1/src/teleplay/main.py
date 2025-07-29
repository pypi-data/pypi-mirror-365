import sys
import yaml
import importlib
import pkg_resources

from io import StringIO

def reset_args() -> None:
    """ Resets command-line arguments from prior binaries """
    values = len(sys.argv) - 1
    while len(sys.argv) > 0:
        del sys.argv[values]
        values -= 1
    sys.argv.append("")

def load_config(filename: str = "config.yaml") -> dict:
    """ Loads the configuration file """
    try:
        with open("teleplay.yaml", "r") as fh:
            config = yaml.safe_load(fh)
        return config
    except FileNotFoundError:
        print("[ERROR] Could not find teleplay.yaml file")
        sys.exit(1)

def discover_modules(modules: list = [], mod_group: str = "console_scripts") -> list[pkg_resources.EntryPoint]:
    """ Discovers entry points for system modules """
    # Provides a list of all modules with entry points
    pkgs = pkg_resources.iter_entry_points(group = mod_group)
    # Returns a list of the module entry point accompanied by args from config.yaml
    return [(pkg, modules[pkg.name]["args"]) for pkg in pkgs if pkg.name in modules]

def run_module(entry_point: pkg_resources.EntryPoint, arguments: list = []) -> None:
    """ Runs module based on reported entry point """

    # Apply any arguments provided in config
    for arg in arguments:
        if arg is not None:
            sys.argv.append(arg)

    # Load the entry point or fail over to importlib
    try:
        entry = entry_point.load()
    except ImportError:
        mod = entry_point.attrs[0]
        func = entry_point.attrs[1]
        # Module apparently needs coercion
        entry = getattr(importlib.import_module(
            f"{entry_point.name}.{mod}"
        ), func)

    # Run the program entry point
    stdout = sys.stdout
    output = StringIO()
    sys.stdout = output
    try:
        # Run the entry point
        entry()
    except SystemExit as e:
        # Circumvent any fun forced exits
        pass
    finally:
        # Return stdout to original handler
        sys.stdout = stdout
    return output.getvalue()

def main():
    """ Main function """
    config = load_config()
    # Supply relevant modules to filter the list
    entry_points = discover_modules(modules = config["modules"])
    # For each discovered module, run the process
    for entry in entry_points:
        # Run the module by providing the module entry and the args
        result = run_module(
            entry_point = entry[0],
            arguments = entry[1]
        )
        # Get the specified outcome of the process
        outcome = config["modules"][entry[0].name]["outcome"]
        # Attempt to assert it in various ways; need to make
        # type independent?
        try:
            expected_type = type(outcome)
            assert expected_type(result) == outcome
        except AssertionError:
            sys.exit(1)
        # Blast the previously-supplied args
        reset_args()

if __name__ == "__main__":
    main()
