"""
Competitive Programming MCP tool registration.

Registers the cp_assistant tool with the FastMCP server,
providing AI agents with access to Codeforces profile data,
contest history, weak topic analysis, and problem recommendations.
"""

import json

from mcp.server.fastmcp import FastMCP

from services.codeforces_service import CodeforcesService
from utils.exceptions import CodeforcesAPIError
from utils.logger import get_logger

logger = get_logger(__name__)

VALID_ACTIONS = {
    "get_user_profile",
    "get_contest_history",
    "get_recent_submissions",
    "get_rating_history",
    "analyze_weak_topics",
    "recommend_problems",
}

SUPPORTED_PLATFORMS = {"codeforces"}


def register_cp_tools(mcp: FastMCP) -> None:
    """
    Register all competitive programming tools on the MCP server.

    Args:
        mcp: FastMCP server instance.
    """

    @mcp.tool()
    async def cp_assistant(
        action: str,
        username: str,
        platform: str = "codeforces",
        count: int = 10,
    ) -> str:
        """Competitive programming assistant for Codeforces.

        Provides real-time access to competitive programming data including
        user profiles, contest history, submissions, rating changes,
        weak topic analysis, and personalized problem recommendations.

        Available actions:
        - get_user_profile: Get user profile with rating and rank
        - get_contest_history: Get past contest participation and results
        - get_recent_submissions: Get recent problem submissions
        - get_rating_history: Get rating changes over time
        - analyze_weak_topics: Identify weak areas from submission history
        - recommend_problems: Get personalized problem recommendations

        Args:
            action: The action to perform (see available actions above)
            username: Codeforces username/handle
            platform: Platform name, currently only 'codeforces' (default: 'codeforces')
            count: Number of items to return for list operations (default: 10)

        Returns:
            JSON-formatted string with the requested data.
        """
        logger.info(
            f"cp_assistant called: action={action}, "
            f"username={username}, platform={platform}"
        )

        # Validate platform
        if platform.lower() not in SUPPORTED_PLATFORMS:
            return json.dumps(
                {
                    "error": f"Unsupported platform: '{platform}'",
                    "supported_platforms": sorted(SUPPORTED_PLATFORMS),
                    "note": "Currently only Codeforces is supported. "
                    "LeetCode and CodeChef support coming soon!",
                },
                indent=2,
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

        try:
            service = CodeforcesService()

            if action == "get_user_profile":
                result = await service.get_user_profile(username)
                return result.model_dump_json(indent=2)

            elif action == "get_contest_history":
                results = await service.get_contest_history(username, count)
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "get_recent_submissions":
                results = await service.get_recent_submissions(
                    username, count
                )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "get_rating_history":
                results = await service.get_rating_history(username)
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "analyze_weak_topics":
                results = await service.analyze_weak_topics(username)
                if not results:
                    return json.dumps(
                        {
                            "message": f"No significant weak topics found for '{username}'.",
                            "note": "This could mean the user has a good "
                            "success rate across all topics, or there "
                            "aren't enough submissions for analysis.",
                        },
                        indent=2,
                    )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            elif action == "recommend_problems":
                results = await service.recommend_problems(username)
                if not results:
                    return json.dumps(
                        {
                            "message": f"No problem recommendations available for '{username}'.",
                            "note": "Try adjusting the rating range or "
                            "the user may have solved most problems "
                            "in their weak areas.",
                        },
                        indent=2,
                    )
                return json.dumps(
                    [r.model_dump() for r in results], indent=2
                )

            else:
                return json.dumps({"error": "Unknown action"}, indent=2)

        except CodeforcesAPIError as e:
            logger.error(f"Codeforces API error: {e.message}")
            return json.dumps(e.to_dict(), indent=2)
        except Exception as e:
            logger.error(f"Unexpected error in cp_assistant: {e}")
            return json.dumps(
                {
                    "error": "An unexpected error occurred",
                    "details": str(e),
                },
                indent=2,
            )

    logger.info("Competitive programming tools registered successfully")
