import fastapi
from prometheus_fastapi_instrumentator import Instrumentator


def setup_prometheus(app: fastapi.FastAPI):
    Instrumentator().instrument(app).expose(app)
