from fastapi import APIRouter,Depends
# from app.api.deps import require_permission
from .deps import require_permission
# from app.services.playbook_version_service import PlaybookVersionService
from ..services.playbook_version_service import PlaybookVersionService
from ..services.playbook_service import PlaybookService

router=APIRouter(prefix="/versions",tags=["Versions"])

def get_version_service()->PlaybookVersionService:
    return PlaybookVersionService()

def get_playbook_service()->PlaybookService:
    return PlaybookService()


@router.get("/{playbook_name}",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def list_versions(
    playbook_name:str,
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    result=playbook_service.get_playbook_by_name(playbook_name)

    if not result["playbook"]:
        return{
            "status":"PLAYBOOK NOT FOUND",
            "playbook_name":playbook_name,
            "wcu":0
        }
    playbook_id=result["playbook"]["primary_id"].replace("PLAYBOOK#","")
    return service.list_versions(playbook_id)


@router.get("/{playbook_name}/{version}",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def get_version(
    playbook_name:str,
    version:int,
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    result=playbook_service.get_playbook_service(playbook_name)

    if not result["playbook"]:
        return{
            "status":"PLAYBOOK NOT FOUND",
            "playbook_name":playbook_name,
            "wcu":0
        }
    playbook_id=result["playbook"]["primary_id"].replace("PLAYBOOK#","")

    return service.get_version(playbook_id,version)


@router.post("/{playbook_id}",dependencies=[Depends(require_permission("ADD_VERSION"))])
def add_version(
    playbook_name:str,
    version:int,
    content:str,
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):

    result=playbook_service.get_playbook_service(playbook_name)

    if not result["playbook"]:
        return{
            "status":"PLAYBOOK NOT FOUND",
            "playbook_name":playbook_name,
            "wcu":0
        }
    playbook_id=result["playbook"]["primary_id"].replace("PLAYBOOK#","")
    return service.add_version(playbook_id,version,content)


@router.delete("/{playbook_name}/{version}/soft",dependencies=[Depends(require_permission("DELETE_VERSION"))])
def soft_delete_version(
    playbook_name:str, 
    version:int, 
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    
    result=playbook_service.get_playbook_service(playbook_name)

    if not result["playbook"]:
        return{
            "status":"PLAYBOOK NOT FOUND",
            "playbook_name":playbook_name,
            "wcu":0
        }
    playbook_id=result["playbook"]["primary_id"].replace("PLAYBOOK#","")
    return service.soft_delete_version(playbook_id, version)


@router.delete("/{playbook_name}/{version}",dependencies=[Depends(require_permission("DELETE_VERSION"))])
def hard_delete_version(
    playbook_name:str, 
    version:int, 
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    
    result=playbook_service.get_playbook_service(playbook_name)

    if not result["playbook"]:
        return{
            "status":"PLAYBOOK NOT FOUND",
            "playbook_name":playbook_name,
            "wcu":0
        }
    playbook_id=result["playbook"]["primary_id"].replace("PLAYBOOK#","")
    return service.hard_delete_version(playbook_id, version)


@router.put("/{playbook_name}/{version}",dependencies=[Depends(require_permission("EDIT_VERSION"))])
def update_version(
    playbook_name:str, 
    version:int, 
    content:str, 
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    
    result=playbook_service.get_playbook_service(playbook_name)

    if not result["playbook"]:
        return{
            "status":"PLAYBOOK NOT FOUND",
            "playbook_name":playbook_name,
            "wcu":0
        }
    playbook_id=result["playbook"]["primary_id"].replace("PLAYBOOK#","")
    return service.update_version(playbook_id, version, content)


@router.put("/{playbook_name}/{version}/rollback",dependencies=[Depends(require_permission("EDIT_VERSION"))])
def rollback_version(
    playbook_name:str, 
    version:int, 
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)):
    
    result=playbook_service.get_playbook_service(playbook_name)

    if not result["playbook"]:
        return{
            "status":"PLAYBOOK NOT FOUND",
            "playbook_name":playbook_name,
            "wcu":0
        }
    playbook_id=result["playbook"]["primary_id"].replace("PLAYBOOK#","")
    return service.rollback_version(playbook_id, version)

# Optional: Endpoint to clear previous_content
# @router.delete("/{playbook_id}/{version}/previous-content", dependencies=[Depends(require_permission("EDIT_VERSION"))])
# def clear_previous_content(playbook_id: str, version: int, service: PlaybookVersionService = Depends(get_version_service)):
#     return service.clear_previous_content(playbook_id, version)
