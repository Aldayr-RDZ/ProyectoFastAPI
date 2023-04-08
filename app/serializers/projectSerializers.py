def projectResponseEntity(project)->dict:
    return {
        "id": str(project["_id"]),
        "name": project["name"],
        "description": project["description"],
        "year": project["year"],
        "category": project["category"],
        "langs": project["langs"],
        "image": project["image"]
    }

def projectResponseEntityEmbebed(project)->dict:
    return{
        "name": project["name"],
        "description": project["description"],
        "year": project["year"],
        "category": project["category"],
        "langs": project["langs"],
        "image": project["image"]
    }

def projectListEntity(projects) -> list:
    return [projectResponseEntity(project) for project in projects]
