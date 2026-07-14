from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, ai_assistant

router = APIRouter(prefix="/ai", tags=["AI Assistant"])

@router.post("/query", response_model=schemas.AIQueryResponse)
def post_ai_query(payload: schemas.AIQueryRequest, db: Session = Depends(get_db)):
    result = ai_assistant.query_assistant(payload.query, db)
    return result
