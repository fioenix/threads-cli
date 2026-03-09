"""API client for Threads API."""

import time
import random
import requests
from typing import Optional, Dict, Any


class ThreadsAPI:
    """Threads API client."""

    BASE_URL = "https://graph.threads.net/v1.0"
    # Token endpoints are on graph.threads.net without version prefix
    TOKEN_BASE_URL = "https://graph.threads.net"

    def __init__(self, access_token: str, *, timeout: int = 60, max_retries: int = 3):
        self.access_token = access_token
        self.session = requests.Session()
        self.timeout = timeout
        self.max_retries = max_retries

    def _request(self, method: str, base_url: str, endpoint: str,
                 *, params: Optional[Dict[str, Any]] = None,
                 data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{base_url}/{endpoint}" if endpoint else base_url
        if params is None:
            params = {}
        params["access_token"] = self.access_token

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self.session.request(method, url, params=params, data=data, timeout=self.timeout)

                # Retry on transient server/rate errors
                if resp.status_code in (429, 500, 502, 503, 504):
                    if attempt < self.max_retries:
                        # exponential backoff + jitter
                        sleep_s = (2 ** attempt) * 0.5 + random.random() * 0.25
                        time.sleep(sleep_s)
                        continue

                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                last_exc = e
                if attempt < self.max_retries:
                    sleep_s = (2 ** attempt) * 0.5 + random.random() * 0.25
                    time.sleep(sleep_s)
                    continue
                raise

        # Should not reach here
        raise last_exc if last_exc else RuntimeError("Request failed")

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the Threads API."""
        return self._request("GET", self.BASE_URL, endpoint, params=params)

    def _post(self, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to the Threads API."""
        return self._request("POST", self.BASE_URL, endpoint, params=params, data=data)

    def _delete(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a DELETE request to the Threads API."""
        return self._request("DELETE", self.BASE_URL, endpoint, params=params)

    # User endpoints
    def get_me(self) -> Dict[str, Any]:
        """Get the current user's profile."""
        return self._get("me", {"fields": "id,username,name,threads_profile_picture_url,threads_biography"})

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """Get a specific user's profile."""
        return self._get(user_id, {"fields": "id,username,name,threads_profile_picture_url,threads_biography"})

    def get_user_threads(self, user_id: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get a user's threads."""
        params = {"fields": "id,media_product_type,media_type,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,is_quote_post"}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get(f"{user_id}/threads", params)

    def get_user_replies(self, user_id: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get a user's replies."""
        params = {}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get(f"{user_id}/replies", params)

    def get_user_mentions(self, user_id: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get mentions of a user."""
        params = {}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get(f"{user_id}/mentions", params)

    def get_publishing_limit(self, user_id: str) -> Dict[str, Any]:
        """Get the user's publishing limit."""
        return self._get(f"{user_id}/threads_publishing_limit", {"fields": "quota_usage,quota_duration,config"})

    # Media endpoints
    def get_media(self, media_id: str) -> Dict[str, Any]:
        """Get a specific media post."""
        return self._get(media_id, {"fields": "id,media_product_type,media_type,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,is_quote_post,children"})

    def search_media(self, q: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Search for media by keyword.

        Args:
            q: Search query string
            limit: Maximum number of results
            before: Pagination cursor
            after: Pagination cursor
        """
        params = {"q": q}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get("keyword_search", params)

    # Publishing endpoints
    def create_media_container(self, user_id: str, media_type: str, text: Optional[str] = None,
                                image_url: Optional[str] = None, video_url: Optional[str] = None,
                                carousel_items: Optional[list] = None, reply_to_id: Optional[str] = None,
                                quote_post_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a media container for publishing."""
        data = {"media_type": media_type}
        if text:
            data["text"] = text
        if image_url:
            data["image_url"] = image_url
        if video_url:
            data["video_url"] = video_url
        if carousel_items:
            data["children"] = ",".join(carousel_items)
        if reply_to_id:
            data["reply_to_id"] = reply_to_id
        if quote_post_id:
            data["quote_post_id"] = quote_post_id
        return self._post(f"{user_id}/threads", data)

    def publish_media(self, user_id: str, creation_id: str) -> Dict[str, Any]:
        """Publish a media container."""
        return self._post(f"{user_id}/threads_publish", {"creation_id": creation_id})

    def get_container_status(self, container_id: str) -> Dict[str, Any]:
        """Get the status of a media container."""
        return self._get(container_id, {"fields": "id,status,error_message"})

    def delete_media(self, media_id: str) -> Dict[str, Any]:
        """Delete a media post."""
        return self._delete(media_id)

    # Repost endpoint
    def repost_media(self, media_id: str) -> Dict[str, Any]:
        """Repost a media post."""
        return self._post(f"{media_id}/repost")

    # Ghost posts
    def get_ghost_posts(self, user_id: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get user's ghost posts."""
        params = {}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get(f"{user_id}/threads_ghost_posts", params)

    # Profile lookup and posts
    def profile_lookup(self, username: str) -> Dict[str, Any]:
        """Look up a profile by username.

        GET /profile_lookup?username=... (no user-id prefix per API reference)
        """
        return self._get("profile_lookup", {"username": username})

    def get_profile_posts(self, username: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get posts from a specific profile.

        GET /profile_posts?username=... (no user-id prefix per API reference)
        """
        params = {"username": username}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get("profile_posts", params)

    # Replies management
    def get_media_replies(self, media_id: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get replies for a media post.

        GET /{threads-media-id}/replies
        """
        params: Dict[str, Any] = {}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get(f"{media_id}/replies", params)

    def get_conversation(self, media_id: str, reverse: bool = False, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get conversation for a media post."""
        params: Dict[str, Any] = {}
        if reverse:
            params["reverse"] = "true"
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get(f"{media_id}/conversation", params)

    def get_pending_replies(self, media_id: str, limit: Optional[int] = None, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
        """Get pending replies for a media post.

        GET /{threads-media-id}/pending_replies (not user-id per API reference)
        """
        params = {}
        if limit:
            params["limit"] = limit
        if before:
            params["before"] = before
        if after:
            params["after"] = after
        return self._get(f"{media_id}/pending_replies", params)

    def manage_reply(self, reply_id: str, action: str) -> Dict[str, Any]:
        """Manage a reply (approve/hide).

        POST /{threads-reply-id}/manage_reply
        """
        return self._post(f"{reply_id}/manage_reply", {"action": action})

    def manage_pending_reply(self, reply_id: str, action: str) -> Dict[str, Any]:
        """Manage a pending reply.

        POST /{threads-reply-id}/manage_pending_reply
        """
        return self._post(f"{reply_id}/manage_pending_reply", {"action": action})

    # Insights
    def get_media_insights(self, media_id: str, metrics: str) -> Dict[str, Any]:
        """Get insights for a media post."""
        return self._get(f"{media_id}/insights", {"metric": metrics})

    def get_user_insights(self, user_id: str, metrics: str, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        """Get insights for a user."""
        params = {"metric": metrics}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return self._get(f"{user_id}/threads_insights", params)

    # Locations
    def get_location(self, location_id: str) -> Dict[str, Any]:
        """Get location info."""
        return self._get(location_id)

    def search_locations(self, q: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Search for locations.

        GET /location_search (no user-id prefix per API reference)
        """
        params = {"q": q}
        if limit:
            params["limit"] = limit
        return self._get("location_search", params)

    # OEmbed
    def get_oembed(self, url: str) -> Dict[str, Any]:
        """Get oEmbed for a URL."""
        return self._get("oembed", {"url": url})

    # Token management - these use TOKEN_BASE_URL (no version prefix)
    def debug_token(self, input_token: Optional[str] = None) -> Dict[str, Any]:
        """Debug a token.

        Uses https://graph.threads.net/debug_token (no /v1.0 per API reference)
        """
        params = {"access_token": self.access_token}
        if input_token:
            params["input_token"] = input_token
        url = f"{self.TOKEN_BASE_URL}/debug_token"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def refresh_token(self) -> Dict[str, Any]:
        """Refresh the access token.

        Uses https://graph.threads.net/refresh_access_token (no /v1.0 per API reference)
        """
        params = {"access_token": self.access_token}
        url = f"{self.TOKEN_BASE_URL}/refresh_access_token"
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()