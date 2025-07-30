import os
import uuid
import shutil

UID = None

def connect(id):
    global UID
    UID = id
    user_path = os.path.join("DB_USER", "projects", UID)

    if not os.path.exists(user_path):
        print(f"Error: Project ID '{UID}' does not exist. Please create it first.")
        UID = None
        return
    
    try:
        with open(user_path + "/build.cfg") as build:
            project_name = build.readline()
            cret_path = os.path.join(user_path, "cret")
            os.makedirs(cret_path, exist_ok=True)
            print(f"Connected to Paperbase project...\n{project_name}")
    except Exception as e:
        print(f"Your project is corrupted.." + e)
    

def createNewProject(name):
    # Generate a unique ID
    unique_id = str(uuid.uuid4())
    print(f"Your project ID: {unique_id}")
    # Define the path for the new project folder
    base_path = os.path.expanduser("DB_USER")  # Get the user's home directory
    project_path = os.path.join(base_path, "projects", unique_id)
    # Create the folder
    os.makedirs(project_path, exist_ok=True)
    # Create a 'build.cfg' file and write the project name inside it
    config_file_path = os.path.join(project_path, "build.cfg")
    with open(config_file_path, "w") as config_file:
        config_file.write(f"NAME: {name}\n")
        
    return project_path

def deleteProject(id):
    base_path = os.path.expanduser("DB_USER")
    project_path = os.path.join(base_path, "projects\\" + id)
    # Check if the path exists
    if os.path.exists(project_path):
    # Remove the folder and its contents
        try:
            os.rmdir(project_path)
            return True
        except OSError:
                # If the folder is not empty, remove contents recursively
            shutil.rmtree(project_path)
            return True
    else:
        return False

def listProjects():
            # Define the base path for projects
    base_path = os.path.expanduser("DB_USER")
    projects_path = os.path.join(base_path, "projects")
            
    project_names = []
    for project_id in os.listdir(projects_path):
        project_path = os.path.join(projects_path, project_id)
        if os.path.isdir(project_path):
            config_file_path = os.path.join(project_path, "build.cfg")
            if os.path.exists(config_file_path):
                with open(config_file_path, "r") as config_file:
                    for line in config_file:
                        if line.startswith("NAME:"):
                            project_names.append(line.split("NAME:")[1].strip())
    return project_names