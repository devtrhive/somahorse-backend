from fastapi import APIRouter

router = APIRouter(prefix="/example", tags=["Example"])

@router.get("/")
def read_example():
    return {"msg": "This is an example endpoint"}
