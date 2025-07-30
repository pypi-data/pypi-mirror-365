from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
import logfire
import requests
import os
import json
import sys
import asyncio
from dataclasses import asdict, dataclass, field
from pathlib import Path
from pydantic_ai import Agent, RunContext    
from pydantic_ai.tools import Tool 
from .config import get_config
from .schema import (
    StreamResponse, UserDetails,
    CreatePostResponse, LikePostResponse, DislikePostResponse,
    RetweetPostResponse, GetTrendsResponse, GetTweetDetailsResponse, GetUserDetailsResponse,
    Latest_post
)
from .endpoints import createPost, liketweet, unliketweet, retweet, tweetdetails, userdetails, get_trends               

@dataclass
class X_Agent_Deps:
    auth_token: Optional[str] = None
    ct0: Optional[str] = None
    user_details: Optional[UserDetails] = None
    latest_post: Optional[Latest_post] = None
    latest_post_id: Optional[str] = None
    latest_post_liked: bool = False
    latest_post_disliked: bool = False
    latest_post_retweeted: bool = False
    agent_responses: List[StreamResponse] = field(default_factory=list)
    
    def __post_init__(self):
        config = get_config()
        """Set default values from environment variables if not provided"""
        if self.auth_token is None:
            self.auth_token = config.x_auth_token
        if self.ct0 is None:
            self.ct0 = config.x_ct0



def create_post(ctx: RunContext[X_Agent_Deps], text: str) -> Optional[str]:  
            """
            This function is used to create a post on the X platform.
            It returns the post id.
            """
            if text:
                try:
                    response = createPost(ctx.deps.auth_token, ctx.deps.ct0, text)
                    
                    if response.status_code == 200:
                        result = response.json()
                        # Handle multiple response formats from TwitterClient
                        post_id = None
                        try:
                            # Try to extract post_id from various response formats
                            if "data" in result and "create_tweet" in result["data"]:
                                post_id = result["data"]["create_tweet"]["tweet_results"]["result"]["rest_id"]
                            elif "data" in result and "createTweet" in result["data"]:
                                post_id = result["data"]["createTweet"]["tweet_results"]["result"]["rest_id"]
                            elif "data" in result and "id" in result["data"]:
                                post_id = result["data"]["id"]
                            elif "id_str" in result:
                                post_id = result["id_str"]
                            elif "rest_id" in result:
                                post_id = result["rest_id"]
                            elif "id" in result:
                                post_id = result["id"]
                            else:
                                # If we can't extract a specific post_id, return a success indicator
                                logfire.info(f"Post created successfully, but couldn't extract post_id from response: {result}")
                                post_id = "tweet_created_successfully"
                        except Exception as extract_error:
                            logfire.warning(f"Could not extract post_id from response: {extract_error}")
                            post_id = "tweet_created_successfully"
                        
                        logfire.info(f"Post created successfully!:{post_id}")
                        return post_id
                    else:
                        logfire.error(f"Error creating post: {response.text}")
                        return "failed"
                except Exception as e:
                    logfire.error(f"Error connecting to backend: {str(e)}")
                    return str(e)
            else:
                logfire.error("Please enter post content properly")
                return "failed"


def like_post(ctx: RunContext[X_Agent_Deps], post_id: str) -> str:
        """
        This function is used to like a post on the X platform.
        It returns the likes the post.
        """
        if post_id:
            try:
                response = liketweet(ctx.deps.auth_token, ctx.deps.ct0, post_id)
                if response.status_code == 200:
                    result = response.json()
                    logfire.info(f"Post liked successfully!:{result}")
                    return "success"
                else:
                    logfire.error(f"Error liking post: {response.text}")
                    return "failed"
            except Exception as e:
                logfire.error(f"Error liking post: {str(e)}")
                return "failed" #TODO: add a check to see if the post is already liked
        else:
            logfire.error("Please enter post id properly")
            return "failed"


