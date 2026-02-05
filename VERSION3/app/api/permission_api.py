from fastapi import APIRouter, Depends, HTTPException, status
from ..services.permission_service import PermissionService
from ..services.user_service import UserService
from ..services.role_service import RoleService
from ..api.deps import require_permission

router = APIRouter(prefix="/permissions", tags=["Permissions"])

def get_permission_service():
    return PermissionService()

def get_user_service():
    return UserService()

def get_role_service():
    return RoleService()


# ---------- ROLE PERMISSIONS ----------

@router.get("/{role_name}", dependencies=[Depends(require_permission("VIEW_ROLE"))])
def list_permissions(role_name: str, service: PermissionService = Depends(get_permission_service)):
    return service.list_permissions(role_name)


@router.post("/{role_name}", dependencies=[Depends(require_permission("EDIT_ROLE"))])
def add_permission(role_name: str, permission: str, service: PermissionService = Depends(get_permission_service)):
    return service.add_permission(role_name, permission)


@router.delete("/{role_name}", dependencies=[Depends(require_permission("EDIT_ROLE"))])
def remove_permission(role_name: str, permission: str, service: PermissionService = Depends(get_permission_service)):
    return service.remove_permission(role_name, permission)

# , dependencies=[Depends(require_permission("EDIT_ROLE"))]
@router.post("/{role_name}/assign-all")
def assign_all_permissions(
    role_name: str, 
    all_permissions: list[str], 
    service: PermissionService = Depends(get_permission_service)):
    return service.assign_all_permissions(role_name, all_permissions)

# , dependencies=[Depends(require_permission("EDIT_ROLE"))]
@router.post("/bootstrap-admin-permissions")
def bootstrap_admin_permissions(
    all_permissions: list[str], 
    service: PermissionService = Depends(get_permission_service)):
    return service.bootstrap_admin_permissions(all_permissions)


# ---------- USER PERMISSIONS ----------

@router.get("/user/{user_id}", dependencies=[Depends(require_permission("VIEW_ROLE"))])
def get_user_permissions(user_id: str,
                         service: PermissionService = Depends(get_permission_service),
                         user_service: UserService = Depends(get_user_service),
                         role_service: RoleService = Depends(get_role_service)):
    return service.get_user_permissions(user_id, user_service, role_service)






# from fastapi import APIRouter, Depends, HTTPException, status
# from ..services.permission_service import PermissionService
# from ..api.deps import require_permission

# router = APIRouter(prefix="/permissions", tags=["Permissions"])

# def get_permission_service():
#     return PermissionService()


# @router.get("/{role_name}", dependencies=[Depends(require_permission("VIEW_ROLE"))])
# def list_permissions(role_name: str, service: PermissionService = Depends(get_permission_service)):
#     return service.list_permissions(role_name)


# @router.post("/{role_name}", dependencies=[Depends(require_permission("EDIT_ROLE"))])
# def add_permission(role_name: str, permission: str, service: PermissionService = Depends(get_permission_service)):
#     return service.add_permission(role_name, permission)


# @router.delete("/{role_name}", dependencies=[Depends(require_permission("EDIT_ROLE"))])
# def remove_permission(role_name: str, permission: str, service: PermissionService = Depends(get_permission_service)):
#     return service.remove_permission(role_name, permission)


# @router.post("/{role_name}/assign-all", dependencies=[Depends(require_permission("EDIT_ROLE"))])
# def assign_all_permissions(role_name: str, all_permissions: list[str], service: PermissionService = Depends(get_permission_service)):
#     return service.assign_all_permissions(role_name, all_permissions)
