# api/routes/videos.py
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from uuid import UUID
from src.services.video_service import VideoService
from src.api.deps import get_video_service
from src.api.schemas.video import VideoUploadResponse, VideoDetailResponse, VideoListResponse

router = APIRouter(prefix="/videos", tags=["videos"])

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    video_service: VideoService = Depends(get_video_service),
):
    # Читаем файл (для больших видео нужно стримить, но базовая версия)
    content = await file.read()
    video = await video_service.upload_video(title, description, content, file.filename)
    return VideoUploadResponse.from_entity(video)

@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: UUID,
    video_service: VideoService = Depends(get_video_service),
):
    video = await video_service.get_video_metadata(video_id)
    # Генерируем presigned URL для S3 (если статус READY)
    presigned_url = await video_service._storage.get_presigned_url(video.storage_key)
    return VideoDetailResponse.from_entity(video, presigned_url)

@router.get("/", response_model=VideoListResponse)
async def list_videos(
    limit: int = 10,
    offset: int = 0,
    video_service: VideoService = Depends(get_video_service),
):
    videos = await video_service.get_video_list(limit, offset)
    return VideoListResponse(items=videos, total=len(videos))