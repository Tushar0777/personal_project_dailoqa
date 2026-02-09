from fastapi import APIRouter,Depends,Body,HTTPException,status
# from app.api.deps import require_permission
from .deps import require_permission
# from app.services.playbook_version_service import PlaybookVersionService
from ..services.playbook_version_service import PlaybookVersionService
from ..services.playbook_service import PlaybookService
from pydantic import BaseModel

class CreateVersionRequest(BaseModel):
    content: str


router=APIRouter(prefix="/playbooks",tags=["Versions"])

def get_version_service()->PlaybookVersionService:
    return PlaybookVersionService()

def get_playbook_service()->PlaybookService:
    return PlaybookService()

def get_playbook_id_by_name(playbook_service: PlaybookService, name: str) -> str:
    result = playbook_service.get_playbook_by_name(name)
    if not result["playbook"]:
        raise HTTPException(404, f"Playbook '{name}' not found")
    if result["playbook"].get("is_deleted"):
        raise HTTPException(410, f"Playbook '{name}' is deleted")
    return result["playbook"]["secondary_id"].replace("PLAYBOOK#", "")

@router.get(
    "/{playbook_name}/versions/latest",
    dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))]
)
def get_latest_version(
    playbook_name: str,
    service: PlaybookVersionService = Depends(get_version_service),
    playbook_service: PlaybookService = Depends(get_playbook_service)
):
    playbook_id = get_playbook_id_by_name(playbook_service, playbook_name)

    result = service.get_latest_version(playbook_id)

    if result["status"] == "PLAYBOOK_NOT_FOUND":
        raise HTTPException(404, "Playbook not found")

    if result["status"] == "NO_VERSIONS":
        raise HTTPException(404, "No versions available")

    if result["status"] == "LATEST_VERSION_NOT_AVAILABLE":
        raise HTTPException(409, "Latest version is deleted or unavailable")

    return result



@router.get("/{playbook_name}/versions",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def list_versions(
    playbook_name:str,
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    playbook_id = get_playbook_id_by_name(playbook_service, playbook_name)
    return service.list_versions(playbook_id)


@router.get("/{playbook_name}/versions/{version}",dependencies=[Depends(require_permission("VIEW_PLAYBOOK_CONTENT"))])
def get_version(
    playbook_name:str,
    version:int,
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    playbook_id = get_playbook_id_by_name(playbook_service, playbook_name)
    v = service.get_version(playbook_id, version)

    if not v["version"]:
        raise HTTPException(404, f"Version {version} not found")
    if v["version"].get("is_deleted"):
        raise HTTPException(410, f"Version {version} is deleted")

    return v



@router.post("/{playbook_name}/versions",
             dependencies=[Depends(require_permission("ADD_VERSION"))])
def add_version(
    playbook_name:str,
    # content:str=Body(...),
    body: CreateVersionRequest,
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
        content = body.content
        playbook_id = get_playbook_id_by_name(playbook_service, playbook_name)


        if not content.strip():
            raise HTTPException(400, "Content cannot be empty")

        result = service.add_version(playbook_id, content)
        if result["status"] == "VERSION_ALREADY_EXISTS":
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                f"Version already exists for playbook {playbook_name}"
            )

        return result




@router.delete(
    "/{playbook_name}/versions/{version}",
    dependencies=[Depends(require_permission("DELETE_VERSION"))]
)
def delete_version(
    playbook_name: str,
    version: int,
    service: PlaybookVersionService = Depends(get_version_service),
    playbook_service: PlaybookService = Depends(get_playbook_service)
):
    playbook_id = get_playbook_id_by_name(playbook_service, playbook_name)
    v = service.get_version(playbook_id, version)

    if not v["version"]:
        raise HTTPException(404, "Version not found")
    if v["version"].get("is_deleted"):
        raise HTTPException(409, "Version already deleted")

    return service.delete_version(playbook_id, version)



@router.put("/{playbook_name}/versions/{version}",dependencies=[Depends(require_permission("EDIT_VERSION"))])
def update_version(
    playbook_name:str, 
    version:int, 
    body: CreateVersionRequest, 
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)
    ):
    content=body.content
    playbook_id = get_playbook_id_by_name(playbook_service, playbook_name)
    v = service.get_version(playbook_id, version)

    if not v["version"]:
        raise HTTPException(404, "Version not found")
    if v["version"].get("is_deleted"):
        raise HTTPException(409, "Version is deleted")

    return service.update_version(playbook_id, version, content)


@router.put("/{playbook_name}/versions/{version}/rollback",dependencies=[Depends(require_permission("EDIT_VERSION"))])
def rollback_version(
    playbook_name:str, 
    version:int, 
    service:PlaybookVersionService=Depends(get_version_service),
    playbook_service:PlaybookService=Depends(get_playbook_service)):
    
    playbook_id = get_playbook_id_by_name(playbook_service, playbook_name)
    v = service.get_version(playbook_id, version)

    if not v["version"]:
        raise HTTPException(404, "Version not found")
    if v["version"].get("is_deleted"):
        raise HTTPException(409, "Cannot rollback deleted version")

    return service.rollback_version(playbook_id, version)

