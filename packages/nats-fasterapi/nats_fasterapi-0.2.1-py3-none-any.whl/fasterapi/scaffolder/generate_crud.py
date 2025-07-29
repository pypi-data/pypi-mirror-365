from pathlib import Path

def create_crud_file(name: str):
    schema_path = Path.cwd() / "schemas" / f"{name}.py"
    repo_path = Path.cwd() / "repositories" / f"{name}.py"

    if not schema_path.exists():
        print(f"❌ Schema file {schema_path} not found.")
        return

    class_name = "".join([part.capitalize() for part in name.split("_")]) + "Base"

    crud_code = f'''
from core.database import db
from schemas.{name} import {class_name}

def create_{name}({name}_data: {class_name}):
    {name}_dict = {name}_data.model_dump()
    return db.{name}s.insert_one({name}_dict)

def get_{name}(filter_dict: dict):
    return db.{name}s.find_one(filter_dict)

def update_{name}(filter_dict: dict, {name}_data: {class_name}):
    return db.{name}s.update_one(filter_dict, {name}_data.model_dump())

def delete_{name}(filter_dict: dict):
    return db.{name}s.delete_one(filter_dict)
'''.strip()

    with open(repo_path, "w") as f:
        f.write(crud_code)

    print(f"✅ CRUD for '{name}' created in repository/{name}.py")