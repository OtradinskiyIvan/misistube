import { useState, useEffect, useCallback } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/interactions.js";
import { useAuth } from "../context/AuthContext.jsx";

export default function VideoInteractionsPage() {
  const { videoId } = useParams();
  const { isAuthenticated } = useAuth();

  const [liked, setLiked] = useState(false);
  const [likesCount, setLikesCount] = useState(0);
  const [comments, setComments] = useState([]);
  const [commentsTotal, setCommentsTotal] = useState(0);
  const [newComment, setNewComment] = useState("");
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const limit = 50;

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [countRes, commentsRes] = await Promise.all([
        api.likesCount(videoId),
        api.getComments(videoId, skip, limit),
      ]);
      setLikesCount(countRes.count);
      setComments(commentsRes.comments || []);
      setCommentsTotal(commentsRes.total || 0);

      if (isAuthenticated) {
        const likeRes = await api.isLiked(videoId);
        setLiked(likeRes.liked);
      }
    } catch (err) {
      setError(err.detail || "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [videoId, skip, isAuthenticated]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleLike = async () => {
    if (!isAuthenticated) return;
    try {
      if (liked) {
        await api.unlikeVideo(videoId);
        setLiked(false);
        setLikesCount((c) => c - 1);
      } else {
        await api.likeVideo(videoId);
        setLiked(true);
        setLikesCount((c) => c + 1);
      }
    } catch (err) {
      setError(err.detail || "Failed to toggle like");
    }
  };

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    if (!newComment.trim() || !isAuthenticated) return;
    try {
      await api.createComment(videoId, newComment.trim());
      setNewComment("");
      await fetchData();
    } catch (err) {
      setError(err.detail || "Failed to create comment");
    }
  };

  const handleDeleteComment = async (commentId) => {
    try {
      await api.deleteComment(commentId);
      await fetchData();
    } catch (err) {
      setError(err.detail || "Failed to delete comment");
    }
  };

  if (loading && comments.length === 0) {
    return <div className="text-center mt-6">Loading...</div>;
  }

  return (
    <div className="interactions-page">
      <h1>Video Interactions</h1>
      <p className="mb-4" style={{ color: "var(--misis-text-dark)", opacity: 0.7 }}>
        Video ID: {videoId}
      </p>

      {error && (
        <div className="badge badge-error mb-4" style={{ padding: "0.5rem 1rem" }}>
          {error}
          <button
            className="btn btn-sm"
            style={{ marginLeft: "0.5rem" }}
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}

      <div className="card mb-4">
        <div className="card__content">
          <div
            className={`like-button ${liked ? "like-button--active" : ""}`}
            onClick={handleLike}
          >
            {liked ? "❤️" : "🤍"} {likesCount} {likesCount === 1 ? "like" : "likes"}
          </div>
        </div>
      </div>

      <h2>Comments ({commentsTotal})</h2>

      {isAuthenticated ? (
        <form className="comment-form" onSubmit={handleCommentSubmit}>
          <textarea
            className="textarea"
            placeholder="Write a comment..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            rows={3}
          />
          <div>
            <button className="btn btn-primary" type="submit" disabled={!newComment.trim()}>
              Post Comment
            </button>
          </div>
        </form>
      ) : (
        <p className="mb-4" style={{ opacity: 0.6 }}>
          Log in to leave a comment.
        </p>
      )}

      <div className="comments-list">
        {comments.length === 0 && <p style={{ opacity: 0.5 }}>No comments yet.</p>}
        {comments.map((comment) => (
          <div key={comment.id} className="comment">
            <div className="comment__header">
              <span className="comment__author">User {comment.user_id.slice(0, 8)}...</span>
              <span className="comment__date">
                {new Date(comment.created_at).toLocaleDateString()}
                {comment.is_edited && " (edited)"}
              </span>
            </div>
            <div className="comment__content">{comment.content}</div>
            <div className="comment__actions">
              {isAuthenticated && (
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => handleDeleteComment(comment.id)}
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {commentsTotal > limit && (
        <div className="pagination mt-4">
          <button
            className="btn btn-sm btn-secondary"
            disabled={skip === 0}
            onClick={() => setSkip((s) => Math.max(0, s - limit))}
          >
            Previous
          </button>
          <span className="pagination__info">
            {skip + 1}–{Math.min(skip + limit, commentsTotal)} of {commentsTotal}
          </span>
          <button
            className="btn btn-sm btn-secondary"
            disabled={skip + limit >= commentsTotal}
            onClick={() => setSkip((s) => s + limit)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
