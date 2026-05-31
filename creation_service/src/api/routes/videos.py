from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from uuid import UUID
from src.api.deps import get_video_service
from src.api.schemas.video import VideoUploadResponse, VideoDetailResponse, VideoListResponse
from src.services.video_service import VideoService
from src.domain.exceptions import VideoNotFoundError

router = APIRouter(prefix="/videos", tags=["videos"])

@router.options("/upload")
async def preflight_upload():
    return Response(status_code=200)

@router.get("/upload")
async def get_upload_info():
    raise HTTPException(status_code=405, detail="Use POST to upload a video")

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(..., min_length=1),
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
        duration=video.duration,
        created_at=video.created_at,
    )

@router.get("/", response_model=VideoListResponse)
async def list_videos(
    limit: int = 10,
    offset: int = 0,
    service: VideoService = Depends(get_video_service),
):
    videos = await service.get_video_list(limit, offset)
    video_items = [
        VideoUploadResponse(
            id=v.id,
            title=v.title,
            description=v.description,
            status=v.status.value,
            duration=v.duration,
            created_at=v.created_at,
        )
        for v in videos
    ]
    return VideoListResponse(items=video_items, total=len(videos))

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
            duration=video.duration,
            created_at=video.created_at,
            storage_url=presigned_url,
        )
    except VideoNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")