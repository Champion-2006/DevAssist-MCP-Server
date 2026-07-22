"""
Unit tests for the GitHub service layer.

Tests all GitHubService methods with mocked httpx responses
to ensure correct data parsing, error handling, and edge cases.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.github_service import GitHubService
from utils.exceptions import GitHubAPIError


@pytest.fixture
def github_service() -> GitHubService:
    """Create a GitHubService instance for testing."""
    return GitHubService(token="test_token_123")


def _mock_response(
    status_code: int = 200,
    json_data: dict | list | None = None,
    headers: dict | None = None,
    text: str = "",
) -> MagicMock:
    """Create a mock httpx response."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.headers = headers or {
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Limit": "5000",
    }
    response.text = text
    return response


@pytest.mark.asyncio
async def test_get_user_profile(github_service, mock_github_user_response):
    """Test fetching a GitHub user profile."""
    mock_resp = _mock_response(json_data=mock_github_user_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await github_service.get_user_profile("octocat")

        assert result.login == "octocat"
        assert result.name == "The Octocat"
        assert result.followers == 20000
        assert result.public_repos == 42


@pytest.mark.asyncio
async def test_get_repo_info(github_service, mock_github_repo_response):
    """Test fetching repository information."""
    mock_resp = _mock_response(json_data=mock_github_repo_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await github_service.get_repo_info("octocat", "Hello-World")

        assert result.name == "Hello-World"
        assert result.stars == 2500
        assert result.language == "Python"
        assert result.forks == 450


@pytest.mark.asyncio
async def test_get_latest_commits(github_service, mock_github_commits_response):
    """Test fetching latest commits."""
    mock_resp = _mock_response(json_data=mock_github_commits_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await github_service.get_latest_commits(
            "octocat", "Hello-World", count=2
        )

        assert len(result) == 2
        assert result[0].message == "Fix critical bug in authentication module"
        assert result[0].author_name == "The Octocat"


@pytest.mark.asyncio
async def test_get_repo_stats(github_service, mock_github_repo_response):
    """Test fetching aggregated repo statistics."""
    mock_resp = _mock_response(json_data=mock_github_repo_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await github_service.get_repo_stats("octocat", "Hello-World")

        assert result.stars == 2500
        assert result.forks == 450
        assert result.language == "Python"
        assert result.repository == "octocat/Hello-World"


@pytest.mark.asyncio
async def test_get_pull_requests(github_service, mock_github_prs_response):
    """Test fetching pull requests."""
    mock_resp = _mock_response(json_data=mock_github_prs_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await github_service.get_pull_requests(
            "octocat", "Hello-World"
        )

        assert len(result) == 1
        assert result[0].title == "Add dark mode support"
        assert result[0].state == "open"
        assert result[0].number == 1347


@pytest.mark.asyncio
async def test_get_issues(github_service, mock_github_issues_response):
    """Test fetching issues (excluding PRs)."""
    mock_resp = _mock_response(json_data=mock_github_issues_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await github_service.get_issues("octocat", "Hello-World")

        assert len(result) == 1
        assert result[0].title == "Login page returns 500 error"
        assert "bug" in result[0].labels


@pytest.mark.asyncio
async def test_error_handling_404(github_service):
    """Test 404 Not Found error handling."""
    mock_resp = _mock_response(status_code=404)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(GitHubAPIError) as exc_info:
            await github_service.get_user_profile("nonexistent_user_xyz")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_error_handling_403_rate_limit(github_service):
    """Test 403 rate limit error handling."""
    mock_resp = _mock_response(
        status_code=403,
        headers={
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Limit": "60",
        },
    )

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(GitHubAPIError) as exc_info:
            await github_service.get_user_profile("octocat")

        assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_error_handling_500(github_service):
    """Test 500 Internal Server Error handling."""
    mock_resp = _mock_response(
        status_code=500,
        text="Internal Server Error",
    )

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.request = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(GitHubAPIError) as exc_info:
            await github_service.get_user_profile("octocat")

        assert exc_info.value.status_code == 500
