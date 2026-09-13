"""
RVC (Retrieval-based Voice Conversion) manager.

This module handles automatic download and setup of the RVC repository
if it's not already present in the project directory.

Based on the HuBERT manager pattern.
"""

import logging
import os
import subprocess
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# Directory relative to this module file
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.join(_MODULE_DIR, '..')
_DEFAULT_RVC_DIR = os.path.join(_PROJECT_ROOT, 'Retrieval-based-Voice-Conversion-WebUI')


def _is_git_available() -> bool:
    """Check if git is available on the system."""
    try:
        subprocess.run(
            ['git', '--version'],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _clone_repository(repo_url: str, target_dir: str) -> bool:
    """Clone a git repository.

    Args:
        repo_url: URL of the repository to clone
        target_dir: Directory to clone into

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Cloning repository: {repo_url}")
        subprocess.run(
            ['git', 'clone', repo_url, target_dir],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"Successfully cloned to {target_dir}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repository: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error cloning repository: {e}")
        return False


class RVCManager:
    """Manager for automatic RVC (Retrieval-based Voice Conversion) setup."""

    @staticmethod
    def make_sure_rvc_installed(
        repo_url: str = 'https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI.git',
        install_dir: Optional[str] = None,
        force_reinstall: bool = False
    ) -> str:
        """Download and setup RVC if not already installed.

        This method clones the RVC repository if it doesn't exist in the
        expected location. It requires git to be installed on the system.

        Args:
            repo_url: URL of the RVC repository to clone
            install_dir: Directory to install RVC (default: Retrieval-based-Voice-Conversion-WebUI/
                        in project root)
            force_reinstall: If True, remove existing installation and reinstall

        Returns:
            Path to the installed RVC directory

        Raises:
            RuntimeError: If git is not available or installation fails
            FileNotFoundError: If git is not installed
        """
        if install_dir is None:
            install_dir = _DEFAULT_RVC_DIR

        # Check if already installed
        if os.path.isdir(install_dir) and not force_reinstall:
            # Check if it looks like a valid RVC installation
            if os.path.isfile(os.path.join(install_dir, 'vc_infer_pipeline.py')) or \
               os.path.isfile(os.path.join(install_dir, 'infer.py')):
                logger.info(f"RVC already installed at {install_dir}")
                return install_dir
            else:
                logger.warning(f"Directory exists but doesn't appear to be a valid RVC installation")

        # Check if git is available
        if not _is_git_available():
            raise FileNotFoundError(
                "Git is required to install RVC. Please install git from https://git-scm.com/"
            )

        # Remove existing directory if force reinstall
        if force_reinstall and os.path.isdir(install_dir):
            import shutil
            logger.info(f"Removing existing RVC installation at {install_dir}")
            shutil.rmtree(install_dir)

        # Clone the repository
        if not _clone_repository(repo_url, install_dir):
            raise RuntimeError(f"Failed to clone RVC repository to {install_dir}")

        return install_dir

    @staticmethod
    def get_rvc_path(install_dir: Optional[str] = None) -> str:
        """Get the path to the RVC installation.

        Args:
            install_dir: Custom RVC directory path

        Returns:
            Path to RVC directory
        """
        if install_dir is None:
            install_dir = _DEFAULT_RVC_DIR
        return install_dir

    @staticmethod
    def is_rvc_installed(install_dir: Optional[str] = None) -> bool:
        """Check if RVC is installed.

        Args:
            install_dir: Custom RVC directory path

        Returns:
            True if RVC is installed
        """
        if install_dir is None:
            install_dir = _DEFAULT_RVC_DIR

        if not os.path.isdir(install_dir):
            return False

        # Check for key RVC files
        key_files = ['vc_infer_pipeline.py', 'infer.py']
        return any(os.path.isfile(os.path.join(install_dir, f)) for f in key_files)

    @staticmethod
    def add_rvc_to_path(install_dir: Optional[str] = None) -> None:
        """Add the RVC directory to sys.path for imports.

        Args:
            install_dir: Custom RVC directory path
        """
        if install_dir is None:
            install_dir = _DEFAULT_RVC_DIR

        if install_dir not in sys.path:
            sys.path.insert(0, install_dir)
            logger.info(f"Added {install_dir} to sys.path")


# Convenience function for quick setup
def setup_rvc(install_dir: Optional[str] = None) -> str:
    """Setup RVC by downloading if necessary and adding to path.

    Args:
        install_dir: Custom RVC directory path

    Returns:
        Path to RVC directory
    """
    rvc_path = RVCManager.make_sure_rvc_installed(install_dir=install_dir)
    RVCManager.add_rvc_to_path(rvc_path)
    return rvc_path
