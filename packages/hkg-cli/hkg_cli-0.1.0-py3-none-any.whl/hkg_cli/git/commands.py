import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

from hkg_cli.git.models import GitRepositoryModel

logger = logging.getLogger("hkg_cli")


def _get_latest_tag(repo_dir: Path) -> Optional[str]:
    """Get the latest tag from the repository.

    Args:
        repo_dir: The local directory of the repository.

    Returns:
        The latest tag name, or None if no tags are found or an error occurs.
    """
    original_dir = os.getcwd()
    try:
        os.chdir(repo_dir)
        logger.debug("Changed working directory to %s", repo_dir)

        logger.info("Fetching all tags from remote...")
        subprocess.check_call(["git", "fetch", "--tags", "--force", "origin"])

        logger.info("Finding latest tag...")
        result = subprocess.check_output(
            ["git", "tag", "--sort=-v:refname"],
            universal_newlines=True,
            stderr=subprocess.PIPE,
        ).strip()

        if result:
            latest_tag = result.split("\n")[0]
            logger.info("Latest tag found: %s", latest_tag)
            return latest_tag

        logger.info("No tags found in repository.")
        return None
    except subprocess.CalledProcessError as e:
        logger.warning("Could not determine latest tag: %s", e.stderr)
        return None
    except FileNotFoundError:
        logger.error(
            "git command not found. Please ensure Git is installed and in your PATH."
        )
        return None
    finally:
        os.chdir(original_dir)
        logger.debug("Restored working directory to %s", original_dir)


def clone_and_checkout(repo: GitRepositoryModel, target_path: str) -> None:
    """Clone the given repository if it does not exist, and check out the specified ref.

    If the repository already exists, it fetches and checks out the specified ref.
    If no ref is provided, it attempts to check out the latest version tag.
    If no tags exist, it defaults to the 'main' branch.

    Args:
        repo (GitRepositoryModel): The repository configuration.
        target_path (str): The local directory for the repository.

    Raises:
        subprocess.CalledProcessError: If any git command fails.
    """
    target_dir = Path(target_path)
    checkout_ref = None
    is_branch = False

    if repo.commit_hash:
        checkout_ref = repo.commit_hash
    elif repo.version:
        checkout_ref = repo.version
    elif repo.branch:
        checkout_ref = repo.branch
        is_branch = True

    if target_dir.exists() and (target_dir / ".git").exists():
        logger.info("Repository already exists at %s.", target_dir)
        if not checkout_ref:
            checkout_ref = _get_latest_tag(target_dir)
            if not checkout_ref:
                logger.info(
                    "No ref specified and no tags found, checking out 'main' branch."
                )
                checkout_ref = "main"
                is_branch = True
        _fetch_and_checkout(target_dir, checkout_ref, is_branch)
    else:
        logger.info("Cloning %s into %s...", repo.remote_url, target_dir)
        subprocess.check_call(["git", "clone", str(repo.remote_url), str(target_dir)])

        if not checkout_ref:
            checkout_ref = _get_latest_tag(target_dir)
            if not checkout_ref:
                logger.info("No ref specified and no tags found, using default branch.")
                checkout_ref = "main"

        if checkout_ref != "main":
            logger.info("Checking out %s...", checkout_ref)
            _checkout_ref(target_dir, checkout_ref)


def _fetch_and_checkout(repo_dir: Path, ref: str, is_branch: bool) -> None:
    """Fetch and checkout a given ref in an existing repository.

    Args:
        repo_dir (Path): The local directory of the repository.
        ref (str): The branch, tag, or commit hash to check out.
        is_branch (bool): True if the ref is a branch, False otherwise.

    Raises:
        subprocess.CalledProcessError: If any git command fails.
    """
    original_dir = os.getcwd()
    try:
        os.chdir(repo_dir)
        logger.debug("Changed working directory to %s", repo_dir)

        if is_branch:
            logger.info("Fetching branch %s...", ref)
            subprocess.check_call(["git", "fetch", "origin", ref])
            logger.info("Checking out branch %s...", ref)
            subprocess.check_call(["git", "checkout", ref])
            logger.info("Pulling latest changes for branch %s...", ref)
            subprocess.check_call(["git", "pull", "origin", ref])
        else:
            logger.info("Fetching ref %s...", ref)
            subprocess.check_call(["git", "fetch", "origin", ref, "--force"])
            logger.info("Checking out ref %s...", ref)
            subprocess.check_call(["git", "checkout", ref])
    finally:
        os.chdir(original_dir)
        logger.debug("Restored working directory to %s", original_dir)


def _checkout_ref(repo_dir: Path, ref: str) -> None:
    """Check out a given ref in a newly cloned repository.

    Args:
        repo_dir (Path): The local directory of the repository.
        ref (str): The branch, tag, or commit hash to check out.

    Raises:
        subprocess.CalledProcessError: If any git command fails.
    """
    original_dir = os.getcwd()
    try:
        os.chdir(repo_dir)
        logger.debug("Changed working directory to %s", repo_dir)
        logger.info("Checking out %s...", ref)
        subprocess.check_call(["git", "checkout", ref])
    finally:
        os.chdir(original_dir)
        logger.debug("Restored working directory to %s", original_dir)
