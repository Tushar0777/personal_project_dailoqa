from fastapi import APIRouter,Depends
from app.services.playbook_service import PlaybookService
from app.api.deps import require_permission,get_current_user_id


router=APIRouter(prefix="/playbooks",tags=['Playbooks'])

def get_playbook_services():
    return PlaybookService()

@router.get("/",dependencies=[Depends(require_permission("VIEW_PLAYBOOK"))])
def list_playbooks(service:PlaybookService=Depends(get_playbook_services)):
    return service.list_all_playbooks()

@router.post("/",dependencies=[Depends(require_permission("CREATE_PLAYBOOK"))])
def create_playbook(playbook_id:str,title:str,description:str,user_id:str=Depends(get_playbook_services),service:PlaybookService=Depends(get_playbook_services)):

    return service.create_playbook(playbook_id=playbook_id,title=title,description=description,editor_id=user_id)



