import os
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

class DependencyManager:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.python_requirements_path = os.path.join(self.project_root, "requirements.txt")

    def _run_command(self, command: list[str], cwd: str = None, description: str = "Executing command"):
        """Helper to run shell commands."""
        logger.info(f"{description}: {' '.join(command)}")
        try:
            result = subprocess.run(
                command,
                cwd=cwd if cwd else self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"Stdout: {result.stdout}")
            if result.stderr:
                logger.warning(f"Stderr: {result.stderr}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with exit code {e.returncode}: {e.cmd}")
            logger.error(f"Stdout: {e.stdout}")
            logger.error(f"Stderr: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error(f"Command not found. Please ensure '{command[0]}' is installed and in your PATH.")
            return False
        except Exception as e:
            logger.exception(f"An unexpected error occurred: {e}")
            return False

    def install_python_dependencies(self) -> bool:
        """Installs Python dependencies from requirements.txt."""
        if not os.path.exists(self.python_requirements_path):
            logger.warning(f"Python requirements file not found: {self.python_requirements_path}")
            return False
        logger.info("Installing Python dependencies...")
        return self._run_command(
            ["pip", "install", "-r", self.python_requirements_path],
            description="Installing Python dependencies"
        )

    def install_all(self) -> bool:
        """Installs all Python dependencies."""
        logger.info("Starting Python dependency installation...")
        success = self.install_python_dependencies()
        if success:
            logger.info("Python dependency installation completed successfully.")
        else:
            logger.error("Python dependency installation failed.")
        return success

# Example Usage (for testing purposes, can be removed later)
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_example = os.path.abspath(os.path.join(current_dir, "..", ".."))

    manager = DependencyManager(project_root_example)
    manager.install_all()