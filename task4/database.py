from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from typing import List, Dict

DATABASE_URL = "postgresql+asyncpg://arxiv_user:arxiv_pass@localhost:5432/arxiv_db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def save_to_db(articles: List[Dict]):
    async with AsyncSessionLocal() as session:
        for article in articles:
            await session.execute(
                text("""
                    INSERT INTO arxiv_articles (arxiv_id, title, authors, subjects, url)
                    VALUES (:arxiv_id, :title, :authors, :subjects, :url)
                    ON CONFLICT (arxiv_id) DO NOTHING
                """),
                article
            )
        await session.commit()
        print(f"Сохранено в БД: {len(articles)} статей")

async def get_all_data() -> List[Dict]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT * FROM arxiv_articles ORDER BY parsed_at DESC"))
        return [dict(row) for row in result.mappings().all()]