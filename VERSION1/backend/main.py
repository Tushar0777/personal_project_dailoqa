from fastapi import FastAPI,HTTPException
from datetime import datetime
from store import playbooks

app=FastAPI()

@app.get("/playbooks")
def list_playbooks():
    return[{
        "playbook_id":pid,
        "latest_version":data["latest_version"]
    }
    for pid ,data in playbooks.items()

]

@app.get("/playbooks/{playbook_id}")
def get_latest_playbook(playbook_id:str):
    pb=playbooks.get(playbook_id)
    if not pb:
        raise HTTPException(status_code=404,detail="playbook does not exists")
    
    latest=pb['latest_version']
    # ye version hai 
    version_data=pb["versions"][latest]
    # basically dekh store me jake version ke andar content hai 
    return{
            "playbook_id":playbook_id,
            "version":latest,
            "content":version_data["content"]
           }


@app.get("/playbooks/{playbook_id}/versions")
def list_versions(playbook_id: str):
    pb = playbooks.get(playbook_id)
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")

    return list(pb["versions"].keys())



@app.post("/playbooks/{playbook_id}/versions")
def create_new_version(playbook_id: str, content: str):
    pb = playbooks.get(playbook_id)
    if not pb:
        raise HTTPException(status_code=404, detail="Playbook not found")


    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    version_key = f"VERSION#{timestamp}"

    pb["versions"][version_key] = {
        "content": content,
        "created_at": datetime.utcnow()
    }

    # Update latest version
    pb["latest_version"] = version_key

    return {
        "message": "New version created",
        "version": version_key
    }