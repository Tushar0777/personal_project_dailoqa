from fastapi import FastAPI,HTTPException
from .dbconnect import table
from .crud import (create_playbook,create_new_version,update_version_content,get_latest_version,list_all_playbooks,list_all_versions)
from . import model

app=FastAPI()
# PS D:\Local Disk (D)\Dailoqa(Intern)\30jan_project\version1\VERSION2> 
# uvicorn app.main:app --reload

@app.post("/playbooks")
def create_playbook_api(payload:model.PlaybookCreate):
    try:
        create_playbook(table,payload.playbook_id)
        return {"message":"Playbook created"}
    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))


@app.post("/playbooks/{playbook_id}/versions")
def create_version_api(playbook_id:str,payload:model.VersionCreate):
    try:
        create_new_version(table,playbook_id,payload.content)
        return{"message":"Version created"}
    except Exception as e:
        raise HTTPException(status_code=404,detail=str(e))



@app.get("/playbooks/{playbook_id}/versions/latest",response_model=model.VersionResponse)
def get_latest_version_api(playbook_id:str):
    item=get_latest_version(table,playbook_id)
    return item



@app.put("/playbooks/{playbook_id}/versions/{version}")
def updated_version_api(playbook_id:str,version:int,payload:model.VersionCreate):
    update_version_content(table,playbook_id,version,payload.content)
    return {"message":"version updated"}



@app.get("/playbooks")
def list_playbooks():
    return list_all_playbooks(table)

@app.get("/playbooks/{playbook_id}/versions")
def list_versions(playbook_id:str):
    return list_all_versions(table,playbook_id)



# if __name__=="__main__":
#     get_latest_version(table,"playbook1")
