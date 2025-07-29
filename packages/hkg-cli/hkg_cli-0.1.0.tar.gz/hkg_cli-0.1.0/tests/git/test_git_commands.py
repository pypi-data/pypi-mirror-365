from unittest.mock import patch, call
import pytest
from hkg_cli.git.commands import clone_and_checkout
from hkg_cli.git.models import GitRepositoryModel


@pytest.fixture
def mock_subprocess():
    """Fixture to mock subprocess.check_call."""
    with patch("hkg_cli.git.commands.subprocess.check_call") as mock:
        yield mock


# --- Test Cases for a New Repository ---


def test_clone_new_repo_with_branch(tmp_path, mock_subprocess):
    """Test cloning a new repo with a specific branch."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git", branch="develop")
    target_path = tmp_path / "repo"
    target_path.mkdir(parents=True, exist_ok=True)

    clone_and_checkout(repo, str(target_path))

    mock_subprocess.assert_has_calls(
        [
            call(["git", "clone", "https://test.com/repo.git", str(target_path)]),
            call(["git", "checkout", "develop"]),
        ]
    )


def test_clone_new_repo_with_commit(tmp_path, mock_subprocess):
    """Test cloning a new repo with a specific commit hash."""
    repo = GitRepositoryModel(
        remote_url="https://test.com/repo.git", commit_hash="abcde123"
    )
    target_path = tmp_path / "repo"
    target_path.mkdir(parents=True, exist_ok=True)

    clone_and_checkout(repo, str(target_path))

    mock_subprocess.assert_has_calls(
        [
            call(["git", "clone", "https://test.com/repo.git", str(target_path)]),
            call(["git", "checkout", "abcde123"]),
        ]
    )


def test_clone_new_repo_with_version(tmp_path, mock_subprocess):
    """Test cloning a new repo with a specific version tag."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git", version="v1.0.0")
    target_path = tmp_path / "repo"
    target_path.mkdir(parents=True, exist_ok=True)

    clone_and_checkout(repo, str(target_path))

    mock_subprocess.assert_has_calls(
        [
            call(["git", "clone", "https://test.com/repo.git", str(target_path)]),
            call(["git", "checkout", "v1.0.0"]),
        ]
    )


@patch("hkg_cli.git.commands._get_latest_tag", return_value="v2.1.0")
def test_clone_new_repo_with_latest_tag(mock_get_tag, tmp_path, mock_subprocess):
    """Test cloning a new repo and checking out the latest tag when no ref is given."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git")
    target_path = tmp_path / "repo"
    target_path.mkdir(parents=True, exist_ok=True)

    clone_and_checkout(repo, str(target_path))

    mock_subprocess.assert_has_calls(
        [
            call(["git", "clone", "https://test.com/repo.git", str(target_path)]),
            call(["git", "checkout", "v2.1.0"]),
        ]
    )
    mock_get_tag.assert_called_once_with(target_path)


@patch("hkg_cli.git.commands._get_latest_tag", return_value=None)
def test_clone_new_repo_no_tags_defaults_to_main(
    mock_get_tag, tmp_path, mock_subprocess
):
    """Test that cloning a new repo defaults to the 'main' branch if no tags are found."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git")
    target_path = tmp_path / "repo"
    target_path.mkdir(parents=True, exist_ok=True)

    clone_and_checkout(repo, str(target_path))

    mock_subprocess.assert_called_once_with(
        ["git", "clone", "https://test.com/repo.git", str(target_path)]
    )
    # No checkout call because 'main' is the default after cloning.
    assert mock_subprocess.call_count == 1
    mock_get_tag.assert_called_once_with(target_path)


# --- Test Cases for an Existing Repository ---


@pytest.fixture
def existing_repo(tmp_path):
    """Fixture to create a mock existing repository."""
    repo_path = tmp_path / "repo"
    (repo_path / ".git").mkdir(parents=True)
    return repo_path


def test_existing_repo_with_branch(existing_repo, mock_subprocess):
    """Test fetching and pulling an existing repo with a branch."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git", branch="feature")

    clone_and_checkout(repo, str(existing_repo))

    mock_subprocess.assert_has_calls(
        [
            call(["git", "fetch", "origin", "feature"]),
            call(["git", "checkout", "feature"]),
            call(["git", "pull", "origin", "feature"]),
        ]
    )


def test_existing_repo_with_version(existing_repo, mock_subprocess):
    """Test fetching and checking out a version tag in an existing repo."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git", version="v1.5.0")

    clone_and_checkout(repo, str(existing_repo))

    mock_subprocess.assert_has_calls(
        [
            call(["git", "fetch", "origin", "v1.5.0", "--force"]),
            call(["git", "checkout", "v1.5.0"]),
        ]
    )


@patch("hkg_cli.git.commands._get_latest_tag", return_value="v3.0.0")
def test_existing_repo_no_ref_checks_out_latest_tag(
    mock_get_tag, existing_repo, mock_subprocess
):
    """Test that an existing repo checks out the latest tag when no ref is provided."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git")

    clone_and_checkout(repo, str(existing_repo))

    mock_get_tag.assert_called_once_with(existing_repo)
    mock_subprocess.assert_has_calls(
        [
            call(["git", "fetch", "origin", "v3.0.0", "--force"]),
            call(["git", "checkout", "v3.0.0"]),
        ]
    )


@patch("hkg_cli.git.commands._get_latest_tag", return_value=None)
def test_existing_repo_no_ref_no_tags_checks_out_main(
    mock_get_tag, existing_repo, mock_subprocess
):
    """Test that an existing repo checks out 'main' when no ref or tags are found."""
    repo = GitRepositoryModel(remote_url="https://test.com/repo.git")

    clone_and_checkout(repo, str(existing_repo))

    mock_get_tag.assert_called_once_with(existing_repo)
    mock_subprocess.assert_has_calls(
        [
            call(["git", "fetch", "origin", "main"]),
            call(["git", "checkout", "main"]),
            call(["git", "pull", "origin", "main"]),
        ]
    )
