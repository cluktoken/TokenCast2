from fastapi import FastAPI

app = FastAPI(
    title="TokenCast API",
    version="0.1.0"
)

@app.get("/")
async def root():
    return {
        "name": "TokenCast2",
        "version": "0.1.0",
        "status": "online"
    }