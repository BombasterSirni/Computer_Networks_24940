from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from urllib.parse import unquote, urlsplit, parse_qsl, urlencode, urlunsplit
from contextlib import asynccontextmanager

from app.scraper import parse_arxiv
from app.database import save_to_db, get_all_data, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="Arxiv Parser API", lifespan=lifespan)


class ParseResponse(BaseModel):
    status: str
    message: str
    articles_saved: int = 0
    error_detail: Optional[str] = None


@app.get("/parse", response_model=ParseResponse)
async def parse_and_save(
    url: str = Query(..., description="Ссылка на arxiv")
):
    target_url = unquote(url)

    if not target_url:
        raise HTTPException(status_code=400, detail="URL is required")

    print(f"[DEBUG] Получен URL: {target_url}")

    try:
        articles = parse_arxiv(target_url)

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
