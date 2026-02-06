import argparse
import sys
from mcp_memory.db import store

def main():
    parser = argparse.ArgumentParser(description="Manage MCP Memory Projects")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a project")
    delete_parser.add_argument("project_id", help="ID of the project to delete")
    delete_parser.add_argument("--force", "-f", action="store_true", help="Skip confirmation")

    args = parser.parse_args()

    if args.command == "delete":
        if not args.force:
            response = input(f"⚠️  Are you sure you want to DELETE all memories for project '{args.project_id}'? [y/N]: ")
            if response.lower() != 'y':
                print("Operation cancelled.")
                sys.exit(0)
        
        print(f"Deleting project '{args.project_id}'...")
        if store.delete_project(args.project_id):
            print("✅ Project deleted successfully.")
        else:
            print("❌ Error deleting project.")
            sys.exit(1)

if __name__ == "__main__":
    main()
