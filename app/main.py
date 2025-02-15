from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import auth, profile,social_auth,root,docs,finance,dashboard
from .config import description, title
from .analytics import metrics


import os
import logging
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


dir_path = os.path.dirname(os.path.realpath(__file__))

app = FastAPI(
    title=title,
    description=description,
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)


origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(root.router)
app.include_router(docs.router)
app.include_router(auth.router)
app.include_router(social_auth.router)
app.include_router(profile.router)
app.include_router(metrics.router)
app.include_router(dashboard.dashboard_router)
app.include_router(finance.financial_router)
templates = Jinja2Templates(directory="templates")