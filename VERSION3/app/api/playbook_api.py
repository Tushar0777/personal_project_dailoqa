from fastapi import APIRouter,Depends,Body
# from app.services.playbook_service import PlaybookService
from ..services.playbook_service import PlaybookService
# from app.api.deps import require_permission,get_current_user_id
from ..api.deps import require_permission,get_current_user


router=APIRouter(prefix="/playbooks",tags=['Playbooks'])

def get_playbook_services():
    return PlaybookService()

@router.get("/",dependencies=[Depends(require_permission("VIEW_PLAYBOOK"))])
def list_playbooks(
    service:PlaybookService=Depends(get_playbook_services)):
    return service.list_all_playbooks()


@router.post("/",dependencies=[Depends(require_permission("CREATE_PLAYBOOK"))])
def create_playbook(
    playbook_name:str=Body(...),
    title:str=Body(...),
    description:str=Body(...),
    user_id:str=Depends(get_current_user),
    service:PlaybookService=Depends(get_playbook_services)):

    return service.create_playbook(
        name=playbook_name,
        title=title,
        description=description,
        editor_id=user_id)

@router.delete("/",dependencies=[Depends(require_permission("DELETE_PLAYBOOK"))])
def delete_playbook(
    playbook_name:str=Body(...),
    service:PlaybookService=Depends(get_playbook_services)
):
    result=service.get_playbook_by_name(playbook_name)
    if not result["playbook"]:
        return {
            "status": "PLAYBOOK_NOT_FOUND",
            "playbook_name": playbook_name,
            "wcu": 0
        }
    playbook_id = result["playbook"]["primary_id"].replace("PLAYBOOK#", "")
    response = service.delete_playbook(playbook_id)
    if not response["deleted"]:
        return {
            "status": "PLAYBOOK_ALREADY_DELETED",
            "playbook_name": playbook_name,
            "wcu": 0
        }
    return {
        "status": "PLAYBOOK_DELETED",
        "playbook_name": playbook_name,
        "wcu": response["wcu"]
    }




