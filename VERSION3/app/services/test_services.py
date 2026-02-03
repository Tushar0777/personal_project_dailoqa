from .user_service import UserService
from .role_service import RoleService
from .playbook_service import PlaybookService
from .playbook_version_service import PlaybookVersionService

if __name__ == "__main__":
    # UserService test
    user_service = UserService()
    print("== USERS ==")
    print(user_service.get_user("user123"))
    print(user_service.get_user_roles("user123"))

    # RoleService test
    role_service = RoleService()
    print("== ROLES ==")
    print(role_service.get_permissions("EDITOR"))

    # PlaybookService test
    playbook_service = PlaybookService()
    print("== PLAYBOOKS ==")
    print(playbook_service.list_all_playbooks())
    # create new playbook test
    # playbook_service.create_playbook("pb001", "Title1", "Desc1", "editor123")

    # PlaybookVersionService test
    version_service = PlaybookVersionService()
    print("== VERSIONS ==")
    print(version_service.list_versions("pb001"))
    # version_service.add_version("pb001", 1, "Content v1")
