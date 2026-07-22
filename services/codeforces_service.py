"""
Codeforces API service layer.

Provides async methods to interact with the Codeforces API
with profile analysis, weak topic detection, and problem recommendations.
"""

import json
from collections import defaultdict
from typing import Any

import httpx

from config import settings
from models.cp_models import (
    CodeforcesContest,
    CodeforcesSubmission,
    CodeforcesUser,
    ProblemRecommendation,
    RatingChange,
    WeakTopic,
)
from utils.exceptions import CodeforcesAPIError
from utils.logger import get_logger

logger = get_logger(__name__)


class CodeforcesService:
    """Service for interacting with the Codeforces API."""

    def __init__(self, base_url: str | None = None) -> None:
        """
        Initialize the Codeforces service.

        Args:
            base_url: Codeforces API base URL. Defaults to settings.
        """
        self.base_url = (
            base_url or settings.codeforces_api_base_url
        ).rstrip("/")
        self.headers: dict[str, str] = {
            "User-Agent": f"DevAssist-MCP/{settings.server_version}",
            "Accept": "application/json",
        }

    async def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """
        Make a request to the Codeforces API.

        Args:
            endpoint: API endpoint (e.g., 'user.info').
            params: Query parameters.

        Returns:
            The 'result' field from the API response.

        Raises:
            CodeforcesAPIError: If the API request fails.
        """
        url = f"{self.base_url}/{endpoint}"
        logger.debug(f"Codeforces API request: GET {url}")

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=settings.http_timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url, params=params)

                if response.status_code != 200:
                    raise CodeforcesAPIError(
                        message=f"API request failed with status {response.status_code}",
                        status_code=response.status_code,
                        details={"endpoint": endpoint},
                    )

                data = response.json()

                if data.get("status") != "OK":
                    comment = data.get("comment", "Unknown error")
                    raise CodeforcesAPIError(
                        message=f"API returned error: {comment}",
                        status_code=400,
                        details={
                            "endpoint": endpoint,
                            "comment": comment,
                        },
                    )

                return data.get("result")

        except httpx.TimeoutException as e:
            logger.error(f"Codeforces API request timed out: {url}")
            raise CodeforcesAPIError(
                message=f"Request timed out: {endpoint}",
                status_code=408,
            ) from e
        except httpx.ConnectError as e:
            logger.error(f"Failed to connect to Codeforces API: {e}")
            raise CodeforcesAPIError(
                message="Failed to connect to Codeforces API",
                status_code=503,
            ) from e
        except CodeforcesAPIError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Codeforces API request: {e}")
            raise CodeforcesAPIError(
                message=f"Unexpected error: {str(e)}",
                status_code=500,
            ) from e

    async def get_user_profile(self, username: str) -> CodeforcesUser:
        """
        Get a Codeforces user's profile.

        Args:
            username: Codeforces handle.

        Returns:
            CodeforcesUser model with profile data.
        """
        logger.info(f"Fetching Codeforces profile for: {username}")
        result = await self._make_request(
            "user.info", params={"handles": username}
        )

        if not result or len(result) == 0:
            raise CodeforcesAPIError(
                message=f"User '{username}' not found",
                status_code=404,
            )

        return CodeforcesUser.model_validate(result[0])

    async def get_contest_history(
        self, username: str, count: int = 10
    ) -> list[CodeforcesContest]:
        """
        Get a user's contest history.

        Args:
            username: Codeforces handle.
            count: Number of recent contests to return (default: 10).

        Returns:
            List of CodeforcesContest models (most recent first).
        """
        logger.info(f"Fetching contest history for: {username}")
        result = await self._make_request(
            "user.rating", params={"handle": username}
        )

        contests = [
            CodeforcesContest.model_validate(item) for item in result
        ]

        # Return most recent contests first
        contests.reverse()
        return contests[:count]

    async def get_recent_submissions(
        self, username: str, count: int = 10
    ) -> list[CodeforcesSubmission]:
        """
        Get a user's recent submissions.

        Args:
            username: Codeforces handle.
            count: Number of submissions to return (default: 10).

        Returns:
            List of CodeforcesSubmission models.
        """
        logger.info(f"Fetching recent {count} submissions for: {username}")
        result = await self._make_request(
            "user.status",
            params={"handle": username, "from": 1, "count": count},
        )

        submissions: list[CodeforcesSubmission] = []
        for item in result:
            problem = item.get("problem", {})
            submissions.append(
                CodeforcesSubmission(
                    id=item.get("id", 0),
                    contestId=item.get("contestId"),
                    problem_name=problem.get("name", ""),
                    problem_index=problem.get("index", ""),
                    problem_rating=problem.get("rating"),
                    problem_tags=problem.get("tags", []),
                    verdict=item.get("verdict"),
                    programmingLanguage=item.get("programmingLanguage", ""),
                    timeConsumedMillis=item.get("timeConsumedMillis", 0),
                    memoryConsumedBytes=item.get("memoryConsumedBytes", 0),
                )
            )
        return submissions

    async def get_rating_history(
        self, username: str
    ) -> list[RatingChange]:
        """
        Get a user's complete rating history.

        Args:
            username: Codeforces handle.

        Returns:
            List of RatingChange models chronologically.
        """
        logger.info(f"Fetching rating history for: {username}")
        result = await self._make_request(
            "user.rating", params={"handle": username}
        )

        return [RatingChange.model_validate(item) for item in result]

    async def analyze_weak_topics(
        self, username: str
    ) -> list[WeakTopic]:
        """
        Analyze a user's weak topics based on submission history.

        Fetches all submissions, groups by problem tags, calculates
        success rate per tag, and returns tags with <50% success rate.

        Args:
            username: Codeforces handle.

        Returns:
            List of WeakTopic models sorted by success rate (ascending).
        """
        logger.info(f"Analyzing weak topics for: {username}")

        # Fetch a large batch of submissions for analysis
        result = await self._make_request(
            "user.status",
            params={"handle": username, "from": 1, "count": 500},
        )

        # Track per-tag statistics
        tag_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {"total": 0, "accepted": 0}
        )

        # Track unique problems to avoid counting retries
        seen_problems: set[str] = set()

        for item in result:
            problem = item.get("problem", {})
            verdict = item.get("verdict", "")
            problem_key = (
                f"{problem.get('contestId', '')}_{problem.get('index', '')}"
            )

            # Only count the first attempt per problem
            if problem_key in seen_problems:
                continue
            seen_problems.add(problem_key)

            tags = problem.get("tags", [])
            for tag in tags:
                tag_stats[tag]["total"] += 1
                if verdict == "OK":
                    tag_stats[tag]["accepted"] += 1

        # Build weak topics list (success rate < 50%, min 3 attempts)
        weak_topics: list[WeakTopic] = []
        for tag, stats in tag_stats.items():
            total = stats["total"]
            accepted = stats["accepted"]
            failed = total - accepted

            if total < 3:
                continue

            success_rate = round((accepted / total) * 100, 1)
            if success_rate < 50.0:
                weak_topics.append(
                    WeakTopic(
                        tag=tag,
                        total_attempts=total,
                        successful=accepted,
                        failed=failed,
                        success_rate=success_rate,
                    )
                )

        # Sort by success rate ascending (weakest first)
        weak_topics.sort(key=lambda x: x.success_rate)

        logger.info(f"Found {len(weak_topics)} weak topics for {username}")
        return weak_topics

    async def recommend_problems(
        self, username: str
    ) -> list[ProblemRecommendation]:
        """
        Recommend problems based on weak topics and current rating.

        Fetches the user's profile and weak topics, then finds problems
        from the Codeforces problem set that match the user's weak areas
        and are slightly above their current level.

        Args:
            username: Codeforces handle.

        Returns:
            List of ProblemRecommendation models (up to 10).
        """
        logger.info(f"Generating problem recommendations for: {username}")

        # Get user profile for current rating
        user = await self.get_user_profile(username)
        current_rating = user.rating or 800

        # Get weak topics
        weak_topics = await self.analyze_weak_topics(username)
        weak_tags = {wt.tag for wt in weak_topics}

        # If no weak topics found, use general tags
        if not weak_tags:
            weak_tags = {
                "implementation",
                "math",
                "greedy",
                "dp",
                "sorting",
            }
            logger.info(
                f"No weak topics found for {username}, using general tags"
            )

        # Fetch problems from Codeforces
        result = await self._make_request("problemset.problems")
        problems = result.get("problems", [])

        # Define rating range: current rating - 100 to current rating + 300
        min_rating = max(800, current_rating - 100)
        max_rating = current_rating + 300

        # Get user's solved problems to exclude them
        try:
            submissions = await self._make_request(
                "user.status",
                params={"handle": username, "from": 1, "count": 1000},
            )
            solved_problems: set[str] = set()
            for sub in submissions:
                if sub.get("verdict") == "OK":
                    prob = sub.get("problem", {})
                    solved_key = (
                        f"{prob.get('contestId', '')}_{prob.get('index', '')}"
                    )
                    solved_problems.add(solved_key)
        except Exception:
            solved_problems = set()

        # Filter and score problems
        candidates: list[tuple[float, dict]] = []
        for problem in problems:
            rating = problem.get("rating")
            if rating is None:
                continue
            if not (min_rating <= rating <= max_rating):
                continue

            contest_id = problem.get("contestId")
            index = problem.get("index", "")
            problem_key = f"{contest_id}_{index}"

            # Skip already solved
            if problem_key in solved_problems:
                continue

            tags = set(problem.get("tags", []))
            matching_tags = tags & weak_tags

            if not matching_tags:
                continue

            # Score: more matching weak tags = higher priority
            score = len(matching_tags) * 10 + (1 / max(1, abs(rating - current_rating)))
            candidates.append((score, problem))

        # Sort by score descending and take top 10
        candidates.sort(key=lambda x: x[0], reverse=True)
        top_problems = candidates[:10]

        recommendations: list[ProblemRecommendation] = []
        for _, problem in top_problems:
            contest_id = problem.get("contestId")
            index = problem.get("index", "")
            url = None
            if contest_id:
                url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"

            recommendations.append(
                ProblemRecommendation(
                    name=problem.get("name", ""),
                    contest_id=contest_id,
                    index=index,
                    rating=problem.get("rating"),
                    tags=problem.get("tags", []),
                    url=url,
                )
            )

        logger.info(
            f"Generated {len(recommendations)} recommendations for {username}"
        )
        return recommendations
