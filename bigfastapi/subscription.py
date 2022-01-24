from fastapi import APIRouter
import fastapi

app = ApiRouter(tags=["Subscription"])
app = Fastapi


@app.get('/subscription/ping')
def ping():
    return {
        "status": "Good",
        "msg": "Eric is Up and Running"
    }
