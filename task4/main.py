from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional

from scraper import parse_arxiv
from database import save_to_db, get_all_data


app = FastAPI(title="Arxiv Parser API")


class ParseResponse(BaseModel):
    status: str
    message: str
    articles_saved: int = 0
    error_detail: Optional[str] = None


@app.get("/parse", response_model=ParseResponse)
async def parse_endpoint(url: str = Query(..., description="Ссылка на arxiv")):
    try:
        articles = parse_arxiv(url)
        if articles:
            await save_to_db(articles)
            return {
                "status": "success",
                "message": f"Успешно сохранено {len(articles)} статей",
                "articles_saved": len(articles)
            }
        return {"status": "error", "message": "Статей не найдено"}
    except Exception as e:
        return {"status": "error", "message": "Ошибка", "error_detail": str(e)}


@app.get("/get_data")
async def get_data_endpoint():
    data = await get_all_data()
    return data
