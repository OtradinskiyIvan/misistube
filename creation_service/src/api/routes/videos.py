from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from uuid import UUID
from src.api.deps import get_video_service
from src.api.schemas.video import VideoUploadResponse, VideoDetailResponse, VideoListResponse
from src.services.video_service import VideoService
from src.domain.exceptions import VideoNotFoundError

router = APIRouter(prefix="/videos", tags=["videos"])

print("ROUTER INITIALIZED")

@router.options("/upload")
async def options_upload():
    return Response(status_code=200)

@router.options("/upload")
async def preflight_upload():
    print("OPTIONS HANDLER CALLED")
    return {}   # FastAPI сам добавит нужные CORS-заголовки

# 1. Сначала POST /upload (без параметров пути)
@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(...),
    
    service: VideoService = Depends(get_video_service),
):
    content = await file.read()
    video = await service.upload_video(title, description, content, file.filename)
    return VideoUploadResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        status=video.status.value,
        created_at=video.created_at,
    )

# 2. Затем GET / (список)
# src/api/routes/videos.py

@router.get("/", response_model=VideoListResponse)
async def list_videos(
    limit: int = 10,
    offset: int = 0,
    service: VideoService = Depends(get_video_service),
):
    videos = await service.get_video_list(limit, offset)
    
    # Правильное преобразование объектов в Pydantic-схемы
    video_items = [
        VideoUploadResponse(
            id=v.id,
            title=v.title,
            description=v.description,
            status=v.status.value,
            created_at=v.created_at,
        )
        for v in videos
    ]
    
    return VideoListResponse(items=video_items, total=len(videos))

# 3. В конце GET /{video_id} (с параметром пути)
@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: UUID,
    service: VideoService = Depends(get_video_service),
):
    try:
        video = await service.get_video_metadata(video_id)
        presigned_url = await service._storage.get_presigned_url(video.storage_key)
        return VideoDetailResponse(
            id=video.id,
            title=video.title,
            description=video.description,
            status=video.status.value,
            created_at=video.created_at,
            storage_url=presigned_url,
        )
    except VideoNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")