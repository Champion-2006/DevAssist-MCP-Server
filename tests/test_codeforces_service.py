"""
Unit tests for the Codeforces service layer.

Tests all CodeforcesService methods with mocked httpx responses
to ensure correct data parsing, analysis logic, and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.codeforces_service import CodeforcesService
from utils.exceptions import CodeforcesAPIError


@pytest.fixture
def cf_service() -> CodeforcesService:
    """Create a CodeforcesService instance for testing."""
    return CodeforcesService()


def _mock_response(
    status_code: int = 200,
    json_data: dict | list | None = None,
) -> MagicMock:
    """Create a mock httpx response."""
    response = MagicMock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.text = ""
    return response


@pytest.mark.asyncio
async def test_get_user_profile(cf_service, mock_cf_user_response):
    """Test fetching a Codeforces user profile."""
    mock_resp = _mock_response(json_data=mock_cf_user_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await cf_service.get_user_profile("tourist")

        assert result.handle == "tourist"
        assert result.rating == 3500
        assert result.max_rating == 3900
        assert result.rank == "legendary grandmaster"


@pytest.mark.asyncio
async def test_get_contest_history(cf_service, mock_cf_rating_response):
    """Test fetching contest history (most recent first)."""
    mock_resp = _mock_response(json_data=mock_cf_rating_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await cf_service.get_contest_history("tourist", count=2)

        assert len(result) == 2
        # Most recent first
        assert result[0].contest_name == "Codeforces Round #900"
        assert result[0].new_rating == 3500


@pytest.mark.asyncio
async def test_get_recent_submissions(cf_service, mock_cf_submissions_response):
    """Test fetching recent submissions with problem details."""
    mock_resp = _mock_response(json_data=mock_cf_submissions_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await cf_service.get_recent_submissions("tourist", count=3)

        assert len(result) == 3
        assert result[0].problem_name == "Cover in Water"
        assert result[0].verdict == "OK"
        assert result[1].verdict == "WRONG_ANSWER"


@pytest.mark.asyncio
async def test_get_rating_history(cf_service, mock_cf_rating_response):
    """Test fetching complete rating history."""
    mock_resp = _mock_response(json_data=mock_cf_rating_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await cf_service.get_rating_history("tourist")

        assert len(result) == 3
        assert result[0].new_rating == 1500
        assert result[0].old_rating == 0
        assert result[0].rating_change == 1500


@pytest.mark.asyncio
async def test_analyze_weak_topics(cf_service):
    """Test weak topic analysis from submissions."""
    # Create mock submissions with enough data for analysis
    submissions_data = {
        "status": "OK",
        "result": [],
    }

    # Add submissions: 5 wrong answers for 'geometry', 5 correct for 'math'
    for i in range(5):
        submissions_data["result"].append({
            "id": 300000 + i,
            "contestId": 2000 + i,
            "problem": {
                "contestId": 2000 + i,
                "index": "A",
                "name": f"Geometry Problem {i}",
                "rating": 1500,
                "tags": ["geometry"],
            },
            "verdict": "WRONG_ANSWER",
            "programmingLanguage": "Python 3",
            "timeConsumedMillis": 100,
            "memoryConsumedBytes": 256000,
        })
        submissions_data["result"].append({
            "id": 400000 + i,
            "contestId": 3000 + i,
            "problem": {
                "contestId": 3000 + i,
                "index": "A",
                "name": f"Math Problem {i}",
                "rating": 1200,
                "tags": ["math"],
            },
            "verdict": "OK",
            "programmingLanguage": "Python 3",
            "timeConsumedMillis": 50,
            "memoryConsumedBytes": 128000,
        })

    mock_resp = _mock_response(json_data=submissions_data)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await cf_service.analyze_weak_topics("testuser")

        # Geometry should be identified as weak (0% success rate)
        weak_tags = [wt.tag for wt in result]
        assert "geometry" in weak_tags

        geometry_topic = next(wt for wt in result if wt.tag == "geometry")
        assert geometry_topic.success_rate == 0.0
        assert geometry_topic.failed == 5


@pytest.mark.asyncio
async def test_analyze_weak_topics_no_weak_areas(cf_service):
    """Test weak topic analysis when user has high success rate."""
    submissions_data = {
        "status": "OK",
        "result": [],
    }
    # All successful submissions
    for i in range(5):
        submissions_data["result"].append({
            "id": 500000 + i,
            "contestId": 4000 + i,
            "problem": {
                "contestId": 4000 + i,
                "index": "A",
                "name": f"Easy Problem {i}",
                "rating": 800,
                "tags": ["implementation"],
            },
            "verdict": "OK",
            "programmingLanguage": "Python 3",
            "timeConsumedMillis": 30,
            "memoryConsumedBytes": 64000,
        })

    mock_resp = _mock_response(json_data=submissions_data)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        result = await cf_service.analyze_weak_topics("stronguser")
        assert len(result) == 0


@pytest.mark.asyncio
async def test_error_handling_user_not_found(cf_service):
    """Test handling of user not found error."""
    error_response = {
        "status": "FAILED",
        "comment": "handles: User with handle nonexistent not found",
    }
    mock_resp = _mock_response(json_data=error_response)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(CodeforcesAPIError) as exc_info:
            await cf_service.get_user_profile("nonexistent")

        assert "error" in exc_info.value.message.lower()


@pytest.mark.asyncio
async def test_error_handling_server_error(cf_service):
    """Test handling of Codeforces server errors."""
    mock_resp = _mock_response(status_code=500)

    with patch("httpx.AsyncClient") as MockClient:
        instance = AsyncMock()
        instance.get = AsyncMock(return_value=mock_resp)
        instance.__aenter__ = AsyncMock(return_value=instance)
        instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = instance

        with pytest.raises(CodeforcesAPIError) as exc_info:
            await cf_service.get_user_profile("tourist")

        assert exc_info.value.status_code == 500
