import pytest
from pydantic import ValidationError
from hkg_cli.git.models import GitRepositoryModel


def test_valid_repository_with_branch():
    """Test a valid repository configuration with a branch."""
    repo = GitRepositoryModel(
        remote_url="https://github.com/example/repo.git", branch="main"
    )
    assert str(repo.remote_url) == "https://github.com/example/repo.git"
    assert repo.branch == "main"
    assert repo.commit_hash is None
    assert repo.version is None


def test_valid_repository_with_commit_hash():
    """Test a valid repository configuration with a commit hash."""
    repo = GitRepositoryModel(
        remote_url="git@github.com:example/repo.git",
        commit_hash="a1b2c3d4",
    )
    assert str(repo.remote_url) == "git@github.com:example/repo.git"
    assert repo.branch is None
    assert repo.commit_hash == "a1b2c3d4"
    assert repo.version is None


def test_valid_repository_with_version():
    """Test a valid repository configuration with a version tag."""
    repo = GitRepositoryModel(
        remote_url="https://github.com/example/repo.git", version="v1.2.3"
    )
    assert str(repo.remote_url) == "https://github.com/example/repo.git"
    assert repo.branch is None
    assert repo.commit_hash is None
    assert repo.version == "v1.2.3"


def test_valid_repository_with_no_ref():
    """Test a valid repository with no specific ref."""
    repo = GitRepositoryModel(remote_url="https://github.com/example/repo.git")
    assert repo.branch is None
    assert repo.commit_hash is None
    assert repo.version is None


def test_invalid_multiple_refs():
    """Test that providing more than one ref raises a validation error."""
    with pytest.raises(ValidationError) as excinfo:
        GitRepositoryModel(
            remote_url="https://github.com/example/repo.git",
            branch="main",
            version="v1.0.0",
        )
    assert "Only one of `branch`, `commit_hash`, or `version` can be provided." in str(
        excinfo.value
    )

    with pytest.raises(ValidationError):
        GitRepositoryModel(
            remote_url="https://github.com/example/repo.git",
            branch="main",
            commit_hash="a1b2c3d4",
        )

    with pytest.raises(ValidationError):
        GitRepositoryModel(
            remote_url="https://github.com/example/repo.git",
            version="v1.0.0",
            commit_hash="a1b2c3d4",
        )

    with pytest.raises(ValidationError):
        GitRepositoryModel(
            remote_url="https://github.com/example/repo.git",
            branch="main",
            version="v1.0.0",
            commit_hash="a1b2c3d4",
        )


@pytest.mark.parametrize(
    "url",
    ["not-a-url", "https://github.com/example/repo", "ftp://example.com/repo.git"],
)
def test_invalid_remote_url(url):
    """Test that invalid remote URLs raise a validation error."""
    with pytest.raises(ValidationError):
        GitRepositoryModel(remote_url=url)


@pytest.mark.parametrize(
    "url, expected",
    [
        ("https://github.com/user/my-repo.git", "my-repo"),
        ("git@gitlab.com:org/another-repo.git", "another-repo"),
        ("https://dev.azure.com/org/proj/_git/repo-name.git", "repo-name"),
    ],
)
def test_repo_folder_property(url, expected):
    """Test the repo_folder property for various URL formats."""
    repo = GitRepositoryModel(remote_url=url)
    assert repo.repo_folder == expected
