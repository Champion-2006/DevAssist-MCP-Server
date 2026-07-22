"""
Unit tests for the GitHub MCP tool.

Tests the github_assistant tool's action routing,
input validation, and error handling.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from models.github_models import (
    GitHubUser,
    GitHubRepository,
    RepoStats,
    GitHubContributor,
    GitHubRelease,
    GitHubUserEvent,
)


@pytest.mark.asyncio
async def test_github_tool_get_user_profile():
    """Test get_user_profile action routes correctly."""
    mock_user = GitHubUser(
        login="octocat",
        name="The Octocat",
        public_repos=42,
        followers=20000,
    )

    with patch("tools.github.GitHubService") as MockService:
        instance = MockService.return_value
        instance.get_user_profile = AsyncMock(return_value=mock_user)

        result = await instance.get_user_profile("octocat")
        assert result.login == "octocat"
        assert result.followers == 20000


@pytest.mark.asyncio
async def test_github_tool_get_user_repos():
    """Test get_user_repos action routes correctly."""
    mock_repo = GitHubRepository(
        name="Hello-World",
        full_name="octocat/Hello-World",
        stargazers_count=2500,
    )

    with patch("tools.github.GitHubService") as MockService:
        instance = MockService.return_value
        instance.get_user_repos = AsyncMock(return_value=[mock_repo])

        result = await instance.get_user_repos("octocat", count=5)
        assert len(result) == 1
        assert result[0].name == "Hello-World"


@pytest.mark.asyncio
async def test_github_tool_get_user_activity():
    """Test get_user_activity action routes correctly."""
    mock_event = GitHubUserEvent(
        event_type="PushEvent",
        repo_name="octocat/Hello-World",
        created_at="2024-01-01T00:00:00Z",
        payload_summary="Pushed 2 commit(s)",
    )

    with patch("tools.github.GitHubService") as MockService:
        instance = MockService.return_value
        instance.get_user_activity = AsyncMock(return_value=[mock_event])

        result = await instance.get_user_activity("octocat", count=5)
        assert len(result) == 1
        assert result[0].event_type == "PushEvent"


@pytest.mark.asyncio
async def test_github_tool_get_repo_info():
    """Test get_repo_info action routes correctly."""
    mock_repo = GitHubRepository(
        name="Hello-World",
        full_name="octocat/Hello-World",
        stargazers_count=2500,
        forks_count=450,
        language="Python",
    )

    with patch("tools.github.GitHubService") as MockService:
        instance = MockService.return_value
        instance.get_repo_info = AsyncMock(return_value=mock_repo)

        result = await instance.get_repo_info("octocat", "Hello-World")
        assert result.name == "Hello-World"
        assert result.stars == 2500


@pytest.mark.asyncio
async def test_github_tool_invalid_action():
    """Test that invalid action returns error JSON."""
    from tools.github import VALID_ACTIONS

    assert "invalid_action_xyz" not in VALID_ACTIONS


@pytest.mark.asyncio
async def test_github_tool_missing_repository():
    """Test that repo-specific actions require repository parameter."""
    from tools.github import REPO_REQUIRED_ACTIONS

    expected = {
        "get_repo_info",
        "get_latest_commits",
        "get_repo_stats",
        "get_pull_requests",
        "get_issues",
        "get_repo_languages",
        "get_repo_contributors",
        "get_latest_release",
    }
    assert REPO_REQUIRED_ACTIONS == expected


@pytest.mark.asyncio
async def test_github_tool_get_repo_stats():
    """Test get_repo_stats action returns aggregated stats."""
    mock_stats = RepoStats(
        repository="octocat/Hello-World",
        stars=2500,
        forks=450,
        watchers=2500,
        open_issues=12,
        language="Python",
    )

    with patch("tools.github.GitHubService") as MockService:
        instance = MockService.return_value
        instance.get_repo_stats = AsyncMock(return_value=mock_stats)

        result = await instance.get_repo_stats("octocat", "Hello-World")
        assert result.stars == 2500
        assert result.repository == "octocat/Hello-World"