def dislike_post(ctx: RunContext[X_Agent_Deps], post_id: str) -> str:
        """
        This function is used to dislike a post on the X platform.
        It returns the "success" if the post is disliked successfully.
        """
        if post_id:
                try:
                    response = unliketweet(ctx.deps.auth_token, ctx.deps.ct0, post_id)
                    if response.status_code == 200:
                        result = response.json()
                        logfire.info(f"Post disliked successfully!:{result}")
                        return "success"
                    else:
                        logfire.error(f"Error disliking post: {response.text}")
                        return "failed"
                except Exception as e:
                    logfire.error(f"Error disliking post: {str(e)}")
                    return "failed"
        else:
                logfire.error("Please enter post id properly")
                return "failed"


def retweet_post(ctx: RunContext[X_Agent_Deps], post_id: str) -> str:
        """
        This function is used to retweet a post on the X platform.
        It returns the "success" if the post is retweeted successfully.
        It returns the "Retweeted already" if the post is already retweeted.
        """
        if post_id:
                try:
                    response = retweet(ctx.deps.auth_token, ctx.deps.ct0, post_id)
                    if response.status_code == 200:
                        result = response.json()
                        # Check for already retweeted error in response
                        if "error" in result and "already retweeted" in result["error"].lower():
                            return "Retweeted already"
                        else:
                            logfire.info(f"Post retweeted successfully!:{result}")
                            return "success"
                    else:
                        logfire.error(f"Error retweeting post: {response.text}")
                        return "failed"
                except Exception as e:
                    logfire.error(f"Error retweeting post: {str(e)}")
                    return "failed"
        else:
            logfire.error("Please enter post id properly")
            return "failed"

def get_trends(ctx: RunContext[X_Agent_Deps]) -> dict:
                """
                This function is used to get the trends from the X platform.
                It returns the trends.
                """
                try:
                    response = get_trends()
                    if response.status_code == 200:
                        result = response.json()
                        logfire.info(f"Trends fetched successfully!:{result}") 
                        return result
                    else:
                        logfire.error(f"Error fetching trends: {response.text}")
                        return {}
                except Exception as e:
                    logfire.error(f"Error fetching trends: {str(e)}")
                    return {}

    
def get_tweet_details(ctx: RunContext[X_Agent_Deps], tweet_id: str) -> list[str]:
        """
        This function is used to get the tweet details from the X platform.
        It returns the tweet details.
        """
        if tweet_id:
            try:
                response = tweetdetails(ctx.deps.auth_token, ctx.deps.ct0, tweet_id)
                
                if response.status_code not in [200, 201]:
                    logfire.error(f"Error fetching tweet details: {response.text}")
                    return []
                
                data = response.json()
                tweet_data = []
                
                # Try to parse the response structure with better error handling
                try:
                    # Check if the expected structure exists
                    if "user" in data and "result" in data["user"]:
                        user_result = data["user"]["result"]
                        if "timeline" in user_result and "timeline" in user_result["timeline"]:
                            timeline = user_result["timeline"]["timeline"]
                            if "instructions" in timeline and len(timeline["instructions"]) > 1:
                                entries = timeline["instructions"][1].get("entries", [])
                                
                                for entry in entries:
                                    try:
                                        if "content" in entry and "itemContent" in entry["content"]:
                                            item_content = entry["content"]["itemContent"]
                                            if "tweet_results" in item_content and "result" in item_content["tweet_results"]:
                                                tweet_result = item_content["tweet_results"]["result"]
                                                if "rest_id" in tweet_result:
                                                    tweet_id = tweet_result["rest_id"]
                                                    created_at = tweet_result.get("legacy", {}).get("created_at", "")
                                                    tweet_data.append((tweet_id, created_at))
                                    except (KeyError, TypeError) as e:
                                        logfire.warning(f"Error parsing tweet entry: {e}")
                                        continue
                    else:
                        logfire.warning(f"Unexpected response structure: {data}")
                        return []
                        
                except (KeyError, TypeError, IndexError) as e:
                    logfire.error(f"Error parsing tweet details response: {e}")
                    return []
                
                # Sort by creation date and extract tweet IDs
                tweet_data.sort(key=lambda x: x[1], reverse=False)
                tweet_ids = [tweet_id for tweet_id, created_at in tweet_data]

                logfire.info(f"Tweet details fetched successfully! Found {len(tweet_ids)} tweets")
                return tweet_ids
                
            except Exception as e:
                logfire.error(f"Error fetching tweet details: {str(e)}")
                return []
        else:
            logfire.error("Please enter tweet id properly")
            return []

