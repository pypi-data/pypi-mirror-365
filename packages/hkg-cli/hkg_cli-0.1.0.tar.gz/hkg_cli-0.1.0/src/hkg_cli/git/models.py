"""Models needed in git module."""

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Annotated, Optional
from urllib.parse import urlparse
from typing_extensions import Self


class GitRepositoryModel(BaseModel):
    """GitRepositoryModel."""

    remote_url: Annotated[
        str,
        Field(
            description="The URL to the Git repository. Can be either HTTP(S) or SSH URL.",
            pattern=r"^(https?://|git@).*\.git$",
        ),
    ]
    branch: Annotated[
        Optional[str],
        Field(description="The name of the branch to use in the setup.", min_length=1),
    ] = None
    commit_hash: Annotated[
        Optional[str],
        Field(description="The commit hash to use in the setup.", min_length=1),
    ] = None
    version: Annotated[
        Optional[str],
        Field(description="The version to use in the setup.", min_length=1),
    ] = None

    @model_validator(mode="after")
    def validate_exclusive_fields(self) -> Self:
        """Ensure that only one of branch, commit_hash or version is provided."""
        provided_fields = [self.branch, self.commit_hash, self.version]
        if sum(f is not None for f in provided_fields) > 1:
            raise ValueError(
                "Only one of `branch`, `commit_hash`, or `version` can be provided."
            )
        return self

    @property
    def repo_folder(self):
        """Return the folder name when cloned."""
        # Extract the repository name (strip trailing slashes, take the last component)
        parsed_url = urlparse(str(self.remote_url))
        repo_name = parsed_url.path.rstrip("/").split("/")[-1]

        # Remove the ".git" suffix if present
        if repo_name.lower().endswith(".git"):
            repo_name = repo_name[:-4]

        return repo_name
