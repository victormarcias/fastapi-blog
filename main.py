from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
##
from schemas import PostCreate, PostResponse
##
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: list[dict] = [
    {
        "id": 1,
        "author": "Victor Marcias",
        "title": "Aguante FastAPI",
        "content": "Apretás TAB en VSCode y te autocompleta todo, es una locura.",
        "date_posted": "Jul 8, 2026",
    },
    {
        "id": 2,
        "author": "Juana María",
        "title": "Python es genial para desarrollo web",
        "content": "Python es genial para desarrollo web, y FastAPI es un gran ejemplo de ello.",
        "date_posted": "July 8, 2026",
    },
    {
        "id": 3,
        "author": "Juan Pablo Folk",
        "title": "Folco programa en C++",
        "content": "Gana una fortuna imprimiendo logos en gorras cabeza.",
        "date_posted": "July 8, 2026",
    },
]


########################################
########################################
### API ###

@app.get("/api/posts", response_model=list[PostResponse])
def get_posts():
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(request: Request, post_id: int):
    for post in posts:
        if post["id"] == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Papá no aparece")

########################################
########################################
## Create Post
@app.post(
    "/api/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title": post.title,
        "content": post.content,
        "date_posted": "April 23, 2025",
    }
    posts.append(new_post)
    return new_post

########################################
########################################
### CONTENT

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(
        request, 
        "home.html", 
        {"posts": posts, "title": "PAGINA PRENCEPAL"},
    )

@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post["id"] == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(
                request,
                "post.html", 
                {"post": post, "title": title},
            )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="Papá no aparece"
    )


########################################
########################################
### ERROR HANDLER

@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exc: StarletteHTTPException):
    message = (
        exc.detail
        if exc.detail
        else "An error occurred while processing your request."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": message},
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

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY, 
            "title": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "Invalid request data. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )