#!/usr/bin/env python3
import argparse
from hyyshare import run_server, cleanup
from hyyshare.user_manager import UserManager
from hyyshare.config import hyyshareConfig

def main():
    parser = argparse.ArgumentParser(description="hyyshare - Local File Sharing Server")
    parser.add_argument("--name", "-n", default="hyyshare", help="Share name")
    parser.add_argument("--hostname", "-H", default="hyyshare.localhost", 
                        help="Hostname for the server (e.g., custom.localhost)")
    parser.add_argument("--path", "-p", default="~", help="Share directory path")
    parser.add_argument("--port", "-P", type=int, default=8545, help="Server port")
    parser.add_argument("--chinese", "-C", action="store_true", help="Use Chinese output")
    parser.add_argument("--english", "-E", action="store_true", help="Use English output")
    parser.add_argument("--auth", "-a", action="store_true", help="Enable authentication")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup system settings")
    
    # 用户管理命令
    user_subparsers = parser.add_subparsers(dest='user_command', help='User management commands')
    
    # 添加用户
    add_user_parser = user_subparsers.add_parser('add-user', help='Add a new user')
    add_user_parser.add_argument('username', help='Username')
    add_user_parser.add_argument('password', help='Password')
    
    # 移除用户
    remove_user_parser = user_subparsers.add_parser('remove-user', help='Remove a user')
    remove_user_parser.add_argument('username', help='Username')
    
    # 列出用户
    user_subparsers.add_parser('list-users', help='List all users')
    
    args = parser.parse_args()
    
    language = "chinese" if args.chinese else "english"
    
    if args.cleanup:
        cleanup()
        return
    
    if args.user_command:
        try:
            config = hyyshareConfig.load_from_file()
        except FileNotFoundError:
            print("No configuration file found. Please start the server first.")
            return
        
        user_manager = UserManager(config)
        
        if args.user_command == 'add-user':
            if user_manager.add_user(args.username, args.password):
                print(f"User '{args.username}' added successfully")
            else:
                print(f"Failed to add user '{args.username}'")
        
        elif args.user_command == 'remove-user':
            if user_manager.remove_user(args.username):
                print(f"User '{args.username}' removed successfully")
            else:
                print(f"Failed to remove user '{args.username}'")
        
        elif args.user_command == 'list-users':
            users = user_manager.list_users()
            if users:
                print("Registered users:")
                for user in users:
                    print(f" - {user}")
            else:
                print("No users registered")
        return
    
    run_server(
        share_name=args.name,
        hostname=args.hostname,  # 传递hostname参数
        share_path=args.path,
        port=args.port,
        language=language,
        enable_auth=args.auth
    )

if __name__ == "__main__":
    main()