def get_userdetails(ctx: RunContext[X_Agent_Deps], username: str) -> tuple:

        """
        This function is used to get the user details from the X platform.
        It returns the user id, followers and following count.
        """
        if username:
       
            try:
                response = userdetails(username)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    logfire.info(f"User details fetched successfully!:{data}")
                    # Handle new response format with graceful fallback
                    try:
                        id = data["user"]["result"]["rest_id"]
                        followers = str(data["user"]["result"]["legacy"]["followers_count"])
                        following = str(data["user"]["result"]["legacy"]["friends_count"])
                    except KeyError:
                        # Fallback for different response structure
                        id = "user_id_not_found"
                        followers = "0"
                        following = "0"
                        logfire.warning(f"Could not extract user details from response structure: {data}")

                    return id, followers, following
                else:
                    logfire.error(f"Error fetching user details: {response.text}")
                    return "error", "0", "0"
            except Exception as e:
                logfire.error(f"Error fetching user details: {str(e)}")
                return "error", "0", "0"
        else:
            logfire.error("Please enter username properly")
            return "error", "0", "0"



def create_post_tool_func(ctx: RunContext[X_Agent_Deps], content: str) -> CreatePostResponse:
            if content:
                post_id = create_post(ctx, content)
                if post_id == "failed":
                     ctx.deps.agent_responses.append(StreamResponse(tool_name = "create_post_tool", 
                                                               instructions = "Create a post on X", 
                                                               steps = [f"Post creation failed!:{post_id}"], 
                                                               status_code = 500, 
                                                               output = post_id))
                     return CreatePostResponse(post_id=None, status="failed", message="Post creation failed")
                else:
                    ctx.deps.latest_post_id = post_id
                    ctx.deps.agent_responses.append(StreamResponse(tool_name = "create_post_tool", 
                                                                instructions = "Create a post on X", 
                                                                steps = [f"Post created successfully!:{post_id}"], 
                                                                status_code = 200, 
                                                                output = post_id))
                    return CreatePostResponse(post_id=post_id, status="success", message="Post created successfully")
            else:
                return CreatePostResponse(post_id=None, status="failed", message="Please enter content properly")
            


def like_post_tool_func(ctx: RunContext[X_Agent_Deps], post_id: Optional[str] = None, username: Optional[str] = None, index: Optional[int] = None) -> LikePostResponse:
            executable_post_id = None
            
            if username:
                user_id, followers, following = get_userdetails(ctx, username)
                if user_id == "error":
                    return LikePostResponse(status="failed", message="Failed to get user details")
                else:
                    tweet_ids = get_tweet_details(ctx, user_id)
                    if not tweet_ids:
                        return LikePostResponse(status="failed", message=f"No tweets found for user {username}")
                    
                    try:
                        if index is not None:
                            if index < len(tweet_ids):
                                executable_post_id = tweet_ids[index]
                            else:
                                return LikePostResponse(status="failed", message=f"Index {index} out of range. User has {len(tweet_ids)} tweets")
                        else:
                            executable_post_id = tweet_ids[0]
                    except (IndexError, TypeError) as e:
                        return LikePostResponse(status="failed", message=f"Error accessing tweet at index {index}: {str(e)}")
            elif post_id:
                executable_post_id = post_id
            else:
                executable_post_id = ctx.deps.latest_post_id

            if executable_post_id:
                response = like_post(ctx, executable_post_id)
                ctx.deps.agent_responses.append(StreamResponse(tool_name = "like_post_tool", 
                                                               instructions = "Like a post on X", 
                                                               steps = [f"Post liked successfully!:{response}"], 
                                                               status_code = 200, 
                                                               output = response))
               
                return LikePostResponse(status="success", message="Post liked successfully")
            else:
                return LikePostResponse(status="failed", message="No post ID provided. Please provide a valid post ID to like the post.")
            

