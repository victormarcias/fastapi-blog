## main.py
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi.exception_handlers import (
    http_exception_handler,
    request_validation_exception_handler
)

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette.exceptions import HTTPException as StarletteHTTPException

import models
from config import settings
from database import engine, get_db
from routers import posts, users

## 
@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield 
    # Shutdown
    await engine.dispose()

## 
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")

##
templates = Jinja2Templates(directory="templates")

##
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])

###
### Templates
###

### POST PAGE
@app.get(
    "/posts/{post_id}", 
    include_in_schema=False
)
async def post_page(request: Request, post_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.id == post_id)
    )
    post = result.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {"post": post, "title": title},
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
#
#
### USER{id} POSTS PAGE - PAGINATED
@app.get("/users/{user_id}/posts", include_in_schema=False, name="user_posts")
async def user_posts_page(
    request: Request,
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    count_result = await db.execute(
        select(func.count())
        .select_from(models.Post)
        .where(models.Post.user_id == user_id),
    )
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_user),
    )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
            "limit": settings.posts_per_user,
            "has_more": has_more,
        },
    )

###
### Error Handler
###

### EXCEPTION HANDLER
@app.exception_handler(StarletteHTTPException)
async def general_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api"):
        return await http_exception_handler(request, exc)
    
    message = (
        exc.detail
        if exc.detail
        else "An error occurred while processing your request."
    )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "request": request, 
            "status_code": exc.status_code, 
            "detail": message
        },
        status_code=exc.status_code,
    )
#
#
### VALIDATION EXCEPTION HANDLER
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return await request_validation_exception_handler(request, exc)
    
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT, 
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request data. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )
#
#
### HOME
@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def home(request: Request, db: Annotated[AsyncSession, Depends(get_db)]):
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0

    result = await db.execute(
        select(models.Post)
        .options(selectinload(models.Post.author))
        .order_by(models.Post.date_posted.desc())
        .limit(settings.posts_per_page),
    )
    posts = result.scalars().all()

    has_more = len(posts) < total

    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home",
            "limit": settings.posts_per_page,
            "has_more": has_more,
        },
    )
#
#
### LOGIN
@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {"title": "Login"},
    )
#
#
### REGISTER
@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"title": "Register"},
    )
#
#
### ACCOUNT
@app.get("/account", include_in_schema=False)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "account.html",
        {"title": "Account"},
    )
#
#
### FORGOT PASSWORD
@app.get("/forgot-password", include_in_schema=False)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse(
        request,
        "forgot_password.html",
        {"title": "Forgot Password"},
    )
#
#
### RESET PASSWORD
@app.get("/reset-password", include_in_schema=False)
async def reset_password_page(request: Request):
    response = templates.TemplateResponse(
        request,
        "reset_password.html",
        {"title": "Reset Password"},
    )
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
#
# 
### HEALTH CHECK ENDPOINT
@app.get("/health")
async def health_check(db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        await db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        ) from exc
    return {"status": "healthy"}

