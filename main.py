import uvicorn
from fastapi import FastAPI


def app_factory():
    app = FastAPI(description="Health app API")
    return app


if __name__ == "__main__":
    uvicorn.run(app_factory(), host="127.0.0.1", port=8000)
