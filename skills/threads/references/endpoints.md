# Threads API CLI ↔ Endpoint map

Base URL (API): `https://graph.threads.net/v1.0`

Token utilities (no `/v1.0`): `https://graph.threads.net`

## Publishing
- POST `/{threads-user-id}/threads` → `threads_cli publish create`
- POST `/{threads-user-id}/threads_publish` → `threads_cli publish publish`
- GET `/{threads-container-id}?fields=status` → `threads_cli publish status`
- POST `/{threads-media-id}/repost` → `threads_cli publish repost`
- DELETE `/{threads-media-id}` → `threads_cli publish delete`

## Media Retrieval
- GET `/{threads-media-id}` → `threads_cli media get`
- GET `/keyword_search` → `threads_cli media keyword-search`

## Reply Management
- GET `/{threads-media-id}/replies` → `threads_cli replies for-media`
- GET `/{threads-media-id}/conversation` → `threads_cli replies conversation`
- GET `/{threads-media-id}/pending_replies` → `threads_cli replies pending`
- POST `/{threads-reply-id}/manage_reply` → `threads_cli replies manage`
- POST `/{threads-reply-id}/manage_pending_reply` → `threads_cli replies manage-pending`

## User
- GET `/{threads-user-id}` → `threads_cli user get`
- GET `/{threads-user-id}/threads` → `threads_cli user threads`
- GET `/{threads-user-id}/threads_publishing_limit` → `threads_cli user publishing-limit`
- GET `/{threads-user-id}/replies` → `threads_cli user replies`
- GET `/{threads-user-id}/mentions` → `threads_cli user mentions`
- GET `/{threads-user-id}/ghost_posts` → `threads_cli user ghost-posts`
- GET `/profile_lookup?username=...` → `threads_cli user profile-lookup`
- GET `/profile_posts?username=...` → `threads_cli user profile-posts`

## Insights
- GET `/{threads-media-id}/insights` → `threads_cli insights media`
- GET `/{threads-user-id}/threads_insights` → `threads_cli insights user`

## Locations
- GET `/{location-id}` → `threads_cli locations get`
- GET `/location_search` → `threads_cli locations search`

## oEmbed
- GET `/oembed?url=...` → `threads_cli oembed`

## Debug
- GET `/debug_token` → `threads_cli debug-token`
- GET `/refresh_access_token` → `threads_cli token refresh`
