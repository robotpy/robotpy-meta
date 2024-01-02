"""
When a user runs `robotpy` or `python -m robotpy`, they are presented with
several subcommands. Each of these subcommands is a class that must meet
the following requirements:

* The docstring of the class is used when the user does --help. The first
  line is treated as the summary, and all other lines are displayed when
  the subcommand specific help is queried.
* The constructor must take a single argument, an argparse.ArgumentParser.
  The object may register any commands 
* The ``run`` function is called when the subcommand is used by the user.
  The arguments to this function are passed in by name, and the names can
  be any of the options that the subcommand registered. There are two other
  special argument names:
  * ``options`` - if specified, this is the Namespace returned by parse_args
  * ``robot_class`` - if specified, the user's robot.py will be loaded and
    it will be inspected for their robot class, which will be passed in
    as this option
  * ``main_file`` - if specified, the name of the user's robot.py file. This
    is not guaranteed to exist unless robot_class is also an option.
  * ``project_path`` - if specified, the name of the directory that contains 
    the user's robot.py file. This is not guaranteed to exist unless robot_class
    is also an option.

You can register your custom subcommand via Python's entry point mechanism.
This will load any entry point in the "robotpy" group.

"""

import argparse
import importlib.util
import inspect
import os
import pathlib
import sys
import traceback
import typing

import importlib.metadata

from .logconfig import configure_logging

if sys.version_info < (3, 10):

    def entry_points(group):
        eps = importlib.metadata.entry_points()
        return eps.get(group, [])

else:
    entry_points = importlib.metadata.entry_points


#: This is used by wpilib.getOperatingDirectory and wpilib.getDeployDirectory
robot_py_path: typing.Optional[pathlib.Path] = None


