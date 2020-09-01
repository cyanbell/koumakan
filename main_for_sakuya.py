import uvicorn

from izayoi_sakuya.factory import generate_app

app = generate_app()

if __name__ == "__main__":
    uvicorn.run(app)    
