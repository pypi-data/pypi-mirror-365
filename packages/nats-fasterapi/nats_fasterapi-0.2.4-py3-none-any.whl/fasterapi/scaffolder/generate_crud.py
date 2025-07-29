from pathlib import Path

def create_crud_file(name: str):
    db_name=name.lower()
    schema_path = Path.cwd() / "schemas" / f"{db_name}.py"
    repo_path = Path.cwd() / "repositories" / f"{db_name}.py"

    if not schema_path.exists():
        print(f"❌ Schema file {schema_path} not found.")
        return

    class_name = "".join([part.capitalize() for part in db_name.split("_")]) + "Base"
    update_class_name = "".join([part.capitalize() for part in db_name.split("_")]) + "Update"
    create_class_name = "".join([part.capitalize() for part in db_name.split("_")]) + "Create"
    out_class_name = "".join([part.capitalize() for part in db_name.split("_")]) + "Out"
    crud_code = f'''
from core.database import db
from schemas.{db_name} import {update_class_name},{create_class_name},{out_class_name}

def create_{db_name}({db_name}_data: {create_class_name})->{out_class_name}:
    {db_name}_dict = {db_name}_data.model_dump()
    result = db.{db_name}s.insert_one({db_name}_dict)
    returnable_result = {out_class_name}(**result)
    return returnable_result

def get_{db_name}(filter_dict: dict)->{out_class_name}:
    result = db.{db_name}s.find_one(filter_dict)
    returnable_result = {out_class_name}(**result)
    return returnable_result
    
def update_{db_name}(filter_dict: dict, {db_name}_data: {update_class_name})->{out_class_name}:
    result = db.{db_name}s.find_one_and_update(
    filter_dict,
    {"$set": {db_name}_data.model_dump()},
    return_document=ReturnDocument.AFTER
)
    returnable_result = {out_class_name}(**result)
    return returnable_result

def delete_{db_name}(filter_dict: dict):
    return db.{db_name}s.delete_one(filter_dict)
'''.strip()

    with open(repo_path, "w") as f:
        f.write(crud_code)

    print(f"✅ CRUD for '{db_name}' created in repository/{db_name}.py")