def _load_robot_class():
    """
    Loads a valid robot class from the user's robot.py. This is only loaded
    if the subcommand class asks for it via a ``robot_class`` argument to its
    ``run`` function.
    """
    import wpilib

    if not robot_py_path:
        print(f"ERROR: internal error", file=sys.stderr)
        sys.exit(1)
    elif not robot_py_path.exists():
        print(f"ERROR: {robot_py_path} does not exist", file=sys.stderr)
        sys.exit(1)
    elif robot_py_path.is_dir():
        print(f"ERROR: {robot_py_path} is a directory", file=sys.stderr)
        sys.exit(1)

    # Add that directory to sys.path to ensure that imports work as expected
    sys.path.insert(0, str(robot_py_path.parent.absolute()))

    modname = robot_py_path.stem
    spec = importlib.util.spec_from_file_location(modname, robot_py_path)
    if spec is None:
        print(
            f"ERROR: {robot_py_path} could not be loaded as a python module",
            file=sys.stderr,
        )
        sys.exit(1)

    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module

    try:
        spec.loader.exec_module(module)
    except:
        print(f"ERROR: importing {robot_py_path} failed!", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    robot_classes = []

    for k in dir(module):
        try:
            v = getattr(module, k)
        except AttributeError:
            continue
        if (
            inspect.isclass(v)
            and issubclass(v, wpilib.RobotBase)
            and getattr(v, "__module__", None) == modname
        ):
            robot_classes.append((k, v))

    if len(robot_classes) == 1:
        return robot_classes[0][1]
    elif len(robot_classes) == 0:
        print(
            f"ERROR: {robot_py_path} does not contain any robot classes\n"
            "- At least one class must inherit from wpilib.RobotBase or its descendents",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print(
            f"ERROR: {robot_py_path} contains multiple robot classes! Must only contain one. Classes found:",
            file=sys.stderr,
        )
        for k, v in sorted(robot_classes):
            print(f"- {k}: {v}", file=sys.stderr)

        sys.exit(1)


def _enable_faulthandler():
    #
    # In the event of a segfault, faulthandler will dump the currently
    # active stack so you can figure out what went wrong.
    #
    # Additionally, on non-Windows platforms we register a SIGUSR2
    # handler -- if you send the robot process a SIGUSR2, then
    # faulthandler will dump all of your current stacks. This can
    # be really useful for figuring out things like deadlocks.
    #

    import logging

    logger = logging.getLogger("faulthandler")

    try:
        # These should work on all platforms
        import faulthandler

        faulthandler.enable()
    except Exception as e:
        logger.warn("Could not enable faulthandler: %s", e)
        return

    try:
        import signal

        faulthandler.register(signal.SIGUSR2)
        logger.info("registered SIGUSR2 for PID %s", os.getpid())
    except Exception:
        return


class _CustomHelpAction(argparse.Action):
    def __init__(
        self,
        option_strings,
        dest=argparse.SUPPRESS,
        default=argparse.SUPPRESS,
        help=None,
    ):
        super(_CustomHelpAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        parser.print_help()
        parser.exit(1)  # argparse uses an exit code of zero by default


argparse._HelpAction = _CustomHelpAction


def main():
    """
    This function loads available entry points, parses arguments, and
    sets things up specific to RobotPy so that the robot can run. This
    function is used whether the code is running on the roboRIO or
    a simulation.
    """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=inspect.cleandoc(
            """
            RobotPy launcher. See below for subcommands to accomplish various tasks for your robot project.
        """
        ),
    )

    # This allows the user to name their robot.py file something different
    # .. originally I had this as an optional positional, but it breaks some subcommands
    parser.add_argument(
        "--main",
        dest="main_file",
        help="The file that contains your main robot class",
        default=pathlib.Path("robot.py").absolute(),
        type=lambda p: pathlib.Path(p).absolute(),
    )

    subparser = parser.add_subparsers(dest="command", help="commands")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Enable debug logging",
    )

    parser.add_argument(
        "--ignore-plugin-errors",
        action="store_true",
        default=False,
        help="Ignore errors caused by RobotPy plugins (probably should fix or replace instead!)",
    )

    has_cmd = False

    cmds: typing.List[typing.Tuple[str, typing.Any]] = []

    for entry_point in entry_points(group="robotpy"):
        try:
            cmd_class = entry_point.load()
        except Exception:
            if "--ignore-plugin-errors" in sys.argv:
                print("WARNING: Ignoring error in '%s'" % entry_point)
                continue
            else:
                traceback.print_exc(file=sys.stderr)
                print(
                    f"Plugin error detected in '{entry_point}' (use "
                    "--ignore-plugin-errors to ignore this)",
                    file=sys.stderr,
                )
                exit(1)

        cmds.append((entry_point.name, cmd_class))

    cmds.sort()

    for name, cmd_class in cmds:
        desc = inspect.getdoc(cmd_class)
        if desc:
            help = desc.split("\n", 1)[0]
        else:
            help = None

        cmdparser = subparser.add_parser(
            name,
            description=desc,
            help=help,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        obj = cmd_class(cmdparser)
        cmdparser.set_defaults(cmdobj=obj)
        has_cmd = True

    if not has_cmd:
        parser.error(
            "No entry points defined -- robot code can't do anything. Install packages to add entry points (see README)"
        )
        exit(1)

    options = parser.parse_args()
    if options.command is None:
        parser.print_help()
        exit(1)

    main_file: pathlib.Path = options.main_file
    if main_file.is_dir():
        main_file = main_file / "robot.py"

    global robot_py_path
    robot_py_path = main_file

    configure_logging(options.verbose)

    _enable_faulthandler()

    subcommand = options.cmdobj

    signature = inspect.Signature.from_callable(subcommand.run)
    params = dict(signature.parameters)

    kwargs = {}

    # Special arguments for backwards compat
    if params.pop("options", None):
        kwargs["options"] = options
    if params.pop("robot_class", None):
        kwargs["robot_class"] = _load_robot_class()
    if params.pop("main_file", None):
        kwargs["main_file"] = main_file
    if params.pop("project_path", None):
        kwargs["project_path"] = main_file.parent

    ok_args = (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY)
    bad_args = (inspect.Parameter.POSITIONAL_ONLY,)

    for k, v in params.items():
        if v.kind in ok_args:
            # An error here is an error in the command -- should never happen
            kwargs[k] = getattr(options, k)
        elif v.kind in bad_args:
            raise ValueError(
                "internal error: subcommands may only have keyword or normal arguments"
            )

    retval = subcommand.run(**kwargs)

    if retval is None:
        retval = 0
    elif retval is True:
        retval = 0
    elif retval is False:
        retval = 1

    exit(retval)
