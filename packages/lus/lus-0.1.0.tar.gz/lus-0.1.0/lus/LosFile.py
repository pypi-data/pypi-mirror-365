import os
import shlex
import subprocess
import sys
import ckdl


class LosFile:
    def __init__(self, content: str):
        self.main_lus_kdl = ckdl.parse(content).nodes
        self.print_commands = False
        self.local_variables = {}

        self.check_args(self.main_lus_kdl, sys.argv[1:], True)

    def print_command(self, args: list[str]):
        if self.print_commands:
            print(f"\x1b[1;34m$ {shlex.join(args)}\x1b[0m")

    def run(self, args: list[str], properties: dict[str, str]):
        if args[0] == "exit":
            raise SystemExit(args[1])
        elif args[0] == "cd":
            self.print_command(args)
            os.chdir(args[1])
        elif args[0] == "test":
            if args[1] == "-f" or args[1] == "-d":
                exists = os.path.exists(args[2])
                if (
                    not exists
                    or (args[1] == "-f" and not os.path.isfile(args[2]))
                    or (args[1] == "-d" and not os.path.isdir(args[2]))
                ):
                    if len(args) > 3 and args[3] == "||":
                        self.run(args[4:], properties)
                    else:
                        raise SystemExit(1)
            else:
                raise NotImplementedError(f"test {args[1]} not implemented")
        elif args[0] == "lus":
            old_cwd = os.getcwd()
            # print_command(args)
            try:
                self.check_args(self.main_lus_kdl, args[1:], True)
            except SystemExit as e:
                if e.code != 0:
                    raise SystemExit(e.code)
            finally:
                os.chdir(old_cwd)
        elif args[0] == "export":
            self.print_command(args + [f"{k}={v}" for k, v in properties.items()])
            os.environ.update(properties)
        elif args[0] == "set":
            global print_commands
            if args[1] == "-x":
                print_commands = True
            elif args[1] == "+x":
                print_commands = False
            else:
                raise NotImplementedError(f"set {args[1]} not implemented")
        elif "/" in args[0] and not os.path.isabs(args[0]):
            self.print_command(args)
            subprocess.check_call([os.path.join(os.getcwd(), args[0])] + args[1:])
        else:
            self.print_command(args)
            subprocess.check_call(args)

    def check_args(self, nodes, args: list[str], check_if_args_handled: bool):
        # Flags for this subcommand, i.e. ["--release"]
        flags = []

        # Everything after the last flag. For example, if the command is `lus build --release foo bar
        # -v`, then this will contain `["foo", "bar", "-v"]`.
        remaining_args_without_flags = []

        for arg in args:
            if len(remaining_args_without_flags) == 0 and arg.startswith("-"):
                flags.append(arg)
            else:
                remaining_args_without_flags.append(arg)
        remaining_args = args

        subcommand = (
            remaining_args_without_flags[0]
            if remaining_args_without_flags
            else "default"
        )

        for i, child in enumerate(nodes):
            if child.name == "$":
                if len(child.args) > 0:
                    cmd = []
                    for arg in child.args:
                        if arg == "$args":
                            cmd.extend(remaining_args)
                            remaining_args = []
                        elif arg == "$subcommand":
                            cmd.append(subcommand)
                        else:
                            cmd.append(arg)
                    self.run(cmd, child.properties)
                else:
                    self.local_variables.update(child.properties)
            elif child.name == subcommand:
                try:
                    remaining_args.remove(subcommand)
                except ValueError as e:
                    if subcommand != "default":
                        raise e
                self.check_args(child.children, remaining_args, i == len(nodes) - 1)
                remaining_args = []
            elif child.name in flags:
                remaining_args.remove(child.name)
                self.check_args(child.children, remaining_args_without_flags, False)
        if check_if_args_handled and len(remaining_args) > 0:
            available_subcommands = [
                child.name
                for child in nodes
                if len(child.name) > 0
                and child.name != "$"
                and child.name[0] != "-"
                and child.name != "default"
            ]
            if len(available_subcommands) == 0:
                print(
                    f"\x1b[1;31merror:\x1b[0m Unexpected argument: {shlex.join(remaining_args)}"
                )
            else:
                print(
                    f"\x1b[1;31merror:\x1b[0m Unknown subcommand {shlex.quote(subcommand)} not one of:"
                )
                for available_subcommand in available_subcommands:
                    print(f"    \x1b[1;34m{available_subcommand}\x1b[0m")
            raise SystemExit(1)
