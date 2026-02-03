from fastapi import APIRouter,Depends
from app.api.deps import require_permission
from app.services.playbook_version_service import PlaybookVersionService

router=APIRouter(prefix="/versions",tags=["Versions"])

def get_version_service()->PlaybookVersionService:
    return PlaybookVersionService()


@router.get("/{playbook_id}",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def list_versions(playbook_id:str,service:PlaybookVersionService=Depends(get_version_service)):
    return service.list_versions(playbook_id)


@router.get("/{playbook_id}/{version}",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def get_version(playbook_id:str,version:int,service:PlaybookVersionService=Depends(get_version_service)):
    return service.get_version(playbook_id,version)


@router.post("/{playbook_id}")
def add_version(playbook_id:str,version:int,content:str,service:PlaybookVersionService=Depends(get_version_service)):
    return service.add_version(playbook_id,version,content)
