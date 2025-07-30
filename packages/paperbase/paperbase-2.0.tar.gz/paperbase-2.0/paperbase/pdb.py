import os
import shutil
from paperbase import config

def _get_base_path(paperbase, subpath=None):
    """Helper to construct full path with optional subpath."""
    if not config.UID:
        raise Exception("Project ID not connected. Use config.connect(project_id) first.")
    
    base = os.path.join("DB_USER", "projects", config.UID, "data", paperbase)
    if not os.path.exists(base):
        raise FileNotFoundError(f"Paperbase '{paperbase}' does not exist.")
    
    if subpath:
        sub = os.path.join(base, subpath)
        if not os.path.exists(sub):
            raise FileNotFoundError(f"Subpath '{subpath}' does not exist in paperbase '{paperbase}'.")
        return sub
    return base

def _safe_key(key):
    return key.replace('/', '_').replace('\\', '_')

def newPaperBase(name):
    base_path = os.path.join("DB_USER", "projects", config.UID, "data", name)
    if os.path.exists(base_path):
        print(f"Error: The paperbase '{name}' already exists.")
        return
    try:
        os.makedirs(base_path)
    except Exception as e:
        print(f"Error creating paperbase: {e}")

def newPaperSubBase(paperbase, name):
    try:
        base_path = _get_base_path(paperbase)
        sub_path = os.path.join(base_path, name)
        os.makedirs(sub_path, exist_ok=True)
    except Exception as e:
        print(f"Error: {e}")

def insertData(paperbase, key, value, subpath=None):
    try:
        base_path = _get_base_path(paperbase, subpath)
        file_path = os.path.join(base_path, _safe_key(key))
        with open(file_path, 'w') as file:
            file.write(value)
    except Exception as e:
        print(f"Error inserting data: {e}")

def retrieveData(paperbase, key, subpath=None):
    try:
        base_path = _get_base_path(paperbase, subpath)
        file_path = os.path.join(base_path, _safe_key(key))
        if not os.path.exists(file_path):
            print(f"Error: Data key '{key}' does not exist.")
            return
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"Error retrieving data: {e}")

def editData(paperbase, key, new_value, subpath=None):
    try:
        base_path = _get_base_path(paperbase, subpath)
        file_path = os.path.join(base_path, _safe_key(key))
        if not os.path.exists(file_path):
            print(f"Error: Data key '{key}' does not exist.")
            return
        with open(file_path, 'w') as file:
            file.write(new_value)
    except Exception as e:
        print(f"Error editing data: {e}")

def deletePaperBase(name):
    try:
        base_path = os.path.join("DB_USER", "projects", config.UID, "data", name)
        if not os.path.exists(base_path):
            print(f"Error: The paperbase '{name}' does not exist.")
            return
        shutil.rmtree(base_path)
    except Exception as e:
        print(f"Error deleting paperbase: {e}")

def deleteData(paperbase, key, subpath=None):
    try:
        base_path = _get_base_path(paperbase, subpath)
        file_path = os.path.join(base_path, _safe_key(key))
        if not os.path.exists(file_path):
            print(f"Error: Data key '{key}' does not exist.")
            return
        os.remove(file_path)
    except Exception as e:
        print(f"Error deleting data: {e}")
def deletePaperSubBase(paperbase, subbase):
    if not config.UID:
        print("Project ID not connected. Use config.connect(project_id) first.")
        return

    subbase_path = os.path.join("DB_USER", "projects", config.UID, "data", paperbase, subbase)

    if not os.path.exists(subbase_path):
        print(f"Error: Subbase '{subbase}' does not exist in paperbase '{paperbase}'.")
        return

    try:
        shutil.rmtree(subbase_path)
    except Exception as e:
        print(f"Error deleting subbase: {e}")

def retrieveSubBases(paperbase):
    if not config.UID:
        print("Project ID not connected. Use config.connect(project_id) first.")
        return []

    base_path = os.path.join("DB_USER", "projects", config.UID, "data", paperbase)

    if not os.path.exists(base_path):
        print(f"Error: Paperbase '{paperbase}' does not exist.")
        return []

    try:
        subbases = [name for name in os.listdir(base_path)
                    if os.path.isdir(os.path.join(base_path, name))]
        return subbases
    except Exception as e:
        print(f"Error retrieving subbases: {e}")
        return []
    
def retrieveSubBaseDatas(paperbase, subbase):
    if not config.UID:
        print("Project ID not connected. Use config.connect(project_id) first.")
        return {}

    sub_path = os.path.join("DB_USER", "projects", config.UID, "data", paperbase, subbase)

    if not os.path.exists(sub_path):
        print(f"Error: Subbase '{subbase}' does not exist in paperbase '{paperbase}'.")
        return {}

    data_map = {}
    try:
        for filename in os.listdir(sub_path):
            file_path = os.path.join(sub_path, filename)
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    data_map[filename] = file.read()
        return data_map
    except Exception as e:
        print(f"Error retrieving subbase data: {e}")
        return {}
