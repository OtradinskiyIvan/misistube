from datetime import datetime
from typing import Optional
from uuid import UUID


class User:
    def __init__(
        self,
        id: UUID,
        username: str,
        email: str,
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.username = username
        self.email = email
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username}, email={self.email})"


class UserProfile:
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        avatar_url: Optional[str] = None,
        bio: Optional[str] = None,
        location: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.avatar_url = avatar_url
        self.bio = bio
        self.location = location
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()


class UserRole:
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        role: str,
        assigned_at: Optional[datetime] = None,
        assigned_by: Optional[UUID] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.role = role
        self.assigned_at = assigned_at or datetime.utcnow()
        self.assigned_by = assigned_by
        self.expires_at = expires_at


class UserPreference:
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        is_profile_public: bool = True,
        allow_notifications: bool = True,
        notification_email: bool = True,
        show_subscriber_count: bool = True,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.is_profile_public = is_profile_public
        self.allow_notifications = allow_notifications
        self.notification_email = notification_email
        self.show_subscriber_count = show_subscriber_count
        self.updated_at = updated_at or datetime.utcnow()


class UserSubscription:
    def __init__(
        self,
        id: UUID,
        follower_id: UUID,
        following_id: UUID,
        subscribed_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.follower_id = follower_id
        self.following_id = following_id
        self.subscribed_at = subscribed_at or datetime.utcnow()


class UserStatistic:
    def __init__(
        self,
        id: UUID,
        user_id: UUID,
        total_videos: int = 0,
        total_views: int = 0,
        total_subscribers: int = 0,
        total_likes_received: int = 0,
        total_comments_received: int = 0,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self.id = id
        self.user_id = user_id
        self.total_videos = total_videos
        self.total_views = total_views
        self.total_subscribers = total_subscribers
        self.total_likes_received = total_likes_received
        self.total_comments_received = total_comments_received
        self.updated_at = updated_at or datetime.utcnow()