def dislike_post_tool_func(ctx: RunContext[X_Agent_Deps], post_id: Optional[str] = None, username: Optional[str] = None, index: Optional[int] = None) -> DislikePostResponse:
            executable_post_id = None
            
            if username:
                user_id, followers, following = get_userdetails(ctx, username)
                if user_id == "error":
                    return DislikePostResponse(status="failed", message="Failed to get user details")
                else:
                    tweet_ids = get_tweet_details(ctx, user_id)
                    if not tweet_ids:
                        return DislikePostResponse(status="failed", message=f"No tweets found for user {username}")
                    
                    try:
                        if index is not None:
                            if index < len(tweet_ids):
                                executable_post_id = tweet_ids[index]
                            else:
                                return DislikePostResponse(status="failed", message=f"Index {index} out of range. User has {len(tweet_ids)} tweets")
                        else:
                            executable_post_id = tweet_ids[0]
                    except (IndexError, TypeError) as e:
                        return DislikePostResponse(status="failed", message=f"Error accessing tweet at index {index}: {str(e)}")
            elif post_id:
                executable_post_id = post_id
            else:
                executable_post_id = ctx.deps.latest_post_id 

            if executable_post_id:
                response = dislike_post(ctx, executable_post_id)
                ctx.deps.agent_responses.append(StreamResponse(tool_name = "dislike_post_tool", 
                                                               instructions = "Dislike a post on X", 
                                                               steps = [f"Post disliked successfully!:{response}"], 
                                                               status_code = 200, 
                                                               output = response))
                if response == "success":
                    ctx.deps.latest_post_disliked = True
                    return DislikePostResponse(status="success", message="Post disliked successfully")
                else:
                    ctx.deps.latest_post_disliked = False
                    return DislikePostResponse(status="failed", message="Failed to dislike post")
            else:
                return DislikePostResponse(status="failed", message="No post ID provided. Please provide a valid post ID to dislike the post.")
        

def retweet_post_tool_func(ctx: RunContext[X_Agent_Deps], post_id: Optional[str] = None, username: Optional[str] = None, index: Optional[int] = None) -> RetweetPostResponse:
            executable_post_id = None
            
            if username:
                user_id, followers, following = get_userdetails(ctx, username)
                if user_id == "error":
                    return RetweetPostResponse(status="failed", message="Failed to get user details")
                else:
                    tweet_ids = get_tweet_details(ctx, user_id)
                    if not tweet_ids:
                        return RetweetPostResponse(status="failed", message=f"No tweets found for user {username}")
                    
                    try:
                        if index is not None:
                            if index < len(tweet_ids):
                                executable_post_id = tweet_ids[index]
                            else:
                                return RetweetPostResponse(status="failed", message=f"Index {index} out of range. User has {len(tweet_ids)} tweets")
                        else:
                            executable_post_id = tweet_ids[0]
                    except (IndexError, TypeError) as e:
                        return RetweetPostResponse(status="failed", message=f"Error accessing tweet at index {index}: {str(e)}")
            elif post_id:
                executable_post_id = post_id
            else:
                executable_post_id = ctx.deps.latest_post_id

            if executable_post_id:
                response = retweet_post(ctx, executable_post_id)
                ctx.deps.agent_responses.append(StreamResponse(tool_name = "retweet_post_tool", 
                                                               instructions = "Retweet a post on X", 
                                                               steps = [f"Post retweeted successfully!:{response}"], 
                                                               status_code = 200, 
                                                               output = response))
                if response == "success":
                    ctx.deps.latest_post_retweeted = True
                    return RetweetPostResponse(status="success", message="Post retweeted successfully")
                else:
                    ctx.deps.latest_post_retweeted = False
                    return RetweetPostResponse(status="failed", message="Failed to retweet post")
            else:
                return RetweetPostResponse(status="failed", message="No post ID provided. Please provide a valid post ID to retweet the post.")
        
