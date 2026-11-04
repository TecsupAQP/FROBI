"""Application factory. Module routers are mounted here as they are implemented."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    return FastAPI(title="FROBI API", version="0.1.0")
