import os
import subprocess
import venv
import logging
import tempfile
from pathlib import Path
from typing import Dict, Optional, Tuple
from .shells import shells

# object to keep track of virtual environments, python versions and their paths
class VirtualEnvironment:
    """Represents a virtual environment with its name, python version and path."""
    def __init__(self, name: str, python_version: str, path: Path):
        self.name = name
        self.python_version = python_version
        self.path = path
        self.has_pip = (path / "bin" / "pip").exists()


class VenvStackManager:
    """Manages the creation and modification of virtual environments."""
    def __init__(self):
        self.VENV_STACK_HOME = Path.home() / ".venv-stack"
        self.VENV_STACK_HOME.mkdir(exist_ok=True)
        logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Using venv stack home: {self.VENV_STACK_HOME}")
        self.available_venvs = self._load_available_venvs()

    def _load_available_venvs(self) -> Dict[str, 'VirtualEnvironment']:
        """Load all available virtual environments from the venv stack home directory."""

        venvs = {}
        for item in self.VENV_STACK_HOME.iterdir():
            if item.is_dir() and (item / "bin" / "activate").exists():
                venvs[item.name] = VirtualEnvironment(
                    name=item.name,
                    python_version=self._get_python_version(item),
                    path=item
                )
        return venvs

    def _get_python_version(self, venv_path: Path) -> str:
        """Get the Python version of the virtual environment."""

        python_executable = venv_path / "bin" / "python"
        if python_executable.exists():
            version_output = os.popen(f"{python_executable} --version").read().strip()
            return version_output.split()[1] if version_output else "unknown"
        return "unknown"

    def list_available_venvs(self) -> None:
        """List all available virtual environments with their details."""

        if not self.available_venvs:
            print("No virtual environments found.")
            return
        
        # List all available virtual environments
        print("Available virtual environments:")
        for name, venv in self.available_venvs.items():
            print(f"  * Name: {name}\n     - Version: {venv.python_version}\n     - Pip: {'installed' if venv.has_pip else 'no pip'}\n     - Path:{venv.path}")

    def list_installed_packages(self, name=Optional[str]) -> None:
        """List installed packages in a virtual environment. Name optional"""

        def _list_venv_modules(name, venv):
            """List installed packages in a virtual environment by name."""
            pip_path = venv.path / "bin" / "pip"
            if pip_path.exists():
                installed_packages = os.popen(f"{pip_path} list").read().strip()
                if installed_packages:
                    installed_packages = "\n".join("      " + line for line in installed_packages.split("\n"))
                    print(f"* Packages in {name}:\n{installed_packages}")
                else:
                    print(f"  * No packages found in {name}.")

        if not self.available_venvs:
            print("No virtual environments found.")
            return
        
        if name:
            if name not in self.available_venvs:
                print(f"Virtual environment '{name}' does not exist.")
                return
            _list_venv_modules(name, self.available_venvs[name])
        else:
            # List installed packages in each venv
            for name, venv in self.available_venvs.items():
                _list_venv_modules(name, venv)
        
    def create_base_env(self, name: str):
        """Create a base virtual environment with the specified name."""

        base_path = self.VENV_STACK_HOME / name
        if base_path.exists():
            self.logger.error(f"Base venv '{name}' already exists at {base_path}")
            return
        
        self.logger.info(f"Creating base venv: {base_path}")
        venv.create(base_path, with_pip=True)
        self.logger.info(f"Done. Activate it with: source {base_path / 'bin' / 'activate'}")

    def create_project_env(self, path: str, bases: list):
        """Create a project virtual environment at the specified path, linking to base environments."""
        bases = bases.split(",") if isinstance(bases, str) else bases
        path = Path(path)
        if not path.exists() or not path.is_dir():
            self.logger.error(f"Project path '{path}' invalid.")
            return
        
        venv_path = path / ".venv"
        if venv_path.exists():
            self.logger.error(f"Project venv already exists at {venv_path}")
            return
        
        if not bases:
            self.logger.error("No base environments specified.")
            return
        
        for base in bases:
            if base not in self.available_venvs:
                self.logger.error(f"Base venv '{base}' does not exist.")
                return
            if self.available_venvs[base].python_version != self.available_venvs[bases[0]].python_version:
                self.logger.error(f"Base venv '{base}' has a different Python version.")
                return
        
        self.logger.info(f"Creating project venv at {venv_path}")
        venv.create(venv_path, with_pip=True, symlinks=True)
        
        base_paths = []
        for base in bases:
            base_site_root = self.VENV_STACK_HOME / base / "lib"
            py_dirs = list(base_site_root.glob("python*/site-packages"))
            if not py_dirs:
                self.logger.warning(f"No site-packages found in base '{base}'")
                continue
            base_paths.append(str(py_dirs[0].resolve()))
        
        project_site = next((venv_path / "lib").glob("python*/site-packages"))
        pth_path = project_site / "venvstack_combined.pth"
        with open(pth_path, "w") as f:
            f.write("\n".join(base_paths) + "\n")
        self.logger.info(f"Linked {len(base_paths)} base venvs.")

    def add_base_to_existing_project(self, base_name: str, project_path: str):
        """Link a base environment to an existing project virtual environment."""

        project_path = Path(project_path)
        venv_path = project_path / ".venv"
        if not venv_path.exists():
            self.logger.error(f"No virtual environment found at {venv_path}")
            return
        
        if base_name not in self.available_venvs:
            self.logger.error(f"Base venv '{base_name}' does not exist.")
            return
        
        base_site_root = self.available_venvs[base_name].path / "lib"
        py_dirs = list(base_site_root.glob("python*/site-packages"))
        if not py_dirs:
            self.logger.error(f"No site-packages found in base '{base_name}'")
            return
        
        project_site = next((venv_path / "lib").glob("python*/site-packages"))
        pth_path = project_site / f"{base_name}.pth"
        with open(pth_path, "w") as f:
            f.write(str(py_dirs[0].resolve()) + "\n")
        self.logger.info(f"Added base '{base_name}' to project at {project_path}.")

    def export_requirements(self, project_path: str, output_file: str):
        """Export the stacked project environment's installed packages to a requirements.txt"""
        project_venv = Path(project_path) / ".venv"
        pip = project_venv / "bin" / "pip"
        
        if not pip.exists():
            self.logger.error(f"No pip found in project venv at {project_venv}")
            return
        
        with open(output_file, "w") as f:
            # freeze includes packages from bases and project
            proc = subprocess.run([str(pip), "freeze"], stdout=subprocess.PIPE, text=True)
            f.write(proc.stdout)
        self.logger.info(f"Exported requirements to {output_file}")

    def sync_requirements(self, project_path: str, requirements_file: str):
        """Install packages from a requirements file into the stacked project environment"""
        project_venv = Path(project_path) / ".venv"
        pip = project_venv / "bin" / "pip"
        
        if not pip.exists():
            self.logger.error(f"No pip found in project venv at {project_venv}")
            return
        
        if not Path(requirements_file).exists():
            self.logger.error(f"Requirements file '{requirements_file}' not found.")
            return
        
        self.logger.info(f"Installing from {requirements_file} into project venv")
        subprocess.run([str(pip), "install", "-r", requirements_file])
        self.logger.info("Sync complete.")


    def activate_venv(self, name: str):
        """Activate a virtual environment by name"""

        if name and name not in self.available_venvs:
            print(f"[error] Virtual environment '{name}' does not exist.")
            return

        if not name: # activate current project
            venv_path = Path.cwd() / ".venv"
            if not venv_path.exists():
                print("[error] No project virtual environment found in current directory.")
                return
        else:
            venv_path = self.available_venvs[name].path
        activate_script = venv_path / "bin" / "activate"
        if not activate_script.exists():
            print(f"[error] Activation script not found at {activate_script}")
            return

        # Detect shell type
        user_shell = os.environ.get("SHELL", "/bin/sh")
        shell_name = Path(user_shell).name.lower()
        self.logger.debug(f"Detected shell: {shell_name}")

        # find their rc (or None)
        rcfile, flags, env = self._detect_user_rc(shell_name)

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = rcfile.name if rcfile else f".{shell_name}rc"
            tmp_profile_path = Path(tmpdir) / filename
            with open(tmp_profile_path, "w") as f:
                f.write(f"source {rcfile}\n")
                f.write(f"source {activate_script}\n")
                f.flush()
            
            if hasattr(env, '__call__'):
                env = env(tmp_profile_path)

            if hasattr(flags, '__call__'):
                flags = flags(tmp_profile_path)
            
            if env:
                os.environ.update({k: v for k, v in (env.split('=') for env in env.split())})
            self.logger.debug(flags)
            os.execvp(shell_name, [shell_name] + flags)


    @staticmethod
    def _detect_user_rc(shell_name: str) -> Tuple[Optional[Path], list, Optional[str]]:
        """
        Given a shell name (e.g. 'bash', 'zsh', 'fish'), return the Path to
        the first existing rc file, or None if none are found.
        """
        global shells
        home = Path.home()

        rcfiles = shells.get(shell_name, {}).get("rc", [])
        env = shells.get(shell_name, {}).get("env", None)
        flags = shells.get(shell_name, {}).get("flags", [])
        rcfile = rcfiles[0] if rcfiles else '.profile'
        for file in rcfiles:
            rc_path = home / file
            if rc_path.exists():
                rcfile = rc_path
                break
        
        return rcfile, flags, env