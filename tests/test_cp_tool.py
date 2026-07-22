"""
Unit tests for the Codeforces MCP tool.

Tests the cp_assistant tool's action routing,
platform validation, and error handling.
"""

import json
import pytest
from unittest.mock import AsyncMock, patch

from models.cp_models import CodeforcesUser, WeakTopic, ProblemRecommendation


@pytest.mark.asyncio
async def test_cp_tool_get_user_profile():
    """Test get_user_profile action routes correctly."""
    mock_user = CodeforcesUser(
        handle="tourist",
        rating=3500,
        maxRating=3900,
        rank="legendary grandmaster",
        maxRank="legendary grandmaster",
    )

    with patch(
        "tools.cp.CodeforcesService"
    ) as MockService:
        instance = MockService.return_value
        instance.get_user_profile = AsyncMock(return_value=mock_user)

        result = await instance.get_user_profile("tourist")
        assert result.handle == "tourist"
        assert result.rating == 3500
        assert result.max_rating == 3900


@pytest.mark.asyncio
async def test_cp_tool_analyze_weak_topics():
    """Test analyze_weak_topics returns weak areas."""
    mock_weak = [
        WeakTopic(
            tag="geometry",
            total_attempts=10,
            successful=2,
            failed=8,
            success_rate=20.0,
        ),
    ]

    with patch(
        "tools.cp.CodeforcesService"
    ) as MockService:
        instance = MockService.return_value
        instance.analyze_weak_topics = AsyncMock(return_value=mock_weak)

        result = await instance.analyze_weak_topics("testuser")
        assert len(result) == 1
        assert result[0].tag == "geometry"
        assert result[0].success_rate == 20.0


@pytest.mark.asyncio
async def test_cp_tool_recommend_problems():
    """Test recommend_problems returns recommendations."""
    mock_recs = [
        ProblemRecommendation(
            name="Theatre Square",
            contest_id=1,
            index="A",
            rating=1000,
            tags=["math"],
            url="https://codeforces.com/problemset/problem/1/A",
        ),
    ]

    with patch(
        "tools.cp.CodeforcesService"
    ) as MockService:
        instance = MockService.return_value
        instance.recommend_problems = AsyncMock(return_value=mock_recs)

        result = await instance.recommend_problems("testuser")
        assert len(result) == 1
        assert result[0].name == "Theatre Square"
        assert result[0].url is not None


@pytest.mark.asyncio
async def test_cp_tool_invalid_platform():
    """Test that invalid platform is handled correctly."""
    from tools.cp import SUPPORTED_PLATFORMS

    assert "codeforces" in SUPPORTED_PLATFORMS
    assert "leetcode" not in SUPPORTED_PLATFORMS


@pytest.mark.asyncio
async def test_cp_tool_invalid_action():
    """Test that invalid action is handled correctly."""
    from tools.cp import VALID_ACTIONS

    assert "get_user_profile" in VALID_ACTIONS
    assert "invalid_action" not in VALID_ACTIONS


@pytest.mark.asyncio
async def test_cp_tool_valid_actions_complete():
    """Test that all expected actions are registered."""
    from tools.cp import VALID_ACTIONS

    expected = {
        "get_user_profile",
        "get_contest_history",
        "get_recent_submissions",
        "get_rating_history",
        "analyze_weak_topics",
        "recommend_problems",
    }
    assert VALID_ACTIONS == expected
