#!/usr/bin/env python3
"""
PortableSource Main Application
"""

import argparse
import sys

from .config import logger
from .utils import (
    PortableSourceApp,
    change_installation_path,
    save_install_path_to_registry,
    install_msvc_build_tools,
    check_msvc_build_tools_installed
)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="PortableSource - Portable AI/ML Environment")
    parser.add_argument("--install-path", type=str, help="Installation path")
    parser.add_argument("--setup-env", action="store_true", help="Setup environment (Portable)")
    parser.add_argument("--setup-reg", action="store_true", help="Register installation path in registry")
    parser.add_argument("--change-path", action="store_true", help="Change installation path")
    parser.add_argument("--install-repo", type=str, help="Install repository")
    parser.add_argument("--update-repo", type=str, help="Update repository")
    parser.add_argument("--list-repos", action="store_true", help="Show installed repositories")
    parser.add_argument("--system-info", action="store_true", help="Show system information")
    parser.add_argument("--check-env", action="store_true", help="Check environment status and tools")
    parser.add_argument("--install-msvc", action="store_true", help="Install MSVC Build Tools")
    parser.add_argument("--check-msvc", action="store_true", help="Check MSVC Build Tools installation")
    
    args = parser.parse_args()
    
    # Create application
    app = PortableSourceApp()
    
    # For path change command, full initialization is not needed
    if args.change_path:
        change_installation_path()
        return
    
    # Initialize for other commands
    app.initialize(args.install_path)
    
    # Execute commands
    if args.setup_env:
        app.setup_environment()
    
    if args.setup_reg:
        if app.install_path:
            save_install_path_to_registry(app.install_path)
        else:
            logger.error("Installation path not defined")
    
    if args.install_repo:
        success = app.install_repository(args.install_repo)
        if success:
            logger.info(f"[OK] Repository '{args.install_repo}' installed successfully")
        else:
            logger.error(f"[ERROR] Failed to install repository '{args.install_repo}'")
            sys.exit(1)
    
    if args.update_repo:
        app.update_repository(args.update_repo)
    
    if args.list_repos:
        repos = app.list_installed_repositories()
        logger.info(f"Installed repositories: {len(repos)}")
        for repo in repos:
            launcher_status = "[OK]" if repo['has_launcher'] else "[ERROR]"
            logger.info(f"  * {repo['name']} {launcher_status}")
    
    if args.system_info:
        app.show_system_info_with_repos()
    
    if args.check_env:
        if app.install_path is None:
            logger.error("Installation path not initialized")
            return
        if not app.environment_manager:
            logger.error("Environment manager not initialized")
            return
        
        logger.info("Checking environment status...")
        status = app.environment_manager.check_environment_status()
        
        print("\n" + "="*60)
        print("ENVIRONMENT STATUS")
        print("="*60)
        print(f"Environment exists: {'[OK]' if status['environment_exists'] else '[ERROR]'}")
        print(f"Setup completed: {'YES' if status['environment_setup_completed'] else 'NO'}")
        print(f"Overall status: {status['overall_status']}")
        
        if status['environment_exists']:
            print("\nTools status:")
            for tool_name, tool_status in status['tools_status'].items():
                if tool_status['working']:
                    print(f"  [OK] {tool_name}: {tool_status['version']}")
                else:
                    print(f"  [ERROR] {tool_name}: {tool_status['error']}")
                    if 'stderr' in tool_status and tool_status['stderr']:
                        print(f"     Error details: {tool_status['stderr']}")
        
        print("="*60)
    
    if args.install_msvc:
        if app.install_path is None:
            logger.error("Installation path not initialized")
            return
        install_msvc_build_tools(app.install_path)
    
    if args.check_msvc:
        is_installed = check_msvc_build_tools_installed()
        status = "Installed" if is_installed else "Not installed"
        logger.info(f"MSVC Build Tools: {status}")
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        app.show_system_info_with_repos()
        print("\n" + "="*50)
        print("Available commands:")
        print("  --setup-env             Setup environment")
        print("  --setup-reg             Register path in registry")
        print("  --change-path           Change installation path")
        print("  --install-repo <url>    Install repository")
        print("  --update-repo <name>    Update repository")
        print("  --list-repos            Show repositories")
        print("  --system-info           System information")
        print("  --check-env             Check environment status")
        print("  --install-path <path>   Installation path")
        print("  --install-msvc          Install MSVC Build Tools")
        print("  --check-msvc            Check MSVC Build Tools")
        print("="*50)

if __name__ == "__main__":
    main()