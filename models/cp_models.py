"""
Pydantic data models for Codeforces API responses.

These models provide type-safe representations of Codeforces API data
with automatic validation, weak topic analysis, and problem recommendations.
"""

from pydantic import BaseModel, Field


class CodeforcesUser(BaseModel):
    """Represents a Codeforces user profile."""

    handle: str
    rating: int = 0
    max_rating: int = Field(0, alias="maxRating")
    rank: str | None = None
    max_rank: str | None = Field(None, alias="maxRank")
    contribution: int = 0
    friend_of_count: int = Field(0, alias="friendOfCount")
    registration_time: int = Field(0, alias="registrationTimeSeconds")
    avatar: str | None = None
    title_photo: str | None = Field(None, alias="titlePhoto")
    organization: str | None = None
    city: str | None = None
    country: str | None = None

    model_config = {"populate_by_name": True}


class CodeforcesContest(BaseModel):
    """Represents a Codeforces contest participation entry."""

    contest_id: int = Field(alias="contestId")
    contest_name: str = Field(alias="contestName")
    rank: int = 0
    old_rating: int = Field(0, alias="oldRating")
    new_rating: int = Field(0, alias="newRating")
    rating_change: int = 0

    model_config = {"populate_by_name": True}

    def model_post_init(self, __context: object) -> None:
        """Calculate rating change if not provided."""
        if self.rating_change == 0 and (self.new_rating != 0 or self.old_rating != 0):
            self.rating_change = self.new_rating - self.old_rating


class CodeforcesSubmission(BaseModel):
    """Represents a Codeforces problem submission."""

    id: int
    contest_id: int | None = Field(None, alias="contestId")
    problem_name: str = ""
    problem_index: str = ""
    problem_rating: int | None = None
    problem_tags: list[str] = []
    verdict: str | None = None
    programming_language: str = Field("", alias="programmingLanguage")
    time_consumed: int = Field(0, alias="timeConsumedMillis")
    memory_consumed: int = Field(0, alias="memoryConsumedBytes")

    model_config = {"populate_by_name": True}


class RatingChange(BaseModel):
    """Represents a rating change from a contest."""

    contest_id: int = Field(alias="contestId")
    contest_name: str = Field(alias="contestName")
    new_rating: int = Field(alias="newRating")
    old_rating: int = Field(alias="oldRating")
    rank: int = 0

    model_config = {"populate_by_name": True}

    @property
    def rating_change(self) -> int:
        """Calculate the rating change."""
        return self.new_rating - self.old_rating


class WeakTopic(BaseModel):
    """Represents a weak topic identified from submission analysis."""

    tag: str
    total_attempts: int
    successful: int
    failed: int
    success_rate: float


class ProblemRecommendation(BaseModel):
    """Represents a recommended problem for practice."""

    name: str
    contest_id: int | None = None
    index: str | None = None
    rating: int | None = None
    tags: list[str] = []
    url: str | None = None


class UserAnalysis(BaseModel):
    """Comprehensive user analysis with weak topics and recommendations."""

    handle: str
    current_rating: int
    max_rating: int
    rank: str | None = None
    weak_topics: list[WeakTopic] = []
    recommendations: list[ProblemRecommendation] = []
