from fastapi import FastAPI


app = FastAPI()

@app.get('hi/')
async def main():
    return {'message': 'hi'}



