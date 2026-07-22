"""
GitHub MCP tool registration.

Registers the github_assistant tool with the FastMCP server,
providing AI agents with access to GitHub repository and user data.
"""

import json

from mcp.server.fastmcp import FastMCP

from services.github_service import GitHubService
from utils.exceptions import GitHubAPIError, ValidationError
from utils.logger import get_logger

logger = get_logger(__name__)

# Actions that require a repository parameter
REPO_REQUIRED_ACTIONS = {
    "get_repo_info",
    "get_latest_commits",
    "get_repo_stats",
    "get_pull_requests",
    "get_issues",
    "get_repo_languages",
    "get_repo_contributors",
    "get_latest_release",
}

VALID_ACTIONS = {
    "get_user_profile",
    "get_user_repos",
    "get_user_activity",
    "get_repo_info",
    "get_latest_commits",
    "get_repo_stats",
    "get_repo_languages",
    "get_repo_contributors",
    "get_latest_release",
    "get_pull_requests",
    "get_issues",
}


def register_github_tools(mcp: FastMCP) -> None:
    """
    Register all GitHub-related tools on the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool()
    async def github_assistant(
        action: str,
        username: str,
        repository: str | None = None,
        count: int = 5,
        state: str = "open",
        sort: str = "updated",
    ) -> str:
        """GitHub assistant tool for comprehensive developer and repository insights.

        Provides real-time access to GitHub user profiles, repositories owned by a user,
        user activity feeds, commit logs, languages, top contributors, releases, PRs, and issues.

        Available actions:
        - get_user_profile: Get user profile details (followers, bio, public repos)
        - get_user_repos: List public repositories owned by a user (supports count & sort)
        - get_user_activity: Get recent activity/events by a user (pushes, PRs, stars)
        - get_repo_info: Get repository details (stars, forks, topics, license)
        - get_latest_commits: Get recent commits for a repo
        - get_repo_stats: Get aggregated stats for a repository
        - get_repo_languages: Get language breakdown with percentages for a repo
        - get_repo_contributors: Get top contributors for a repository
        - get_latest_release: Get latest release version and notes for a repo
        - get_pull_requests: Get pull requests for a repo
        - get_issues: Get issues for a repo

        Args:
            action: The action to perform (see available actions above)
            username: GitHub username
            repository: Repository name (required for repo-specific actions)
            count: Number of items to return for list operations (default: 5)
            state: Filter state for PRs/issues - 'open', 'closed', 'all' (default: 'open')
            sort: Sort order for user repos - 'updated', 'created', 'pushed' (default: 'updated')

        Returns:
            JSON-formatted string with the requested data.
        """
        logger.info(
            f"github_assistant called: action={action}, "
            f"username={username}, repository={repository}"
        )

        # Validate action
        if action not in VALID_ACTIONS:
            return json.dumps(
                {
                    "error": f"Invalid action: '{action}'",
                    "valid_actions": sorted(VALID_ACTIONS),
                },
                indent=2,
            )

        # Validate repository is provided for repo-specific actions
        if action in REPO_REQUIRED_ACTIONS and not repository:
            return json.dumps(
                {
                    "error": f"Action '{action}' requires a 'repository' parameter",
                    "example": {
                        "action": action,
                        "username": username,
                        "repository": "my-repo",
                    },
                },
                indent=2,
            )

        try:
            service = GitHubService()

            if action == "get_user_profile":
                result = await service.get_user_profile(username)
                return result.model_dump_json(indent=2)

            elif action == "get_user_repos":
                results = await service.get_user_repos(
                    username, count, sort
                )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "get_user_activity":
                results = await service.get_user_activity(username, count)
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "get_repo_info":
                result = await service.get_repo_info(username, repository)  # type: ignore[arg-type]
                return result.model_dump_json(indent=2)

            elif action == "get_latest_commits":
                results = await service.get_latest_commits(
                    username, repository, count  # type: ignore[arg-type]
                )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "get_repo_stats":
                result = await service.get_repo_stats(username, repository)  # type: ignore[arg-type]
                return result.model_dump_json(indent=2)

            elif action == "get_repo_languages":
                result = await service.get_repo_languages(
                    username, repository  # type: ignore[arg-type]
                )
                return json.dumps(result, indent=2)

            elif action == "get_repo_contributors":
                results = await service.get_repo_contributors(
                    username, repository, count  # type: ignore[arg-type]
                )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "get_latest_release":
                result = await service.get_latest_release(
                    username, repository  # type: ignore[arg-type]
                )
                return result.model_dump_json(indent=2)

            elif action == "get_pull_requests":
                results = await service.get_pull_requests(
                    username, repository, state  # type: ignore[arg-type]
                )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "get_issues":
                results = await service.get_issues(
                    username, repository, state  # type: ignore[arg-type]
                )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            else:
                return json.dumps({"error": "Unknown action"}, indent=2)

        except GitHubAPIError as e:
            logger.error(f"GitHub API error: {e.message}")
            return json.dumps(e.to_dict(), indent=2)
        except Exception as e:
            logger.error(f"Unexpected error in github_assistant: {e}")
            return json.dumps(
                {
                    "error": "An unexpected error occurred",
                    "details": str(e),
                },
                indent=2,
            )

    logger.info("GitHub tools registered successfully")
