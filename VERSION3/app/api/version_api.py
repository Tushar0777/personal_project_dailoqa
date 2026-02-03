from fastapi import APIRouter,Depends
# from app.api.deps import require_permission
from .deps import require_permission
# from app.services.playbook_version_service import PlaybookVersionService
from ..services.playbook_version_service import PlaybookVersionService

router=APIRouter(prefix="/versions",tags=["Versions"])

def get_version_service()->PlaybookVersionService:
    return PlaybookVersionService()


@router.get("/{playbook_id}",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def list_versions(playbook_id:str,service:PlaybookVersionService=Depends(get_version_service)):
    return service.list_versions(playbook_id)


@router.get("/{playbook_id}/{version}",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def get_version(playbook_id:str,version:int,service:PlaybookVersionService=Depends(get_version_service)):
    return service.get_version(playbook_id,version)


@router.post("/{playbook_id}",dependencies=[Depends(require_permission("ADD_VERSION"))])
def add_version(playbook_id:str,version:int,content:str,service:PlaybookVersionService=Depends(get_version_service)):
    return service.add_version(playbook_id,version,content)


@router.delete("/{playbook_id}/{version}/soft",dependencies=[Depends(require_permission("DELETE_VERSION"))])
def soft_delete_version(playbook_id:str, version:int, service:PlaybookVersionService=Depends(get_version_service)):
    return service.soft_delete_version(playbook_id, version)


@router.delete("/{playbook_id}/{version}",dependencies=[Depends(require_permission("DELETE_VERSION"))])
def hard_delete_version(playbook_id:str, version:int, service:PlaybookVersionService=Depends(get_version_service)):
    return service.hard_delete_version(playbook_id, version)


@router.put("/{playbook_id}/{version}",dependencies=[Depends(require_permission("EDIT_VERSION"))])
def update_version(playbook_id:str, version:int, content:str, service:PlaybookVersionService=Depends(get_version_service)):
    return service.update_version(playbook_id, version, content)


@router.put("/{playbook_id}/{version}/rollback",dependencies=[Depends(require_permission("EDIT_VERSION"))])
def rollback_version(playbook_id:str, version:int, service:PlaybookVersionService=Depends(get_version_service)):
    return service.rollback_version(playbook_id, version)

# Optional: Endpoint to clear previous_content
# @router.delete("/{playbook_id}/{version}/previous-content", dependencies=[Depends(require_permission("EDIT_VERSION"))])
# def clear_previous_content(playbook_id: str, version: int, service: PlaybookVersionService = Depends(get_version_service)):
#     return service.clear_previous_content(playbook_id, version)
