from fastapi import FastAPI
# from app.api import auth_api,playbook_api,version_api
from .api import auth_api,playbook_api,version_api,user_api,permission_api

def create_app() -> FastAPI:
    app = FastAPI(
        title="Playbook Platform",
        version="1.0.0",
        description="Role-based Playbook Management System"
    )

    app.include_router(auth_api.router, tags=["Auth"])
    app.include_router(playbook_api.router, tags=["Playbooks"])
    app.include_router(version_api.router,tags=["Versions"])
    app.include_router(user_api.router,tags=["users"])
    app.include_router(permission_api.router,tags=["Permission"])



    @app.get("/")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
