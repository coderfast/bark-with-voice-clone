# From https://github.com/gitmylo/bark-voice-cloning-HuBERT-quantizer

import hashlib
import logging
import os.path
import shutil
import urllib.request

import huggingface_hub

logger = logging.getLogger(__name__)

# Directory relative to this module file
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_INSTALL_DIR = os.path.join(_MODULE_DIR, '..', 'data', 'models', 'hubert')


def _compute_sha256(file_path: str) -> str:
    """Compute SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def _verify_download(file_path: str, expected_hash: str = None) -> bool:
    """Verify downloaded file integrity.

    Args:
        file_path: Path to the downloaded file
        expected_hash: Optional SHA256 hash to verify against

    Returns:
        True if file is valid, False otherwise
    """
    if not os.path.isfile(file_path):
        return False
    if expected_hash is None:
        return True
    actual_hash = _compute_sha256(file_path)
    if actual_hash != expected_hash:
        logger.warning(f"Hash mismatch for {file_path}: expected {expected_hash}, got {actual_hash}")
        return False
    return True


class HuBERTManager:
    @staticmethod
    def make_sure_hubert_installed(
        download_url: str = 'https://dl.fbaipublicfiles.com/hubert/hubert_base_ls960.pt',
        file_name: str = 'hubert.pt',
        expected_hash: str = None,
        install_dir: str = None
    ):
        """Download HuBERT model if not already installed.

        Args:
            download_url: URL to download the model from
            file_name: Name of the file to save as
            expected_hash: Optional SHA256 hash for verification
            install_dir: Directory to install to (default: data/models/hubert/ relative to module)

        Returns:
            Path to the installed model file
        """
        if install_dir is None:
            install_dir = _DEFAULT_INSTALL_DIR
        if not os.path.isdir(install_dir):
            os.makedirs(install_dir, exist_ok=True)
        install_file = os.path.join(install_dir, file_name)
        if not os.path.isfile(install_file) or not _verify_download(install_file, expected_hash):
            logger.info('Downloading HuBERT base model')
            urllib.request.urlretrieve(download_url, install_file)
            if not _verify_download(install_file, expected_hash):
                os.remove(install_file)
                raise RuntimeError(f"Downloaded file failed verification: {install_file}")
            logger.info('Downloaded HuBERT')
        return install_file

    @staticmethod
    def make_sure_tokenizer_installed(
        model: str = 'quantifier_hubert_base_ls960_14.pth',
        repo: str = 'GitMylo/bark-voice-cloning',
        local_file: str = 'tokenizer.pth',
        install_dir: str = None
    ):
        """Download HuBERT tokenizer if not already installed.

        Args:
            model: Model file name in the HuggingFace repo
            repo: HuggingFace repository ID
            local_file: Local file name to save as
            install_dir: Directory to install to (default: data/models/hubert/ relative to module)

        Returns:
            Path to the installed tokenizer file
        """
        if install_dir is None:
            install_dir = _DEFAULT_INSTALL_DIR
        if not os.path.isdir(install_dir):
            os.makedirs(install_dir, exist_ok=True)
        install_file = os.path.join(install_dir, local_file)
        if not os.path.isfile(install_file):
            logger.info('Downloading HuBERT custom tokenizer')
            huggingface_hub.hf_hub_download(repo, model, local_dir=install_dir, local_dir_use_symlinks=False)
            downloaded_file = os.path.join(install_dir, model)
            if downloaded_file != install_file:
                shutil.move(downloaded_file, install_file)
            logger.info('Downloaded tokenizer')
        return install_file
