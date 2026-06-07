from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response, Query, Request
from fastapi.responses import Response
from uuid import UUID
from src.api.deps import get_video_service, get_current_user
from src.api.schemas.video import VideoUploadResponse, VideoDetailResponse, VideoListResponse, VideoStatusUpdate
from src.services.video_service import VideoService
from src.domain.exceptions import VideoNotFoundError, VideoUploadError
from src.core.config import settings

router = APIRouter(prefix="/videos", tags=["videos"])

@router.get("/upload")
async def get_upload_info():
    raise HTTPException(status_code=405, detail="Use POST to upload a video")

@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(
    title: str = Form(..., min_length=1, max_length=255),
    description: str = Form(..., min_length=1, max_length=1000),
    file: UploadFile = File(...),
    service: VideoService = Depends(get_video_service),
    user_id: UUID = Depends(get_current_user),
):
    content = await file.read()
    try:
        video = await service.upload_video(title, description, content, file.filename, user_id)
    except VideoUploadError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return VideoUploadResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        status=video.status.value,
        duration=video.duration,
        user_id=video.user_id,
        created_at=video.created_at,
        updated_at=video.updated_at,
    )

@router.get("/", response_model=VideoListResponse)
async def list_videos(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: VideoService = Depends(get_video_service),
    user_id: UUID = Depends(get_current_user),
):
    videos, total = await service.get_video_list(limit, offset, user_id=user_id)
    video_items = [
        VideoUploadResponse(
            id=v.id,
            title=v.title,
            description=v.description,
            status=v.status.value,
            duration=v.duration,
            user_id=v.user_id,
            created_at=v.created_at,
            updated_at=v.updated_at,
        )
        for v in videos
    ]
    return VideoListResponse(items=video_items, total=total)

@router.get("/{video_id}", response_model=VideoDetailResponse)
async def get_video(
    video_id: UUID,
    service: VideoService = Depends(get_video_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        video = await service.get_video_metadata(video_id)
        return VideoDetailResponse(
            id=video.id,
            title=video.title,
            description=video.description,
            status=video.status.value,
            duration=video.duration,
            user_id=video.user_id,
            created_at=video.created_at,
            updated_at=video.updated_at,
            storage_url=f"/videos/{video_id}/stream",
        )
    except VideoNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")

@router.get("/{video_id}/stream")
async def stream_video(
    video_id: UUID,
    request: Request,
    service: VideoService = Depends(get_video_service),
    _: UUID = Depends(get_current_user),
):

    try:
        video = await service.get_video_metadata(video_id)
    except VideoNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")

    range_header = request.headers.get("range")
    s3_data = await service.stream_video(video.storage_key, range_header)

    body = s3_data["Body"]
    content_type = s3_data["ContentType"]

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": content_type,
        "Content-Length": str(len(body)),
        "Cache-Control": "public, max-age=31536000",
    }

    if range_header:
        headers["Content-Range"] = s3_data["ContentRange"]
        return Response(content=body, status_code=206, headers=headers, media_type=content_type)

    return Response(content=body, status_code=200, headers=headers, media_type=content_type)

@router.patch("/{video_id}/status")
async def update_video_status(
    video_id: UUID,
    body: VideoStatusUpdate,
    service: VideoService = Depends(get_video_service),
    user_id: UUID = Depends(get_current_user),
):
    try:
        video = await service.update_video_status(video_id, body.status)
    except VideoNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoUploadResponse(
        id=video.id,
        title=video.title,
        description=video.description,
        status=video.status.value,
        duration=video.duration,
        user_id=video.user_id,
        created_at=video.created_at,
        updated_at=video.updated_at,
    )