def get_trends_tool_func(ctx: RunContext[X_Agent_Deps]) -> GetTrendsResponse:
            trends_data = get_trends(ctx)
            # Extract the trends list from the response
            trends_list = trends_data.get("trends", []) if isinstance(trends_data, dict) else []
            ctx.deps.agent_responses.append(StreamResponse(tool_name = "get_trends_tool", 
                                                           instructions = "Get the trends on X", 
                                                           steps = [f"Trends fetched successfully!:{trends_list}"], 
                                                           status_code = 200, 
                                                           output = trends_list))
            return GetTrendsResponse(trends=trends_list, status="success", message="Trends fetched successfully")     
    

def get_tweetdetails_tool_func(ctx: RunContext[X_Agent_Deps], tweet_id: str) -> GetTweetDetailsResponse:
            tweet_details = get_tweet_details(ctx, tweet_id)
            ctx.deps.agent_responses.append(StreamResponse(tool_name = "get_tweetdetails_tool", 
                                                           instructions = "Get the details of a tweet on X", 
                                                           steps = [f"Tweet details fetched successfully!:{tweet_details}"], 
                                                           status_code = 200, 
                                                           output = tweet_details))
            return GetTweetDetailsResponse(tweet_details=tweet_details, status="success", message="Tweet details fetched successfully")
        
def get_userdetails_tool_func(ctx: RunContext[X_Agent_Deps], username: str) -> GetUserDetailsResponse:
            result = get_userdetails(ctx, username)
            if result:
                user_id, followers, following = result
                ctx.deps.agent_responses.append(StreamResponse(tool_name = "get_userdetails_tool", 
                                                               instructions = "Get the details of a user on X", 
                                                               steps = [f"User details fetched successfully!:{user_id, followers, following}"], 
                                                               status_code = 200, 
                                                               output = f"User id: {user_id}, Followers: {followers}, Following: {following}"))
                if ctx.deps.user_details and ctx.deps.user_details.username == username:
                     ctx.deps.user_details.user_id = user_id
                     ctx.deps.user_details.followers = followers
                     ctx.deps.user_details.following = following
                return GetUserDetailsResponse(user_id=user_id, followers=followers, following=following, status="success", message="User details fetched successfully")
            else:
                return GetUserDetailsResponse(user_id=None, followers=None, following=None, status="failed", message="Failed to get user details")
        

def get_persona_func(ctx: RunContext[X_Agent_Deps])->str:
            """Get the persona of the user on X"""
            if ctx.deps.user_details is None:
                return "No user details available. Please fetch user details first."
            persona = ctx.deps.user_details.persona
            return persona if persona else "No persona information available."

    
        
create_post_tool = Tool(
    name="create_post_tool",
    description="Create a post on X",
    function=create_post_tool_func
)

like_post_tool = Tool(
    name="like_post_tool",
    description="Like a post on X. You can provide either a post_id directly, or a username to like their latest post, or a username with index to like a specific post by that user.",
    function=like_post_tool_func
)

dislike_post_tool = Tool(
    name="dislike_post_tool",
    description="Unlike/dislike a post on X. You can provide either a post_id directly, or a username to unlike their latest post, or a username with index to unlike a specific post by that user.",
    function=dislike_post_tool_func
)

retweet_post_tool = Tool(
    name="retweet_post_tool",
    description="Retweet a post on X. You can provide either a post_id directly, or a username to retweet their latest post, or a username with index to retweet a specific post by that user.",
    function=retweet_post_tool_func
)

get_trends_tool = Tool(
    name="get_trends_tool",
    description="Get the trends on X",
    function=get_trends_tool_func
)

get_tweetdetails_tool = Tool(
    name="get_tweetdetails_tool",
    description="Get the details of a tweet on X",
    function=get_tweetdetails_tool_func
)

get_userdetails_tool = Tool(
    name="get_userdetails_tool",
    description="Get the details of a user on X",
    function=get_userdetails_tool_func
)

get_persona = Tool(
    name="get_persona",
    description="Get the persona of the user on X",
    function=get_persona_func
)
