"""
Pydantic data models for GitHub API responses.

These models provide type-safe representations of GitHub API data
with automatic validation and serialization.
"""

from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    """Represents a GitHub user profile."""

    login: str
    name: str | None = None
    bio: str | None = None
    public_repos: int = 0
    followers: int = 0
    following: int = 0
    avatar_url: str | None = None
    html_url: str | None = None
    created_at: str | None = None
    location: str | None = None
    company: str | None = None
    blog: str | None = None

    model_config = {"populate_by_name": True}


class GitHubCommit(BaseModel):
    """Represents a GitHub commit."""

    sha: str
    message: str
    author_name: str
    author_date: str
    url: str | None = None


class GitHubRepository(BaseModel):
    """Represents a GitHub repository."""

    name: str
    full_name: str
    description: str | None = None
    language: str | None = None
    stars: int = Field(0, alias="stargazers_count")
    forks: int = Field(0, alias="forks_count")
    watchers: int = Field(0, alias="watchers_count")
    open_issues: int = Field(0, alias="open_issues_count")
    created_at: str | None = None
    updated_at: str | None = None
    html_url: str | None = None
    default_branch: str = "main"
    is_fork: bool = Field(False, alias="fork")
    topics: list[str] = []
    license_name: str | None = None

    model_config = {"populate_by_name": True}


class GitHubPullRequest(BaseModel):
    """Represents a GitHub pull request."""

    number: int
    title: str
    state: str
    user_login: str
    created_at: str
    updated_at: str | None = None
    html_url: str | None = None
    body: str | None = None


class GitHubIssue(BaseModel):
    """Represents a GitHub issue."""

    number: int
    title: str
    state: str
    user_login: str
    created_at: str
    labels: list[str] = []
    html_url: str | None = None
    body: str | None = None


class RepoStats(BaseModel):
    """Aggregated repository statistics."""

    repository: str
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    open_issues: int = 0
    language: str | None = None
    topics: list[str] = []
    created_at: str | None = None
    last_updated: str | None = None
    license: str | None = None


class GitHubContributor(BaseModel):
    """Represents a contributor to a GitHub repository."""

    login: str
    contributions: int
    html_url: str | None = None
    avatar_url: str | None = None


class GitHubRelease(BaseModel):
    """Represents a GitHub release or tag."""

    tag_name: str
    name: str | None = None
    published_at: str | None = None
    html_url: str | None = None
    body: str | None = None
    is_prerelease: bool = False


class GitHubUserEvent(BaseModel):
    """Represents a recent activity event by a user."""

    event_type: str
    repo_name: str
    created_at: str
    payload_summary: str | None = None
