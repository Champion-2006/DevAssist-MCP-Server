"""
Shared pytest fixtures for DevAssist MCP tests.

Provides realistic mock API responses for GitHub and Codeforces
to enable reliable, offline unit testing.
"""

import pytest


# ─── GitHub Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_github_user_response() -> dict:
    """Realistic GitHub user API response."""
    return {
        "login": "octocat",
        "id": 1,
        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        "html_url": "https://github.com/octocat",
        "name": "The Octocat",
        "company": "GitHub",
        "blog": "https://github.com/blog",
        "location": "San Francisco",
        "email": "octocat@github.com",
        "bio": "A mysterious cat-octopus hybrid.",
        "public_repos": 42,
        "public_gists": 10,
        "followers": 20000,
        "following": 5,
        "created_at": "2008-01-14T04:33:35Z",
        "updated_at": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_github_repo_response() -> dict:
    """Realistic GitHub repository API response."""
    return {
        "id": 1296269,
        "name": "Hello-World",
        "full_name": "octocat/Hello-World",
        "owner": {"login": "octocat", "id": 1},
        "private": False,
        "html_url": "https://github.com/octocat/Hello-World",
        "description": "My first repository on GitHub!",
        "fork": False,
        "size": 108,
        "stargazers_count": 2500,
        "watchers_count": 2500,
        "language": "Python",
        "has_issues": True,
        "forks_count": 450,
        "open_issues_count": 12,
        "default_branch": "main",
        "topics": ["python", "hello-world", "tutorial"],
        "license": {"name": "MIT License", "spdx_id": "MIT"},
        "created_at": "2011-01-26T19:01:12Z",
        "updated_at": "2024-06-15T10:30:00Z",
    }


@pytest.fixture
def mock_github_commits_response() -> list:
    """Realistic GitHub commits API response."""
    return [
        {
            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
            "html_url": "https://github.com/octocat/Hello-World/commit/6dcb09b5",
            "commit": {
                "author": {
                    "name": "The Octocat",
                    "email": "octocat@github.com",
                    "date": "2024-06-15T10:30:00Z",
                },
                "message": "Fix critical bug in authentication module",
            },
        },
        {
            "sha": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
            "html_url": "https://github.com/octocat/Hello-World/commit/a1b2c3d4",
            "commit": {
                "author": {
                    "name": "The Octocat",
                    "email": "octocat@github.com",
                    "date": "2024-06-14T15:20:00Z",
                },
                "message": "Add unit tests for user service",
            },
        },
    ]


@pytest.fixture
def mock_github_prs_response() -> list:
    """Realistic GitHub pull requests API response."""
    return [
        {
            "id": 1,
            "number": 1347,
            "state": "open",
            "title": "Add dark mode support",
            "user": {"login": "octocat"},
            "body": "This PR adds dark mode support to the dashboard.",
            "created_at": "2024-06-10T09:00:00Z",
            "updated_at": "2024-06-12T14:00:00Z",
            "html_url": "https://github.com/octocat/Hello-World/pull/1347",
        },
    ]


@pytest.fixture
def mock_github_issues_response() -> list:
    """Realistic GitHub issues API response."""
    return [
        {
            "id": 1,
            "number": 42,
            "title": "Login page returns 500 error",
            "user": {"login": "contributor1"},
            "state": "open",
            "body": "When I try to login, I get a 500 error.",
            "labels": [
                {"name": "bug"},
                {"name": "high-priority"},
            ],
            "created_at": "2024-06-01T08:00:00Z",
            "html_url": "https://github.com/octocat/Hello-World/issues/42",
        },
    ]


# ─── Codeforces Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def mock_cf_user_response() -> dict:
    """Realistic Codeforces user.info API response."""
    return {
        "status": "OK",
        "result": [
            {
                "handle": "tourist",
                "rating": 3500,
                "maxRating": 3900,
                "rank": "legendary grandmaster",
                "maxRank": "legendary grandmaster",
                "contribution": 150,
                "friendOfCount": 50000,
                "registrationTimeSeconds": 1265987288,
                "avatar": "https://userpic.codeforces.org/422/avatar/full.jpg",
                "titlePhoto": "https://userpic.codeforces.org/422/title/full.jpg",
                "organization": "ITMO University",
                "city": "Minsk",
                "country": "Belarus",
            }
        ],
    }


@pytest.fixture
def mock_cf_rating_response() -> dict:
    """Realistic Codeforces user.rating API response."""
    return {
        "status": "OK",
        "result": [
            {
                "contestId": 1,
                "contestName": "Codeforces Beta Round #1",
                "handle": "tourist",
                "rank": 1,
                "ratingUpdateTimeSeconds": 1266588000,
                "oldRating": 0,
                "newRating": 1500,
            },
            {
                "contestId": 2,
                "contestName": "Codeforces Beta Round #2",
                "handle": "tourist",
                "rank": 3,
                "ratingUpdateTimeSeconds": 1267797600,
                "oldRating": 1500,
                "newRating": 1650,
            },
            {
                "contestId": 100,
                "contestName": "Codeforces Round #900",
                "handle": "tourist",
                "rank": 1,
                "ratingUpdateTimeSeconds": 1700000000,
                "oldRating": 3400,
                "newRating": 3500,
            },
        ],
    }


@pytest.fixture
def mock_cf_submissions_response() -> dict:
    """Realistic Codeforces user.status API response."""
    return {
        "status": "OK",
        "result": [
            {
                "id": 200001,
                "contestId": 1900,
                "creationTimeSeconds": 1700000000,
                "problem": {
                    "contestId": 1900,
                    "index": "A",
                    "name": "Cover in Water",
                    "rating": 1000,
                    "tags": ["implementation", "greedy"],
                },
                "programmingLanguage": "GNU C++20 (64)",
                "verdict": "OK",
                "timeConsumedMillis": 31,
                "memoryConsumedBytes": 0,
                "passedTestCount": 10,
            },
            {
                "id": 200002,
                "contestId": 1900,
                "creationTimeSeconds": 1699999000,
                "problem": {
                    "contestId": 1900,
                    "index": "B",
                    "name": "Collecting Game",
                    "rating": 1200,
                    "tags": ["binary search", "sorting"],
                },
                "programmingLanguage": "GNU C++20 (64)",
                "verdict": "WRONG_ANSWER",
                "timeConsumedMillis": 15,
                "memoryConsumedBytes": 0,
                "passedTestCount": 3,
            },
            {
                "id": 200003,
                "contestId": 1899,
                "creationTimeSeconds": 1699998000,
                "problem": {
                    "contestId": 1899,
                    "index": "C",
                    "name": "Yarik and Array",
                    "rating": 1500,
                    "tags": ["dp", "greedy"],
                },
                "programmingLanguage": "GNU C++20 (64)",
                "verdict": "WRONG_ANSWER",
                "timeConsumedMillis": 46,
                "memoryConsumedBytes": 0,
                "passedTestCount": 5,
            },
        ],
    }


@pytest.fixture
def mock_cf_problems_response() -> dict:
    """Realistic Codeforces problemset.problems API response."""
    return {
        "status": "OK",
        "result": {
            "problems": [
                {
                    "contestId": 1950,
                    "index": "A",
                    "name": "Stair, Peak, or Neither?",
                    "rating": 800,
                    "tags": ["implementation"],
                },
                {
                    "contestId": 1950,
                    "index": "C",
                    "name": "Clock Conversion",
                    "rating": 1000,
                    "tags": ["implementation", "math"],
                },
                {
                    "contestId": 1949,
                    "index": "B",
                    "name": "Fireworks",
                    "rating": 900,
                    "tags": ["math", "greedy"],
                },
            ],
            "problemStatistics": [
                {"contestId": 1950, "index": "A", "solvedCount": 50000},
                {"contestId": 1950, "index": "C", "solvedCount": 30000},
                {"contestId": 1949, "index": "B", "solvedCount": 40000},
            ],
        },
    }
