from fastapi import FastAPI

<<<<<<< HEAD
app = FastAPI(
    title="Todo API",
    version="0.1.0",
)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
=======

app = FastAPI()

@app.get('hi/')
async def main():
    return {'message': 'hi'}



>>>>>>> 428b6cdf20630654770c53747ee5931035296d25
