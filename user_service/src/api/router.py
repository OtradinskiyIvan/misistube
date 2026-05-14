from fastapi import APIRouter, Depends

from src.deps import get_logger_dep, get_settings

router = APIRouter()

@router.get("/health")
async def health_check(
    logger=Depends(get_logger_dep),
    settings=Depends(get_settings),
):
    logger.info("health_check.requested")
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.SERVICE_VERSION,
    }