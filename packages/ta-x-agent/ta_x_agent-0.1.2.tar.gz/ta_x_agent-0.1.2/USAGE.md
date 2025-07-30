# ta-x-agent Usage Guide

## Quick Start

### Installation

```bash
pip install ta-x-agent
```

### Basic Usage

```python
import asyncio
from ta_x import setup, XAgent

async def main():
    # Setup authentication
    setup(
        x_auth_token="your_x_auth_token_here",
        x_ct0="your_x_ct0_token_here", 
        openai_api_key="your_openai_api_key_here",
        rapid_api_key="your_rapid_api_key_here"
    )
    
    # Create agent instance
    agent = XAgent()
    
    # Use the agent
    result = await agent.run("Post this: Hello X world!")
    print(result)

asyncio.run(main())
```

## Import Syntax

The package supports the exact import syntax you wanted:

```python
from ta_x import XAgent
agent = XAgent()
agent.run(user_prompt=" ")
```

## Available Operations

### 1. Create Posts
```python
await agent.run("Post this: Hello X world!")
await agent.run("Create a post about AI and social media")
```

### 2. Like Posts
```python
await agent.run("Like the latest post")
await agent.run("Like the latest post of elonmusk")
await agent.run("Like the second latest post of elonmusk")
```

### 3. Unlike Posts
```python
await agent.run("Unlike the latest post")
await agent.run("Unlike the latest post of elonmusk")
```

### 4. Retweet Posts
```python
await agent.run("Retweet the latest post")
await agent.run("Retweet the latest post of elonmusk")
```

### 5. Get Trends
```python
await agent.run("What's trending on X?")
await agent.run("Show trends")
```

### 6. Get User Details
```python
await agent.run("Get user details for elonmusk")
await agent.run("Show user info for elonmusk")
```

### 7. Get Tweet Details
```python
await agent.run("Get tweet details for 123456789")
```

## Authentication Setup

### Method 1: Using setup() function
```python
from ta_x import setup

setup(
    x_auth_token="your_x_auth_token",
    x_ct0="your_x_ct0_token",
    openai_api_key="your_openai_api_key",
    rapid_api_key="your_rapid_api_key"
)
```

### Method 2: Environment Variables
```bash
export X_AUTH_TOKEN="your_x_auth_token"
export X_CT0="your_x_ct0_token"
export OPENAI_API_KEY="your_openai_api_key"
export RAPID_API_KEY="your_rapid_api_key"
```

### Method 3: .env file
Create a `.env` file in your project root:
```
X_AUTH_TOKEN=your_x_auth_token
X_CT0=your_x_ct0_token
OPENAI_API_KEY=your_openai_api_key
RAPID_API_KEY=your_rapid_api_key
```

## CLI Usage

The package also provides a command-line interface:

```bash
# Setup authentication
ta-x-agent setup --x-auth-token "your_token" --x-ct0 "your_ct0" --openai-key "your_key" --rapid-api-key "your_rapid_key"

# Create a post
ta-x-agent post "Hello X world!"

# Like the latest post
ta-x-agent like

# Get trending topics
ta-x-agent trends

# Get user details
ta-x-agent user-details elonmusk
```

## Advanced Usage

### Using XAgent Class Directly
```python
from ta_x import XAgent

custom_agent = XAgent(
    auth_token="your_x_auth_token",
    ct0="your_x_ct0_token"
)

result = await custom_agent.run("Post this: Hello world!")
```

### Using execute_x_task Function
```python
from ta_x import execute_x_task

result = await execute_x_task("Post this: Hello world!")
```

## Error Handling

```python
try:
    result = await agent.run("Post this: Test post")
    print(f"Success: {result}")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure authentication tokens are set correctly!")
```

## Examples

See the following files for complete examples:
- `simple_example.py` - Basic usage with your desired syntax
- `example_usage.py` - Comprehensive examples of all features

## Requirements

- Python 3.8+
- X (Twitter) authentication tokens
- OpenAI API key
- RapidAPI key

## Dependencies

- pydantic>=2.0.0
- pydantic-ai>=0.1.0
- requests>=2.25.0
- python-dotenv>=1.0.0
- openai>=1.0.0
- httpx>=0.25.0 