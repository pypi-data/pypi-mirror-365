import requests
from .config import get_config

class APIException(Exception):
    """Custom exception for API errors"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"API Error {status_code}: {detail}")


def createPost(auth_token: str, ct0: str, text: str):
   
    base_url = f"https://twitter-aio.p.rapidapi.com/actions/createTweet"
    config = get_config()
    rapid_api_key = config.rapid_api_key 
    querystring = {"authToken":auth_token,"ct0":ct0}

    payload = { "tweet": f"{text}" }
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "twitter-aio.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.post(base_url, json=payload, headers=headers, params=querystring)

    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    print(data)
    return data



def liketweet(auth_token: str, ct0: str, tweetId: str):
   
    base_url=f"https://twitter-aio.p.rapidapi.com/actions/like/{tweetId}"

    querystring = {"authToken":auth_token,"ct0":ct0}

    config = get_config()
    rapid_api_key = config.rapid_api_key 
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
    }
    response = requests.get(base_url, headers=headers, params=querystring)

    print(response.json())

    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
   
    data = response.json()
    print(data)
    return data


def unliketweet(auth_token: str, ct0: str, tweetId: str):
   
    base_url=f"https://twitter-aio.p.rapidapi.com/actions/unlike/{tweetId}"

    querystring = {"authToken":auth_token,"ct0":ct0}

    config = get_config()
    rapid_api_key = config.rapid_api_key 
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
    }
    response = requests.get(base_url, headers=headers, params=querystring)

    print(response.json())

    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
   
    data = response.json()
    print(data)
    return data



def retweet(auth_token: str, ct0: str, tweetId: str):
    
     base_url=f"https://twitter-aio.p.rapidapi.com/actions/retweet/{tweetId}"

     querystring = {"authToken":auth_token,"ct0":ct0}

     config = get_config()
     rapid_api_key = config.rapid_api_key 
     headers = {
         "x-rapidapi-key": rapid_api_key,
         "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
     }
     response = requests.get(base_url, headers=headers, params=querystring)

     print(response.json())

     if response.status_code != 200:
         try:
             error_detail = response.json()
             raise APIException(status_code=response.status_code, detail=error_detail)
         except ValueError:
             raise APIException(status_code=response.status_code, detail=response.text)
    
     data = response.json()
     print(data)
     return data





def get_trends():
    
     base_url=f"https://twitter-aio.p.rapidapi.com/trends/1"
     
     config = get_config()
     rapid_api_key = config.rapid_api_key 
     headers = {
         "x-rapidapi-key": rapid_api_key,
         "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
     }
     response = requests.get(base_url, headers=headers)

     print(response.json())

     if response.status_code != 200:
         try:
             error_detail = response.json()
             raise APIException(status_code=response.status_code, detail=error_detail)
         except ValueError:
             raise APIException(status_code=response.status_code, detail=response.text)
    
     data = response.json()
     print(data)
     return data




def tweetdetails(auth_token: str, ct0: str, tweetId: str):
    
     base_url=f"https://twitter-aio.p.rapidapi.com/tweet/{tweetId}"

     querystring = {"count":"20","includeTimestamp":"false"}

     config = get_config()
     rapid_api_key = config.rapid_api_key 
     headers = {
         "x-rapidapi-key": rapid_api_key,
         "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
     }
     response = requests.get(base_url, headers=headers, params=querystring)

     print(response.json())

     if response.status_code != 200:
         try:
             error_detail = response.json()
             raise APIException(status_code=response.status_code, detail=error_detail)
         except ValueError:
             raise APIException(status_code=response.status_code, detail=response.text)
    
     data = response.json()
     print(data)
     return data


def userdetails(username:str):


    base_url = f"https://twitter-aio.p.rapidapi.com/user/by/username/{username}"
    config = get_config()
    rapid_api_key = config.rapid_api_key 
    headers = {
        "x-rapidapi-key": rapid_api_key,
        "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
    }

    response = requests.get(base_url, headers=headers)

    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    print(data)
    return data


def tweets_byuserId(userId: str):
    
     base_url=f"https://twitter-aio.p.rapidapi.com/user/{userId}/tweets"

     querystring = {"count":"20"}

     config = get_config()
     rapid_api_key = config.rapid_api_key 
     headers = {
         "x-rapidapi-key": rapid_api_key,
         "x-rapidapi-host": "twitter-aio.p.rapidapi.com"
     }
     response = requests.get(base_url, headers=headers, params=querystring)

     print(response.json())

     if response.status_code != 200:
         try:
             error_detail = response.json()
             raise APIException(status_code=response.status_code, detail=error_detail)
         except ValueError:
             raise APIException(status_code=response.status_code, detail=response.text)
    
     data = response.json()
     print(data)
     return data




def tweetsAndReplies(user_id: str):


    base_url = f"https://twitter-aio.p.rapidapi.com/user/{user_id}/tweetsAndReplies"

    config = get_config()
    rapid_api_key = config.rapid_api_key 
    headers = {
	"x-rapidapi-key": rapid_api_key,
	"x-rapidapi-host": "twitter-aio.p.rapidapi.com"
    }
    querystring = {"count":"20"}
    response = requests.get(base_url, headers=headers, params=querystring)


    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    print(data)
    return data



def get_likesbyuserid(user_id: str):


    base_url = f"https://twitter-aio.p.rapidapi.com/user/{user_id}/likes"

    config = get_config()
    rapid_api_key = config.rapid_api_key 
    headers = {
	"x-rapidapi-key": rapid_api_key,
	"x-rapidapi-host": "twitter-aio.p.rapidapi.com"
    }
    querystring = {"count":"20"}
    response = requests.get(base_url, headers=headers, params=querystring)


    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    print(data)
    return data




def get_followers(user_id: str):


    base_url = f"https://twitter-aio.p.rapidapi.com/user/{user_id}/followers"

    config = get_config()
    rapid_api_key = config.rapid_api_key 
    headers = {
	"x-rapidapi-key": rapid_api_key,
	"x-rapidapi-host": "twitter-aio.p.rapidapi.com"
    }
    querystring = {"count":"20"}
    response = requests.get(base_url, headers=headers, params=querystring)


    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    print(data)
    return data



def get_followings(user_id: str):


    base_url = f"https://twitter-aio.p.rapidapi.com/user/{user_id}/followings"

    config = get_config()
    rapid_api_key = config.rapid_api_key 
    headers = {
	"x-rapidapi-key": rapid_api_key,
	"x-rapidapi-host": "twitter-aio.p.rapidapi.com"
    }
    querystring = {"count":"20"}
    response = requests.get(base_url, headers=headers, params=querystring)


    if response.status_code != 200:
        try:
            error_detail = response.json()
            raise APIException(status_code=response.status_code, detail=error_detail)
        except ValueError:
            raise APIException(status_code=response.status_code, detail=response.text)
    
    data = response.json()
    print(data)
    return data