#!/usr/bin/env python3
"""
Command-line interface for TA-X package.
"""

import asyncio
import argparse
import sys
from typing import Optional
from .config import setup, get_config
from .agent import XAgent

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="TA-X: X (Twitter) Agent Package CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ta-x setup --x-auth-token "your_token" --x-ct0 "your_ct0" --openai-key "your_key" --rapid-api-key "your_rapid_key"
  ta-x post "Hello X world!"
  ta-x like
  ta-x trends
  ta-x user-details elonmusk
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Setup authentication tokens')
    setup_parser.add_argument('--x-auth-token', required=True, help='X Auth Token')
    setup_parser.add_argument('--x-ct0', required=True, help='X CT0 Token')
    setup_parser.add_argument('--openai-key', required=True, help='OpenAI API Key')
    setup_parser.add_argument('--rapid-api-key', required=True, help='RapidAPI Key')
    
    # Post command
    post_parser = subparsers.add_parser('post', help='Create a post')
    post_parser.add_argument('content', help='Post content')
    
    # Like command
    like_parser = subparsers.add_parser('like', help='Like the latest post')
    like_parser.add_argument('--username', help='Username to like post from')
    like_parser.add_argument('--index', type=int, default=0, help='Post index (0=latest, 1=second latest, etc.)')
    
    # Unlike command
    unlike_parser = subparsers.add_parser('unlike', help='Unlike the latest post')
    unlike_parser.add_argument('--username', help='Username to unlike post from')
    unlike_parser.add_argument('--index', type=int, default=0, help='Post index (0=latest, 1=second latest, etc.)')
    
    # Retweet command
    retweet_parser = subparsers.add_parser('retweet', help='Retweet the latest post')
    retweet_parser.add_argument('--username', help='Username to retweet post from')
    retweet_parser.add_argument('--index', type=int, default=0, help='Post index (0=latest, 1=second latest, etc.)')
    
    # Trends command
    trends_parser = subparsers.add_parser('trends', help='Get trending topics')
    
    # User details command
    user_parser = subparsers.add_parser('user-details', help='Get user details')
    user_parser.add_argument('username', help='Username to get details for')
    
    # Tweet details command
    tweet_parser = subparsers.add_parser('tweet-details', help='Get tweet details')
    tweet_parser.add_argument('tweet_id', help='Tweet ID to get details for')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Run the appropriate command
    asyncio.run(run_command(args))

async def run_command(args):
    """Run the appropriate command based on arguments."""
    try:
        if args.command == 'setup':
            setup(
                x_auth_token=args.x_auth_token,
                x_ct0=args.x_ct0,
                openai_api_key=args.openai_key,
                rapid_api_key=args.rapid_api_key
            )
            print("✅ Configuration saved successfully!")
            
        elif args.command == 'config':
            config = get_config()
            print("Current Configuration:")
            print(f"X Auth Token: {'*' * 10 if config.x_auth_token else 'Not set'}")
            print(f"X CT0: {'*' * 10 if config.x_ct0 else 'Not set'}")
            print(f"OpenAI API Key: {'*' * 10 if config.openai_api_key else 'Not set'}")
            print(f"RapidAPI Key: {'*' * 10 if config.rapid_api_key else 'Not set'}")
            
        else:
            # For all other commands, we need an agent
            agent = XAgent()
            
            if args.command == 'post':
                result = await agent.run(f"Post this: {args.content}")
                print(f"📝 {result}")
                
            elif args.command == 'like':
                if args.username:
                    result = await agent.run(f"Like the latest post of {args.username}")
                else:
                    result = await agent.run("Like the latest post")
                print(f"❤️ {result}")
                
            elif args.command == 'unlike':
                if args.username:
                    result = await agent.run(f"Unlike the latest post of {args.username}")
                else:
                    result = await agent.run("Unlike the latest post")
                print(f"💔 {result}")
                
            elif args.command == 'retweet':
                if args.username:
                    result = await agent.run(f"Retweet the latest post of {args.username}")
                else:
                    result = await agent.run("Retweet the latest post")
                print(f"🔄 {result}")
                
            elif args.command == 'trends':
                result = await agent.run("What's trending?")
                print(f"📊 {result}")
                
            elif args.command == 'user-details':
                result = await agent.run(f"Get user details for {args.username}")
                print(f"👤 {result}")
                
            elif args.command == 'tweet-details':
                result = await agent.run(f"Get tweet details for {args.tweet_id}")
                print(f"🐦 {result}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 