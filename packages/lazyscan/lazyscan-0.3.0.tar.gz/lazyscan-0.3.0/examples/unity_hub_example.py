#!/usr/bin/env python3
"""Example usage of the Unity Hub parser module."""

from helpers.unity_hub import read_unity_hub_projects


def main():
    """Demonstrate reading Unity Hub projects."""
    print("Unity Hub Project Reader Example")
    print("=" * 40)
    
    # Read from default Unity Hub location
    print("\nReading from default Unity Hub location...")
    projects = read_unity_hub_projects()
    
    if projects:
        print(f"\nFound {len(projects)} Unity project(s):")
        for i, project in enumerate(projects, 1):
            print(f"\n{i}. {project['name']}")
            print(f"   Path: {project['path']}")
    else:
        print("\nNo Unity projects found in default location.")
        print("This could mean:")
        print("- Unity Hub is not installed")
        print("- No projects have been added to Unity Hub")
        print("- The projects file is in a different location")
    
    # Example of reading from a custom path
    print("\n" + "=" * 40)
    print("To read from a custom location, use:")
    print('projects = read_unity_hub_projects("/path/to/projects-v1.json")')


if __name__ == "__main__":
    main()
