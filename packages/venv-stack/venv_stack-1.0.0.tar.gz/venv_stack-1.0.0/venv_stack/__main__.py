from .manager import VenvStackManager
import argparse


def main():
    venv_manager = VenvStackManager()
    parser = argparse.ArgumentParser(description="venv-stack CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    base_parser = subparsers.add_parser("base", help="Create a base virtual environment")
    base_parser.add_argument("name", help="Name of the base virtual environment")

    project_parser = subparsers.add_parser("project", help="Create a project virtual environment")
    project_parser.add_argument("path", nargs="?", default=".", help="Path to the project")
    project_parser.add_argument("bases", help="Comma-separated list of base environment names")

    subparsers.add_parser("list", help="List available virtual environments")
    
    list_packages_parser = subparsers.add_parser("list-packages", help="List installed packages in a virtual environment")
    list_packages_parser.add_argument("name", nargs="?", default=None, help="Name of the virtual environment to list packages for")
    
    activate_parser = subparsers.add_parser("activate", help="Activate a virtual environment")
    activate_parser.add_argument("name", nargs="?", help="Name of the virtual environment to activate. Leave empty to activate current project environment")
    

    link_parser = subparsers.add_parser("link", help="Link base environments to the project virtual environment")
    link_parser.add_argument("base_name", help="Name of the base environment to link")
    link_parser.add_argument("project_path", help="Path to the project")

    export_parser = subparsers.add_parser("export", help="Export project env to requirements file")
    export_parser.add_argument("project_path", nargs="?", default=".", help="Path to the project")
    export_parser.add_argument("output_file", nargs="?", default="requirements.txt", help="Output requirements file")

    sync_parser = subparsers.add_parser("sync", help="Sync project env from requirements file")
    sync_parser.add_argument("project_path", nargs="?", default=".", help="Path to the project")
    sync_parser.add_argument("requirements_file", help="Path to requirements file")

    args = parser.parse_args()

    command_mapping = {
        "base": venv_manager.create_base_env,
        "project": venv_manager.create_project_env,
        "list": venv_manager.list_available_venvs,
        "list-packages": venv_manager.list_installed_packages,
        "activate": venv_manager.activate_venv,
        "link": venv_manager.add_base_to_existing_project,
        "export": venv_manager.export_requirements,
        "sync": venv_manager.sync_requirements
    }

    if args.command in command_mapping:
        kwargs = args.__dict__.copy()
        del kwargs['command']
        command_mapping[args.command](**kwargs)
    else:
        parser.print_help()
        exit(1)


if __name__ == "__main__":
    main()