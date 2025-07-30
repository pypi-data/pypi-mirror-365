from dataclasses import dataclass
from typing import List, Optional
from pydantic import BaseModel, Field

@dataclass
class StreamResponse:
    tool_name: str
    instructions: str
    steps: List[str]
    status_code: int
    output: str

@dataclass
class UserDetails:
    username: str
    user_id: str
    followers: int
    following: int
    persona:str = None

@dataclass
class Latest_post:
    latest_post_id: str = None
    latest_post_liked: bool = False
    latest_post_disliked: bool = False
    latest_post_retweeted: bool = False


class CreatePostResponse(BaseModel):
    post_id: Optional[str] = Field(None, description="ID of the created post")
    status: str = Field(..., description="Status of the operation (success/failed)")
    message: Optional[str] = Field(None, description="Optional message about the operation")


class LikePostResponse(BaseModel):
    status: str = Field(..., description="Status of the operation (success/failed)")
    message: Optional[str] = Field(None, description="Optional message about the operation")


class DislikePostResponse(BaseModel):
    status: str = Field(..., description="Status of the operation (success/failed)")
    message: Optional[str] = Field(None, description="Optional message about the operation")


class RetweetPostResponse(BaseModel):
    status: str = Field(..., description="Status of the operation (success/failed)")
    message: Optional[str] = Field(None, description="Optional message about the operation")


class GetTrendsResponse(BaseModel):
    trends: list = Field(None, description="List of trends fetched from X platform")
    status: str = Field(..., description="Status of the operation (success/failed)")
    message: str = Field(None, description="Optional message about the operation")


class GetTweetDetailsResponse(BaseModel):
    tweet_details: dict = Field(None, description="Details of the tweet fetched from X platform")
    status: str = Field(..., description="Status of the operation (success/failed)")
    message: Optional[str] = Field(None, description="Optional message about the operation")


class GetUserDetailsResponse(BaseModel):
    user_id: str = Field(None, description="User ID of the X user")
    followers: int = Field(None, description="Number of followers")
    following: int = Field(None, description="Number of following")
    status: str = Field(..., description="Status of the operation (success/failed)")
    message: Optional[str] = Field(None, description="Optional message about the operation")

