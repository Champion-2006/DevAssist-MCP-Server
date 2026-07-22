"""
GitHub API service layer.

Provides async methods to interact with the GitHub REST API v3
with proper error handling, rate limiting awareness, and structured responses.
"""

import json
from typing import Any

import httpx

from config import settings
from models.github_models import (
    GitHubCommit,
    GitHubContributor,
    GitHubIssue,
    GitHubPullRequest,
    GitHubRelease,
    GitHubRepository,
    GitHubUser,
    GitHubUserEvent,
    RepoStats,
)
from utils.exceptions import GitHubAPIError
from utils.logger import get_logger

logger = get_logger(__name__)


class GitHubService:
    """Service for interacting with the GitHub REST API v3."""

    def __init__(
        self,
        token: str | None = None,
        base_url: str | None = None,
    ) -> None:
        """
        Initialize the GitHub service.

        Args:
            token: GitHub Personal Access Token. Defaults to settings.
            base_url: GitHub API base URL. Defaults to settings.
        """
        self.token = token or settings.github_token
        self.base_url = (base_url or settings.github_api_base_url).rstrip("/")
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": f"DevAssist-MCP/{settings.server_version}",
        }
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Make an authenticated request to the GitHub API.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path (e.g., '/users/octocat').
            params: Optional query parameters.

        Returns:
            Parsed JSON response.

        Raises:
            GitHubAPIError: If the API request fails.
        """
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"GitHub API request: {method} {url}")

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=settings.http_timeout,
                follow_redirects=True,
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                )

                # Log rate limit info
                remaining = response.headers.get("X-RateLimit-Remaining")
                limit = response.headers.get("X-RateLimit-Limit")
                if remaining and limit:
                    logger.debug(
                        f"GitHub API rate limit: {remaining}/{limit} remaining"
                    )
                    if int(remaining) < 10:
                        logger.warning(
                            f"GitHub API rate limit low: {remaining}/{limit} remaining"
                        )

                # Handle error responses
                if response.status_code == 404:
                    raise GitHubAPIError(
                        message=f"Resource not found: {endpoint}",
                        status_code=404,
                        details={"endpoint": endpoint},
                    )
                elif response.status_code == 403:
                    raise GitHubAPIError(
                        message="API rate limit exceeded or access forbidden",
                        status_code=403,
                        details={
                            "rate_limit_remaining": remaining,
                            "endpoint": endpoint,
                        },
                    )
                elif response.status_code == 401:
                    raise GitHubAPIError(
                        message="Authentication failed. Check your GitHub token.",
                        status_code=401,
                    )
                elif response.status_code >= 400:
                    raise GitHubAPIError(
                        message=f"API request failed with status {response.status_code}",
                        status_code=response.status_code,
                        details={"response": response.text[:500]},
                    )

                return response.json()

        except httpx.TimeoutException as e:
            logger.error(f"GitHub API request timed out: {url}")
            raise GitHubAPIError(
                message=f"Request timed out: {endpoint}",
                status_code=408,
                details={"endpoint": endpoint},
            ) from e
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to GitHub API: {e}")
            raise GitHubAPIError(
                message="Failed to connect to GitHub API",
                status_code=503,
            ) from e
        except GitHubAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in GitHub API request: {e}")
            raise GitHubAPIError(
                message=f"Unexpected error: {str(e)}",
                status_code=500,
            ) from e

    async def get_user_profile(self, username: str) -> GitHubUser:
        """
        Get a GitHub user's profile information.

        Args:
            username: GitHub username.

        Returns:
            GitHubUser model with profile data.
        """
        logger.info(f"Fetching GitHub profile for user: {username}")
        data = await self._make_request("GET", f"/users/{username}")
        return GitHubUser.model_validate(data)

    async def get_repo_info(
        self, username: str, repository: str
    ) -> GitHubRepository:
        """
        Get repository information.

        Args:
            username: Repository owner username.
            repository: Repository name.

        Returns:
            GitHubRepository model with repo data.
        """
        logger.info(f"Fetching repo info: {username}/{repository}")
        data = await self._make_request("GET", f"/repos/{username}/{repository}")

        # Extract license name if present
        license_info = data.get("license")
        if license_info and isinstance(license_info, dict):
            data["license_name"] = license_info.get("name")

        return GitHubRepository.model_validate(data)

    async def get_latest_commits(
        self,
        username: str,
        repository: str,
        count: int = 5,
    ) -> list[GitHubCommit]:
        """
        Get the latest commits from a repository.

        Args:
            username: Repository owner username.
            repository: Repository name.
            count: Number of commits to retrieve (default: 5).

        Returns:
            List of GitHubCommit models.
        """
        logger.info(
            f"Fetching latest {count} commits for {username}/{repository}"
        )
        data = await self._make_request(
            "GET",
            f"/repos/{username}/{repository}/commits",
            params={"per_page": count},
        )

        commits: list[GitHubCommit] = []
        for item in data:
            commit_data = item.get("commit", {})
            author_data = commit_data.get("author", {})
            commits.append(
                GitHubCommit(
                    sha=item.get("sha", ""),
                    message=commit_data.get("message", ""),
                    author_name=author_data.get("name", "Unknown"),
                    author_date=author_data.get("date", ""),
                    url=item.get("html_url"),
                )
            )
        return commits

    async def get_repo_stats(
        self, username: str, repository: str
    ) -> RepoStats:
        """
        Get aggregated repository statistics.

        Args:
            username: Repository owner username.
            repository: Repository name.

        Returns:
            RepoStats model with aggregated statistics.
        """
        logger.info(f"Fetching repo stats for {username}/{repository}")
        repo = await self.get_repo_info(username, repository)

        return RepoStats(
            repository=repo.full_name,
            stars=repo.stars,
            forks=repo.forks,
            watchers=repo.watchers,
            open_issues=repo.open_issues,
            language=repo.language,
            topics=repo.topics,
            created_at=repo.created_at,
            last_updated=repo.updated_at,
            license=repo.license_name,
        )

    async def get_pull_requests(
        self,
        username: str,
        repository: str,
        state: str = "open",
    ) -> list[GitHubPullRequest]:
        """
        Get pull requests for a repository.

        Args:
            username: Repository owner username.
            repository: Repository name.
            state: PR state filter ('open', 'closed', 'all'). Default: 'open'.

        Returns:
            List of GitHubPullRequest models.
        """
        logger.info(
            f"Fetching {state} PRs for {username}/{repository}"
        )
        data = await self._make_request(
            "GET",
            f"/repos/{username}/{repository}/pulls",
            params={"state": state, "per_page": 30},
        )

        pull_requests: list[GitHubPullRequest] = []
        for item in data:
            user_data = item.get("user", {})
            pull_requests.append(
                GitHubPullRequest(
                    number=item.get("number", 0),
                    title=item.get("title", ""),
                    state=item.get("state", ""),
                    user_login=user_data.get("login", "Unknown"),
                    created_at=item.get("created_at", ""),
                    updated_at=item.get("updated_at"),
                    html_url=item.get("html_url"),
                    body=item.get("body"),
                )
            )
        return pull_requests

    async def get_issues(
        self,
        username: str,
        repository: str,
        state: str = "open",
    ) -> list[GitHubIssue]:
        """
        Get issues for a repository.

        Args:
            username: Repository owner username.
            repository: Repository name.
            state: Issue state filter ('open', 'closed', 'all'). Default: 'open'.

        Returns:
            List of GitHubIssue models.
        """
        logger.info(
            f"Fetching {state} issues for {username}/{repository}"
        )
        data = await self._make_request(
            "GET",
            f"/repos/{username}/{repository}/issues",
            params={"state": state, "per_page": 30},
        )

        issues: list[GitHubIssue] = []
        for item in data:
            # Skip pull requests (GitHub API includes them in issues endpoint)
            if "pull_request" in item:
                continue

            user_data = item.get("user", {})
            label_names = [
                label.get("name", "") for label in item.get("labels", [])
            ]
            issues.append(
                GitHubIssue(
                    number=item.get("number", 0),
                    title=item.get("title", ""),
                    state=item.get("state", ""),
                    user_login=user_data.get("login", "Unknown"),
                    created_at=item.get("created_at", ""),
                    labels=label_names,
                    html_url=item.get("html_url"),
                    body=item.get("body"),
                )
            )
        return issues

    async def get_user_repos(
        self,
        username: str,
        count: int = 10,
        sort: str = "updated",
    ) -> list[GitHubRepository]:
        """
        Get public repositories belonging to a user.

        Args:
            username: GitHub username.
            count: Number of repositories to return (default: 10).
            sort: Sort field ('updated', 'created', 'pushed', 'full_name'). Default: 'updated'.

        Returns:
            List of GitHubRepository models.
        """
        logger.info(f"Fetching {count} repos for user '{username}' (sorted by {sort})")
        data = await self._make_request(
            "GET",
            f"/users/{username}/repos",
            params={"per_page": count, "sort": sort, "direction": "desc"},
        )

        repos: list[GitHubRepository] = []
        for item in data:
            license_info = item.get("license")
            if license_info and isinstance(license_info, dict):
                item["license_name"] = license_info.get("name")
            repos.append(GitHubRepository.model_validate(item))
        return repos

    async def get_user_activity(
        self,
        username: str,
        count: int = 10,
    ) -> list[GitHubUserEvent]:
        """
        Get recent public activity events for a user.

        Args:
            username: GitHub username.
            count: Number of activity events to return (default: 10).

        Returns:
            List of GitHubUserEvent models.
        """
        logger.info(f"Fetching recent activity events for user '{username}'")
        data = await self._make_request(
            "GET",
            f"/users/{username}/events/public",
            params={"per_page": count},
        )

        events: list[GitHubUserEvent] = []
        for item in data:
            event_type = item.get("type", "UnknownEvent")
            repo_info = item.get("repo", {})
            repo_name = repo_info.get("name", "UnknownRepo")
            created_at = item.get("created_at", "")

            # Format payload summary based on event type
            payload = item.get("payload", {})
            summary = None
            if event_type == "PushEvent":
                commits = payload.get("commits", [])
                summary = f"Pushed {len(commits)} commit(s)"
            elif event_type == "PullRequestEvent":
                action = payload.get("action", "")
                pr = payload.get("pull_request", {})
                summary = f"{action.capitalize()} PR #{pr.get('number', '')}: {pr.get('title', '')}"
            elif event_type == "IssuesEvent":
                action = payload.get("action", "")
                issue = payload.get("issue", {})
                summary = f"{action.capitalize()} issue #{issue.get('number', '')}: {issue.get('title', '')}"
            elif event_type == "CreateEvent":
                ref_type = payload.get("ref_type", "repo")
                summary = f"Created {ref_type}"
            elif event_type == "WatchEvent":
                summary = "Starred repository"

            events.append(
                GitHubUserEvent(
                    event_type=event_type,
                    repo_name=repo_name,
                    created_at=created_at,
                    payload_summary=summary,
                )
            )
        return events

    async def get_repo_languages(
        self,
        username: str,
        repository: str,
    ) -> dict[str, Any]:
        """
        Get language byte breakdown for a repository.

        Args:
            username: Repository owner.
            repository: Repository name.

        Returns:
            Dict mapping language names to bytes and calculated percentages.
        """
        logger.info(f"Fetching language breakdown for {username}/{repository}")
        data = await self._make_request(
            "GET",
            f"/repos/{username}/{repository}/languages",
        )

        total_bytes = sum(data.values())
        result: dict[str, Any] = {
            "repository": f"{username}/{repository}",
            "total_bytes": total_bytes,
            "languages": {},
        }

        if total_bytes > 0:
            for lang, count_bytes in data.items():
                percentage = round((count_bytes / total_bytes) * 100, 1)
                result["languages"][lang] = {
                    "bytes": count_bytes,
                    "percentage": f"{percentage}%",
                }

        return result

    async def get_repo_contributors(
        self,
        username: str,
        repository: str,
        count: int = 10,
    ) -> list[GitHubContributor]:
        """
        Get top contributors to a repository.

        Args:
            username: Repository owner.
            repository: Repository name.
            count: Number of contributors to return (default: 10).

        Returns:
            List of GitHubContributor models.
        """
        logger.info(f"Fetching top {count} contributors for {username}/{repository}")
        data = await self._make_request(
            "GET",
            f"/repos/{username}/{repository}/contributors",
            params={"per_page": count},
        )

        contributors: list[GitHubContributor] = []
        for item in data:
            contributors.append(
                GitHubContributor(
                    login=item.get("login", "Unknown"),
                    contributions=item.get("contributions", 0),
                    html_url=item.get("html_url"),
                    avatar_url=item.get("avatar_url"),
                )
            )
        return contributors

    async def get_latest_release(
        self,
        username: str,
        repository: str,
    ) -> GitHubRelease:
        """
        Get the latest release of a repository.

        Args:
            username: Repository owner.
            repository: Repository name.

        Returns:
            GitHubRelease model.
        """
        logger.info(f"Fetching latest release for {username}/{repository}")
        data = await self._make_request(
            "GET",
            f"/repos/{username}/{repository}/releases/latest",
        )

        return GitHubRelease(
            tag_name=data.get("tag_name", ""),
            name=data.get("name"),
            published_at=data.get("published_at"),
            html_url=data.get("html_url"),
            body=data.get("body")[:1000] if data.get("body") else None,  # Limit release notes length
            is_prerelease=data.get("prerelease", False),
        )

