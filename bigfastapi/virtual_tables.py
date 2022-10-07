from fastapi import APIRouter

app = APIRouter(tags=["Virtual Tables"])


@app.post("/virtual-tables", status_code=201)
def create_virtual_table():
    pass


@app.get("/virtual-tables", status_code=200)
def get_virtual_tables():
    pass
