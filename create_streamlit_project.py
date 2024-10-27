import os
import sys

def create_project_structure(project_name):
    # Define the directory structure
    structure = {
        '.streamlit': [],
        'assets': ['images', 'styles', 'scripts'],
        'data': ['raw', 'processed', 'external'],
        'notebooks': [],
        'src': ['components', 'pages', 'utils'],
    }

    # Create the project directory
    os.makedirs(project_name, exist_ok=True)

    # Create the subdirectories
    for dir_name, subdirs in structure.items():
        dir_path = os.path.join(project_name, dir_name)
        os.makedirs(dir_path, exist_ok=True)
        for subdir in subdirs:
            os.makedirs(os.path.join(dir_path, subdir), exist_ok=True)

    # Create main.py and config.py in src
    with open(os.path.join(project_name, 'src', 'main.py'), 'w') as f:
        f.write("# Main entry point for Streamlit app\n")

    with open(os.path.join(project_name, 'src', 'config.py'), 'w') as f:
        f.write("# Configuration settings\n")

    # Create requirements.txt and README.md
    with open(os.path.join(project_name, 'requirements.txt'), 'w') as f:
        f.write("# Python dependencies\n")

    with open(os.path.join(project_name, 'README.md'), 'w') as f:
        f.write("# Project Title\n\n## Description\n")

    # Create .gitignore file
    with open(os.path.join(project_name, '.gitignore'), 'w') as f:
        f.write(".DS_Store\n")
        f.write("__pycache__/\n")
        f.write("*.pyc\n")

    print(f"Project structure for '{project_name}' created successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_streamlit_project.py project_name")
        sys.exit(1)
    create_project_structure(sys.argv[1])
