from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from app.models.user import User
from fastapi import Depends, HTTPException
from app.dependencies import get_current_user
from fastapi.templating import Jinja2Templates
from app.routes import auth

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)


@app.get("/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/welcome")
async def welcome_page(
    request: Request,
    current_user: User = Depends(get_current_user),  # Ahora usa la versión modificada
):
    return templates.TemplateResponse(
        "welcome.html", {"request": request, "user": current_user}
    )


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response
