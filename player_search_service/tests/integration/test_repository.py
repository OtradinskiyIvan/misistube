import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.models import Video, VideoStatus
from src.infrastructure.search.repository import SQLAlchemyVideoRepository


class TestSQLAlchemyVideoRepository:
    
    @pytest.mark.asyncio
    async def test_search_ready_only(self, db_session: AsyncSession):
        """Поиск возвращает только status='ready'"""
        repo = SQLAlchemyVideoRepository(session=db_session)
        
        db_session.add_all([
            Video(title="Ready", storage_key="v1.m3u8", status=VideoStatus.READY),
            Video(title="Processing", storage_key="v2.m3u8", status=VideoStatus.PROCESSING),
        ])
        await db_session.commit()
        
        results, total = await repo.search(query="", offset=0, limit=10)
        
        assert total == 1
        assert results[0].title == "Ready"
    
    @pytest.mark.asyncio
    async def test_search_ilike(self, db_session: AsyncSession):
        """Регистронезависимый поиск"""
        repo = SQLAlchemyVideoRepository(session=db_session)
        db_session.add(Video(title="Кот играет", storage_key="cat.m3u8", status=VideoStatus.READY))
        await db_session.commit()
        
        results, total = await repo.search(query="кот", offset=0, limit=10)
        assert total == 1
        assert "Кот" in results[0].title