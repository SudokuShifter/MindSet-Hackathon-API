import uvicorn

from src.bootstrap import bootstrap

app = bootstrap().start_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
