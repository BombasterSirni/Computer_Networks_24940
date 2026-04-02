from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from urllib.parse import unquote

from app.scraper import parse_arxiv
from app.database import save_to_db, get_all_data


app = FastAPI(title="Arxiv Parser API")


class ParseResponse(BaseModel):
    status: str
    message: str
    articles_saved: int = 0
    error_detail: Optional[str] = None


@app.get("/parse")
async def parse_and_save(request: Request):

    raw_url = str(request.query_params).replace("url=", "")
    url = unquote(raw_url)
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    print(f"[DEBUG] Получен URL: {url}")

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
