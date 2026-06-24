const DEFAULT_GRAPH_VERSION = "v25.0";
const X_CREATE_POST_URL = "https://api.x.com/2/tweets";
const X_USER_LOOKUP_URL = "https://api.x.com/2/users/me";
const X_MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json";
const TIKTOK_CREATOR_INFO_URL = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/";
const TIKTOK_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/";
const TIKTOK_UPLOAD_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/";
const TIKTOK_STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/";
const TIKTOK_OAUTH_TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/";
const GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token";
const YOUTUBE_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels";
const YOUTUBE_ANALYTICS_REPORTS_URL = "https://youtubeanalytics.googleapis.com/v2/reports";
const YOUTUBE_UPLOAD_INIT_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status";
const SPOTIFY_OEMBED_URL = "https://open.spotify.com/oembed";
const DEFAULT_QUEUE_URL = "https://www.lilyroo.com/admin/future-posts.json";
const EXECUTION_STATE_PREFIX = "post:";
const MAX_SCHEDULE_ATTEMPTS = 3;

export default {
  async fetch(request, env, ctx) {
    try {
      return await handleRequest(request, env, ctx);
    } catch (error) {
      console.error(JSON.stringify({ level: "error", message: error.message, stack: error.stack }));
      return jsonResponse({ ok: false, error: error.message || "Unknown error" }, 500, request, env);
    }
  },
  async scheduled(controller, env, ctx) {
    ctx.waitUntil(runScheduledPosts(env, {
      scheduledTime: controller.scheduledTime || Date.now(),
      source: "cron",
    }));
  },
};

async function handleRequest(request, env) {
  const url = new URL(request.url);

  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: corsHeaders(request, env) });
  }

  if (!isAllowedOrigin(request, env)) {
    return jsonResponse({ ok: false, error: "Origin is not allowed" }, 403, request, env);
  }

  if (url.pathname === "/api/social/health" && request.method === "GET") {
    return jsonResponse({
      ok: true,
      service: "lilyroo-social-executor",
      graph_version: metaGraphVersion(env),
      execute_auth_required: true,
      supported_platforms: ["X", "Instagram", "Facebook", "TikTok", "YouTube Shorts"],
    }, 200, request, env);
  }

  if (url.pathname === "/api/social/readiness" && request.method === "GET") {
    const authError = await authorizationError(request, env);
    if (authError) {
      return jsonResponse({ ok: false, error: authError.message }, authError.status, request, env);
    }

    return jsonResponse(await readiness(env), 200, request, env);
  }

  if (url.pathname === "/api/social/metrics" && request.method === "GET") {
    const authError = await authorizationError(request, env);
    if (authError) {
      return jsonResponse({ ok: false, error: authError.message }, authError.status, request, env);
    }

    return jsonResponse(await socialMetrics(env), 200, request, env);
  }

  if (url.pathname === "/api/social/tiktok/status" && request.method === "GET") {
    const authError = await authorizationError(request, env);
    if (authError) {
      return jsonResponse({ ok: false, error: authError.message }, authError.status, request, env);
    }

    const publishId = text(url.searchParams.get("publish_id"));
    if (!publishId) {
      return jsonResponse({ ok: false, error: "publish_id is required" }, 400, request, env);
    }
    return jsonResponse(await tiktokPublishStatus(env, publishId), 200, request, env);
  }

  if (url.pathname === "/api/social/executions" && request.method === "GET") {
    const authError = await authorizationError(request, env);
    if (authError) {
      return jsonResponse({ ok: false, error: authError.message }, authError.status, request, env);
    }

    return jsonResponse(await executionStates(env), 200, request, env);
  }

  if (url.pathname === "/api/social/scheduler/dry-run" && request.method === "POST") {
    const authError = await authorizationError(request, env);
    if (authError) {
      return jsonResponse({ ok: false, error: authError.message }, authError.status, request, env);
    }

    const payload = await request.json().catch(() => ({}));
    const result = await runScheduledPosts(env, {
      scheduledTime: payload.scheduledTime || Date.now(),
      source: "dry-run",
      dryRun: true,
    });
    return jsonResponse(result, 200, request, env);
  }

  if (url.pathname !== "/api/social/execute" || request.method !== "POST") {
    return jsonResponse({ ok: false, error: "Not found" }, 404, request, env);
  }

  const authError = await authorizationError(request, env);
  if (authError) {
    return jsonResponse({ ok: false, error: authError.message }, authError.status, request, env);
  }

  const payload = await request.json();
  const result = await executeAndRecord(payload, env, { source: "manual" });
  return jsonResponse(result, 200, request, env);
}

async function executeAndRecord(payload, env, options = {}) {
  const normalized = normalizePostPayload(payload);
  const validation = await validateExecutablePost(normalized, env, options);

  if (payload.dryRun) {
    return {
      ok: true,
      dry_run: true,
      executable: validation.executable,
      status: validation.status,
      reason: validation.reason,
      platform: normalized.platform,
      post_id: normalized.postId,
      post_type: normalized.postType,
      execution_mode: normalized.executionMode,
      tiktok_posting_mode: tiktokPostingMode(normalized, env),
      media_url: mediaUrl(normalized, env),
      media_key: normalized.mediaKey,
    };
  }

  if (!validation.executable) {
    throw new Error(validation.reason || "Post is not executable");
  }

  const existing = normalized.postId ? await executionState(env, normalized.postId) : null;
  if (isTerminalExecutionStatus(existing?.status)) {
    return {
      ok: true,
      duplicate: true,
      platform: existing.platform || normalized.platform,
      post_id: normalized.postId,
      post_url: existing.post_url || "",
      state: existing,
    };
  }

  const attempt = Number(existing?.attempts || 0) + 1;
  if (options.source === "cron" && attempt > MAX_SCHEDULE_ATTEMPTS) {
    await writeExecutionState(env, normalized.postId, {
      ...existing,
      post_id: normalized.postId,
      platform: normalized.platform,
      status: "failed",
      reason: "max_attempts_exceeded",
      attempts: attempt - 1,
      updated_at: new Date().toISOString(),
    });
    throw new Error("max_attempts_exceeded");
  }

  try {
    const result = await executePost(normalized, env, options);
    if (normalized.postId) {
      await writeExecutionState(env, normalized.postId, {
        post_id: normalized.postId,
        platform: result.platform || normalized.platform,
        status: executionStatusFromResult(result),
        attempts: attempt,
        post_url: postUrlFromResult(result),
        external_id: externalIdFromResult(result),
        result,
        updated_at: new Date().toISOString(),
        source: options.source || "manual",
      });
    }
    return result;
  } catch (error) {
    if (normalized.postId) {
      await writeExecutionState(env, normalized.postId, {
        post_id: normalized.postId,
        platform: normalized.platform,
        status: "failed",
        attempts: attempt,
        error: error.message || "Unknown error",
        updated_at: new Date().toISOString(),
        source: options.source || "manual",
      });
    }
    throw error;
  }
}

async function executePost(payload, env, options = {}) {
  const platform = text(payload.platform).toLowerCase();

  if (platform === "x" || platform.startsWith("x")) return postX(payload, env);
  if (platform.includes("instagram")) return postInstagram(payload, env);
  if (platform.includes("facebook")) return postFacebook(payload, env);
  if (platform.includes("tiktok")) return postTikTok(payload, env);
  if (platform.includes("youtube")) return postYouTube(payload, env);

  throw new Error(`Unsupported platform: ${payload.platform || ""}`);
}

function scheduleAttemptState(payload, existing, options = {}) {
  return {
    ...existing,
    post_id: payload.postId,
    platform: payload.platform,
    status: "failed",
    reason: "max_attempts_exceeded",
    attempts: Number(existing?.attempts || MAX_SCHEDULE_ATTEMPTS),
    updated_at: new Date().toISOString(),
    source: options.source || "cron",
  };
}

async function runScheduledPosts(env, options = {}) {
  const store = executionStore(env);
  if (!store && !options.dryRun) {
    return { ok: false, error: "SOCIAL_EXECUTOR_STATE KV binding is required for scheduled posting" };
  }

  const now = new Date(options.scheduledTime || Date.now());
  const queue = await queuePosts(env);
  const due = queue.filter((post) => {
    const scheduled = new Date(text(post.scheduled_at || post.scheduledAt));
    return Number.isFinite(scheduled.getTime()) && scheduled <= now;
  });
  const results = [];

  for (const row of due) {
    const payload = normalizePostPayload(queueRowPayload(row));
    if (!payload.postId) continue;

    const existing = await executionState(env, payload.postId);
    if (isTerminalExecutionStatus(existing?.status)) {
      results.push({
        post_id: payload.postId,
        status: existing.status,
        post_url: existing.post_url || "",
        duplicate: true,
      });
      continue;
    }

    if (Number(existing?.attempts || 0) >= MAX_SCHEDULE_ATTEMPTS) {
      const state = scheduleAttemptState(payload, existing, options);
      if (!options.dryRun) await writeExecutionState(env, payload.postId, state);
      results.push(state);
      continue;
    }

    const validation = await validateExecutablePost(payload, env, { source: "cron" });
    if (!validation.executable) {
      const state = {
        post_id: payload.postId,
        platform: payload.platform,
        status: validation.status === "manual_only" ? "skipped" : "blocked",
        reason: validation.reason,
        attempts: Number(existing?.attempts || 0),
        updated_at: new Date().toISOString(),
        source: options.source || "cron",
      };
      if (!options.dryRun) await writeExecutionState(env, payload.postId, state);
      results.push(state);
      continue;
    }

    if (options.dryRun) {
      results.push({
        post_id: payload.postId,
        platform: payload.platform,
        status: "would_post",
        post_type: payload.postType,
      });
      continue;
    }

    try {
      const result = await executeAndRecord(payload, env, { source: options.source || "cron" });
      results.push({
        post_id: payload.postId,
        status: executionStatusFromResult(result),
        post_url: postUrlFromResult(result),
      });
    } catch (error) {
      results.push({ post_id: payload.postId, status: "failed", error: error.message || "Unknown error" });
    }
  }

  return {
    ok: true,
    dry_run: Boolean(options.dryRun),
    checked_at: now.toISOString(),
    due_count: due.length,
    result_count: results.length,
    results,
  };
}

async function queuePosts(env) {
  const url = text(env.SOCIAL_QUEUE_URL) || DEFAULT_QUEUE_URL;
  const response = await fetch(`${url}${url.includes("?") ? "&" : "?"}v=${Date.now()}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error(`Unable to fetch social queue (${response.status})`);
  const payload = await response.json();
  return Array.isArray(payload) ? payload : (payload.posts || []);
}

function queueRowPayload(row) {
  return {
    postId: row.id,
    platform: row.platform,
    song: row.song,
    text: row.text,
    replyText: row.reply_text || row.replyText,
    mediaKey: row.media_key || row.mediaKey || row.x_media_key || row.xMediaKey,
    imageryUrl: row.imagery_url || row.imageryUrl,
    clipUrl: row.clip_url || row.clipUrl,
    mediaUrl: row.clip_url || row.clipUrl || row.imagery_url || row.imageryUrl,
    approved: row.approved,
    executionMode: row.execution_mode || row.executionMode,
    postType: row.post_type || row.postType,
    desiredPrivacy: row.desired_privacy || row.desiredPrivacy,
    tiktokPostingMode: row.tiktok_posting_mode || row.tiktokPostingMode,
  };
}

function normalizePostPayload(payload) {
  const mediaKey = text(payload.mediaKey || payload.media_key || payload.x_media_key || payload.xMediaKey);
  const normalized = {
    ...payload,
    postId: text(payload.postId || payload.post_id || payload.id),
    platform: text(payload.platform),
    song: text(payload.song),
    text: text(payload.text),
    replyText: text(payload.replyText || payload.reply_text),
    mediaKey,
    imageryUrl: text(payload.imageryUrl || payload.imagery_url),
    clipUrl: text(payload.clipUrl || payload.clip_url),
    mediaUrl: text(payload.mediaUrl || payload.media_url || payload.clipUrl || payload.clip_url || payload.imageryUrl || payload.imagery_url),
    approved: truthy(payload.approved),
    executionMode: text(payload.executionMode || payload.execution_mode),
    postType: text(payload.postType || payload.post_type),
    desiredPrivacy: text(payload.desiredPrivacy || payload.desired_privacy),
    tiktokPostingMode: text(payload.tiktokPostingMode || payload.tiktok_posting_mode),
  };
  if (!normalized.executionMode) {
    normalized.executionMode = inferPostType(normalized).postType === "community" ? "manual" : "auto";
  }
  if (!normalized.postType) {
    normalized.postType = inferPostType(normalized).postType;
  }
  return normalized;
}

async function validateExecutablePost(payload, env, options = {}) {
  const platform = text(payload.platform).toLowerCase();
  const bodyText = text(payload.text);
  const postType = text(payload.postType).toLowerCase();
  const executionMode = text(payload.executionMode).toLowerCase();
  const source = options.source || "manual";
  const url = mediaUrl(payload, env);
  const video = videoUrl(payload, env);

  if (!platform) return blocked("blocked", "platform_required");
  if (!bodyText) return blocked("blocked", "text_required");
  if (source === "cron" && !payload.approved) return blocked("blocked", "not_approved");
  if (executionMode === "manual") return blocked("manual_only", "manual_only");
  if (postType === "community" || platform.includes("youtube community")) return blocked("manual_only", "youtube_community_manual_only");
  if (["story", "stories", "carousel"].includes(postType)) return blocked("blocked", `${postType}_unsupported_v1`);

  if (platform === "x" || platform.startsWith("x")) {
    const xOAuth1 = env.X_API_KEY && env.X_API_SECRET && env.X_ACCESS_TOKEN && env.X_ACCESS_TOKEN_SECRET;
    if (!env.X_USER_ACCESS_TOKEN && !xOAuth1) return blocked("blocked", "x_credentials_missing");
    if (postType === "video" || postType === "gif" || isVideoUrl(url) || /\.gif(\?|$)/i.test(url)) {
      return blocked("blocked", "x_video_or_gif_unsupported_v1");
    }
    return executable();
  }

  if (platform.includes("facebook")) {
    if (!env.META_LONG_LIVED_TOKEN || !env.FB_PAGE_ID) return blocked("blocked", "facebook_credentials_missing");
    if (postType === "video" || postType === "reel" || isVideoUrl(url)) return blocked("blocked", "facebook_video_unsupported_v1");
    return executable();
  }

  if (platform.includes("instagram")) {
    const accessToken = instagramAccessToken(env);
    if (!accessToken) return blocked("blocked", "instagram_credentials_missing");
    if (!url) return blocked("blocked", "instagram_media_required");
    if (!isImageUrl(url) && !isVideoUrl(url)) return blocked("blocked", "instagram_media_type_unsupported");
    const account = await instagramAccountValidation(env, accessToken);
    if (!account.ok) return blocked("blocked", account.reason);
    return executable();
  }

  if (platform.includes("tiktok")) {
    if (!tiktokCredentialsReady(env)) return blocked("blocked", "tiktok_credentials_missing");
    if (!video || !isHttpUrl(video) || !isVideoUrl(video)) return blocked("blocked", "tiktok_public_video_required");
    const postingMode = tiktokPostingMode(payload, env);
    if (postingMode === "direct" && source === "cron") {
      if (env.TIKTOK_PUBLIC_POSTING_APPROVED !== "true") return blocked("blocked", "tiktok_public_posting_not_approved");
      const creator = await tiktokCreatorInfo(env);
      const optionsList = creator?.data?.privacy_level_options || [];
      if (!optionsList.includes("PUBLIC_TO_EVERYONE")) return blocked("blocked", "tiktok_public_privacy_unavailable");
    }
    return executable();
  }

  if (platform.includes("youtube")) {
    if (!env.GOOGLE_CLIENT_ID || !env.YOUTUBE_REFRESH_TOKEN) return blocked("blocked", "youtube_credentials_missing");
    if (!video || !isHttpUrl(video) || !isVideoUrl(video)) return blocked("blocked", "youtube_public_video_required");
    return executable();
  }

  return blocked("blocked", "unsupported_platform");
}

function executable() {
  return { executable: true, status: "auto_ready", reason: "" };
}

function blocked(status, reason) {
  return { executable: false, status, reason };
}

function inferPostType(payload) {
  const platform = text(payload.platform).toLowerCase();
  const url = text(payload.clipUrl || payload.mediaUrl || payload.imageryUrl);
  if (platform.includes("youtube community")) return { postType: "community" };
  if (platform.includes("youtube") || platform.includes("tiktok")) return { postType: "video" };
  if (isVideoUrl(url)) return { postType: "video" };
  if (isImageUrl(url)) return { postType: "image" };
  return { postType: "text" };
}

async function executionStates(env) {
  const store = executionStore(env);
  if (!store) {
    return { ok: false, error: "SOCIAL_EXECUTOR_STATE KV binding is not configured", executions: [] };
  }
  const list = await store.list({ prefix: EXECUTION_STATE_PREFIX, limit: 1000 });
  const executions = [];
  for (const key of list.keys || []) {
    const value = await store.get(key.name, "json");
    if (value) executions.push(value);
  }
  executions.sort((a, b) => text(b.updated_at).localeCompare(text(a.updated_at)));
  return { ok: true, executions };
}

async function executionState(env, postId) {
  const store = executionStore(env);
  if (!store || !postId) return null;
  return store.get(`${EXECUTION_STATE_PREFIX}${postId}`, "json");
}

async function writeExecutionState(env, postId, state) {
  const store = executionStore(env);
  if (!store || !postId) return;
  await store.put(`${EXECUTION_STATE_PREFIX}${postId}`, JSON.stringify(state));
}

function executionStore(env) {
  return env.SOCIAL_EXECUTOR_STATE && typeof env.SOCIAL_EXECUTOR_STATE.get === "function"
    ? env.SOCIAL_EXECUTOR_STATE
    : null;
}

async function socialMetrics(env) {
  const [youtube, spotify, tiktok, instagram, facebook, x] = await Promise.all([
    metricProbe(() => youtubeMetrics(env)),
    metricProbe(() => spotifyMetrics(env)),
    metricProbe(() => tiktokMetrics(env)),
    metricProbe(() => instagramMetrics(env)),
    metricProbe(() => facebookMetrics(env)),
    metricProbe(() => xMetrics(env)),
  ]);

  return {
    ok: true,
    updated_at: new Date().toISOString(),
    platforms: {
      youtube,
      spotify,
      tiktok,
      instagram,
      facebook,
      x,
    },
  };
}

async function metricProbe(fn) {
  try {
    return await fn();
  } catch (error) {
    return unavailableMetric(metricErrorMessage(error), {
      status: error?.status || null,
    });
  }
}

function unavailableMetric(reason, extras = {}) {
  return {
    ok: false,
    reason,
    metrics: {},
    ...extras,
  };
}

function availableMetric(source, metrics, extras = {}) {
  return {
    ok: true,
    source,
    metrics,
    ...extras,
  };
}

async function youtubeMetrics(env) {
  const missing = ["GOOGLE_CLIENT_ID", "YOUTUBE_REFRESH_TOKEN"].filter((name) => !env[name]);
  if (missing.length) {
    return unavailableMetric("YouTube metrics need OAuth refresh credentials.", { missing_secrets: missing });
  }

  const token = await googleAccessToken(env);
  const channels = await jsonGetWithHeaders(YOUTUBE_CHANNELS_URL, {
    part: "snippet,statistics",
    mine: "true",
  }, {
    Authorization: `Bearer ${token}`,
  });
  const channel = (channels.items || [])[0] || {};
  const stats = channel.statistics || {};
  const metrics = {
    subscribers: numberOrNull(stats.subscriberCount),
    total_views: numberOrNull(stats.viewCount),
    video_count: numberOrNull(stats.videoCount),
  };
  const period = lastNDaysPeriod(28);
  let analyticsStatus = "not_requested";

  try {
    const analytics = await jsonGetWithHeaders(YOUTUBE_ANALYTICS_REPORTS_URL, {
      ids: "channel==MINE",
      startDate: period.startDate,
      endDate: period.endDate,
      metrics: "views,estimatedMinutesWatched",
    }, {
      Authorization: `Bearer ${token}`,
    });
    const row = (analytics.rows || [])[0] || [];
    metrics.views_28d = numberOrNull(row[0]);
    metrics.watch_time_minutes_28d = numberOrNull(row[1]);
    metrics.watch_time_hours_28d = metrics.watch_time_minutes_28d === null
      ? null
      : Math.round((metrics.watch_time_minutes_28d / 60) * 10) / 10;
    analyticsStatus = "ok";
  } catch (error) {
    analyticsStatus = metricErrorMessage(error);
  }

  return availableMetric("youtube-data-api", metrics, {
    channel_title: text(channel?.snippet?.title),
    period_28d: period,
    analytics_status: analyticsStatus,
  });
}

async function spotifyMetrics(env) {
  const releaseUrl = text(env.SPOTIFY_RELEASE_URL) || "https://open.spotify.com/album/4Al5eYOqGFMKEES5fDWIfI";
  const release = await jsonGet(SPOTIFY_OEMBED_URL, { url: releaseUrl });
  return availableMetric("spotify-oembed-public", {
    release_verified: release?.title ? 1 : 0,
  }, {
    release_url: releaseUrl,
    album_id: spotifyAlbumId(releaseUrl),
    title: text(release?.title),
    provider_name: text(release?.provider_name),
    provider_url: text(release?.provider_url),
    iframe_url: text(release?.iframe_url),
    thumbnail_url: text(release?.thumbnail_url),
    thumbnail_width: numberOrNull(release?.thumbnail_width),
    thumbnail_height: numberOrNull(release?.thumbnail_height),
    analytics_status: "Spotify streams, saves, monthly listeners, and artist followers require Spotify for Artists export or a connected analytics source.",
    credential_ok: false,
    profile_url: releaseUrl,
  });
}

async function tiktokMetrics(env) {
  if (!tiktokCredentialsReady(env)) {
    return unavailableMetric("TikTok metrics need TikTok OAuth credentials.", { missing_secrets: tiktokMissingCredentials(env) });
  }

  const creator = await tiktokCreatorInfo(env);
  const data = creator?.data || {};
  return unavailableMetric("TikTok Content Posting API returns creator and posting-permission info, not follower or profile-view analytics.", {
    source: "tiktok-content-posting-api",
    credential_ok: true,
    username: text(data.creator_username),
    display_name: text(data.creator_nickname),
    privacy_level_options: data.privacy_level_options || [],
    public_posting_ready: env.TIKTOK_PUBLIC_POSTING_APPROVED === "true"
      && (data.privacy_level_options || []).includes("PUBLIC_TO_EVERYONE"),
    metrics: {},
  });
}

async function instagramMetrics(env) {
  const accessToken = instagramAccessToken(env);
  if (!accessToken) {
    return unavailableMetric("Instagram metrics need IG_ACCESS_TOKEN or META_LONG_LIVED_TOKEN.", {
      missing_secrets: ["IG_ACCESS_TOKEN or META_LONG_LIVED_TOKEN"],
    });
  }

  const useInstagramLogin = isInstagramLoginToken(accessToken);
  const igBusinessAccountId = useInstagramLogin
    ? text(env.IG_BUSINESS_ACCOUNT_ID) || "me"
    : await instagramBusinessAccountId(env, accessToken);
  const base = useInstagramLogin ? instagramBase(env) : metaBase(env);
  const profile = await jsonGet(`${base}/${igBusinessAccountId}`, {
    fields: "username,followers_count,media_count",
    access_token: accessToken,
  });
  const username = text(profile.username);
  return availableMetric(useInstagramLogin ? "instagram-login-api" : "instagram-graph-api", {
    followers: numberOrNull(profile.followers_count),
    media_count: numberOrNull(profile.media_count),
  }, {
    username,
    profile_url: username ? `https://www.instagram.com/${username}/` : "",
  });
}

async function facebookMetrics(env) {
  const missing = ["META_LONG_LIVED_TOKEN", "FB_PAGE_ID"].filter((name) => !env[name]);
  if (missing.length) {
    return unavailableMetric("Facebook metrics need Meta page credentials.", { missing_secrets: missing });
  }

  const page = await jsonGet(`${metaBase(env)}/${env.FB_PAGE_ID}`, {
    fields: "name,link,followers_count,fan_count",
    access_token: env.META_LONG_LIVED_TOKEN,
  });
  const insights = await facebookPageInsights(env);
  const metrics = {
    followers: numberOrNull(page.followers_count),
    page_likes: numberOrNull(page.fan_count),
  };
  if (insights.reach_7d !== null) metrics.reach_7d = insights.reach_7d;

  return availableMetric("meta-graph-page", metrics, {
    page_name: text(page.name),
    profile_url: text(page.link) || `https://www.facebook.com/${env.FB_PAGE_ID}`,
    insights_period: insights.period,
    insights_status: insights.status,
  });
}

async function facebookPageInsights(env) {
  const period = lastNDaysPeriod(7);
  try {
    const payload = await jsonGet(`${metaBase(env)}/${env.FB_PAGE_ID}/insights/page_impressions_unique`, {
      period: "week",
      since: period.startDate,
      until: period.endDate,
      access_token: env.META_LONG_LIVED_TOKEN,
    });
    const reach7d = latestInsightValue(payload);
    return {
      reach_7d: reach7d,
      period: `${period.startDate}..${period.endDate}`,
      status: reach7d === null ? "No page_impressions_unique values returned" : "ok",
    };
  } catch (error) {
    return {
      reach_7d: null,
      period: `${period.startDate}..${period.endDate}`,
      status: metricErrorMessage(error),
    };
  }
}

async function xMetrics(env) {
  if (!env.X_USER_ACCESS_TOKEN) {
    return unavailableMetric("X metrics need X_USER_ACCESS_TOKEN with user lookup access.", {
      missing_secrets: ["X_USER_ACCESS_TOKEN"],
    });
  }

  const payload = await jsonGetWithHeaders(X_USER_LOOKUP_URL, {
    "user.fields": "public_metrics,username,name",
  }, {
    Authorization: `Bearer ${env.X_USER_ACCESS_TOKEN}`,
  });
  const user = payload.data || {};
  const publicMetrics = user.public_metrics || {};
  const username = text(user.username);
  return availableMetric("x-api-user-lookup", {
    followers: numberOrNull(publicMetrics.followers_count),
    following: numberOrNull(publicMetrics.following_count),
    post_count: numberOrNull(publicMetrics.tweet_count),
    listed_count: numberOrNull(publicMetrics.listed_count),
  }, {
    username,
    profile_url: username ? `https://x.com/${username}` : "",
  });
}

async function postFacebook(payload, env) {
  requireEnv(env, ["META_LONG_LIVED_TOKEN", "FB_PAGE_ID"], "Facebook posting");
  const url = mediaUrl(payload, env);
  const forceLink = text(payload.postType).toLowerCase() === "link";
  const endpoint = url && !forceLink ? `${metaBase(env)}/${env.FB_PAGE_ID}/photos` : `${metaBase(env)}/${env.FB_PAGE_ID}/feed`;
  const params = {
    access_token: env.META_LONG_LIVED_TOKEN,
  };
  if (url && !forceLink) {
    params.url = url;
    params.caption = appendCta(text(payload.text), text(payload.replyText));
    params.published = "true";
  } else {
    params.message = text(payload.text);
    if (payload.replyText) params.link = text(payload.replyText);
  }
  const data = await formPost(endpoint, params);
  const postId = data.post_id || data.id || "";
  return {
    ok: true,
    platform: "Facebook",
    post_id: postId,
    post_url: postId ? `https://www.facebook.com/${postId}` : "posted",
    raw: data,
  };
}

async function postInstagram(payload, env) {
  const accessToken = instagramAccessToken(env);
  if (!accessToken) throw new Error("Instagram posting needs Worker secrets/vars: IG_ACCESS_TOKEN or META_LONG_LIVED_TOKEN");
  const useInstagramLogin = isInstagramLoginToken(accessToken);
  const igBusinessAccountId = useInstagramLogin
    ? text(env.IG_BUSINESS_ACCOUNT_ID) || "me"
    : await instagramBusinessAccountId(env, accessToken);
  const url = mediaUrl(payload, env);
  if (!url) throw new Error("Instagram posting needs imageryUrl or clipUrl");
  const base = useInstagramLogin ? instagramBase(env) : metaBase(env);

  const isVideo = isVideoUrl(url);
  const createParams = {
    access_token: accessToken,
    caption: text(payload.text),
  };
  if (isVideo) {
    createParams.media_type = "REELS";
    createParams.video_url = url;
  } else {
    createParams.image_url = url;
  }

  const creation = await formPost(`${base}/${igBusinessAccountId}/media`, createParams);
  const creationId = creation.id;
  if (!creationId) throw new Error(`Instagram media creation failed: ${JSON.stringify(creation)}`);

  await waitForInstagramMedia(base, creationId, accessToken);
  const publish = await publishInstagramMedia(base, igBusinessAccountId, accessToken, creationId);

  return {
    ok: true,
    platform: "Instagram",
    creation_id: creationId,
    media_id: publish.id || "",
    raw: publish,
  };
}

async function publishInstagramMedia(base, igBusinessAccountId, accessToken, creationId) {
  const delays = [0, 5000, 10000, 15000, 30000];
  let lastError;
  for (const delay of delays) {
    if (delay) await sleep(delay);
    try {
      return await formPost(`${base}/${igBusinessAccountId}/media_publish`, {
        access_token: accessToken,
        creation_id: creationId,
      });
    } catch (error) {
      lastError = error;
      if (!isInstagramMediaNotReady(error)) throw error;
    }
  }
  throw lastError;
}

async function waitForInstagramMedia(base, creationId, accessToken) {
  const delays = [0, 3000, 5000, 10000, 15000, 30000];
  let lastStatus = "";
  for (const delay of delays) {
    if (delay) await sleep(delay);
    const status = await jsonGet(`${base}/${creationId}`, {
      fields: "status_code,status",
      access_token: accessToken,
    });
    lastStatus = text(status.status_code || status.status);
    if (!lastStatus || lastStatus === "FINISHED" || lastStatus === "PUBLISHED") return status;
    if (lastStatus === "ERROR" || lastStatus === "EXPIRED") {
      throw new Error(`Instagram media processing failed: ${JSON.stringify(status)}`);
    }
  }
  throw new Error(`Instagram media was not ready to publish; last status: ${lastStatus || "unknown"}`);
}

function isInstagramMediaNotReady(error) {
  const data = error?.data?.error || {};
  return data.code === 9007 || data.error_subcode === 2207027 || /media (id )?is not (available|ready)/i.test(error?.message || "");
}

function instagramAccessToken(env) {
  return text(env.IG_ACCESS_TOKEN) || text(env.META_LONG_LIVED_TOKEN);
}

function isInstagramLoginToken(token) {
  return text(token).startsWith("IG");
}

function instagramBase(env) {
  return `https://graph.instagram.com/${env.INSTAGRAM_GRAPH_VERSION || DEFAULT_GRAPH_VERSION}`;
}

async function instagramBusinessAccountId(env, accessToken) {
  if (env.IG_BUSINESS_ACCOUNT_ID) return env.IG_BUSINESS_ACCOUNT_ID;
  if (!env.FB_PAGE_ID) {
    throw new Error("Instagram posting needs Worker secrets/vars: IG_BUSINESS_ACCOUNT_ID or FB_PAGE_ID");
  }

  const page = await jsonGet(`${metaBase(env)}/${env.FB_PAGE_ID}`, {
    fields: "instagram_business_account",
    access_token: accessToken,
  });
  const id = text(page?.instagram_business_account?.id);
  if (!id) {
    throw new Error("Instagram posting could not resolve instagram_business_account from FB_PAGE_ID; set IG_BUSINESS_ACCOUNT_ID or reconnect the Instagram Business/Creator account to the Facebook Page");
  }
  return id;
}

async function instagramAccountValidation(env, accessToken) {
  if (isInstagramLoginToken(accessToken)) {
    return { ok: true, account_id_source: text(env.IG_BUSINESS_ACCOUNT_ID) ? "IG_BUSINESS_ACCOUNT_ID" : "me" };
  }
  if (text(env.IG_BUSINESS_ACCOUNT_ID)) {
    return { ok: true, account_id_source: "IG_BUSINESS_ACCOUNT_ID" };
  }
  if (!text(env.FB_PAGE_ID)) {
    return { ok: false, reason: "instagram_account_id_missing" };
  }
  try {
    await instagramBusinessAccountId(env, accessToken);
    return { ok: true, account_id_source: "FB_PAGE_ID" };
  } catch (error) {
    if (/instagram_business_account/i.test(error?.message || "")) {
      return { ok: false, reason: "instagram_business_account_unresolved" };
    }
    return { ok: false, reason: "instagram_account_validation_failed" };
  }
}

async function postTikTok(payload, env) {
  const url = videoUrl(payload, env);
  if (!url || !isHttpUrl(url)) {
    throw new Error("TikTok posting from the website needs a public clipUrl video URL");
  }

  const postingMode = tiktokPostingMode(payload, env);
  const sourceInfo = {
    source: "PULL_FROM_URL",
    video_url: url,
  };
  const initPayload = {
    source_info: {
      ...sourceInfo,
    },
  };

  if (postingMode === "direct") {
    const creator = await tiktokCreatorInfo(env);
    const options = creator?.data?.privacy_level_options || [];
    const desired = tiktokDesiredPrivacy(payload, env);
    const privacy = options.includes(desired) ? desired : (options.includes("SELF_ONLY") ? "SELF_ONLY" : (options[0] || "SELF_ONLY"));
    const disclosure = tiktokDisclosure(payload, env);
    initPayload.post_info = {
      title: text(payload.text),
      privacy_level: privacy,
      disable_comment: false,
      disable_duet: false,
      disable_stitch: false,
      brand_content_toggle: disclosure.brandContent,
      brand_organic_toggle: disclosure.brandOrganic,
      is_aigc: env.TIKTOK_IS_AIGC !== "false",
    };
  }

  const init = await jsonPost(postingMode === "upload" ? TIKTOK_UPLOAD_INIT_URL : TIKTOK_INIT_URL, initPayload, {
    Authorization: await tiktokAuthorization(env),
  });

  const publishId = init?.data?.publish_id || "";
  if (!publishId) throw new Error(`TikTok init failed: ${JSON.stringify(init)}`);
  const publishStatus = await tiktokPublishStatus(env, publishId).catch((error) => ({
    ok: false,
    error: metricErrorMessage(error),
    status_code: error?.status || null,
  }));
  return {
    ok: true,
    platform: "TikTok",
    tiktok_posting_mode: postingMode,
    publish_id: publishId,
    status: tiktokStatusValue(publishStatus) || "submitted_for_processing",
    execution_status: postingMode === "upload" ? "draft_uploaded" : "posted",
    publish_status: publishStatus,
    post_url: postingMode === "upload" ? "" : tiktokPostUrl(publishStatus),
    next_action: postingMode === "upload" ? "Open TikTok inbox notification, finish review, publish, then log the public URL." : "Check TikTok status and public URL after processing.",
    raw: init,
  };
}

async function postYouTube(payload, env) {
  requireEnv(env, ["GOOGLE_CLIENT_ID", "YOUTUBE_REFRESH_TOKEN"], "YouTube posting");
  const url = videoUrl(payload, env);
  if (!url || !isHttpUrl(url)) {
    throw new Error("YouTube posting from the website needs a public clipUrl video URL");
  }

  const token = await googleAccessToken(env);

  const media = await fetch(url);
  if (!media.ok) throw new Error(`Unable to fetch YouTube media URL (${media.status})`);
  const videoBytes = await media.arrayBuffer();
  if (looksLikeGitLfsPointer(videoBytes)) {
    throw new Error("YouTube media URL resolved to a Git LFS pointer, not a playable video. Host the Shorts clip as a public non-LFS asset.");
  }
  const contentType = media.headers.get("content-type") || guessVideoType(url);

  const title = text(payload.title) || text(payload.text) || "Lily Roo upload";
  const description = youtubeDescription(payload);
  const init = await fetch(YOUTUBE_UPLOAD_INIT_URL, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json; charset=UTF-8",
      "X-Upload-Content-Length": String(videoBytes.byteLength),
      "X-Upload-Content-Type": contentType,
    },
    body: JSON.stringify({
      snippet: {
        title: title.slice(0, 100),
        description: description.slice(0, 5000),
        categoryId: "10",
        tags: youtubeTags(payload),
      },
      status: {
        privacyStatus: text(payload.desiredPrivacy) || env.YOUTUBE_PRIVACY_STATUS || "public",
        selfDeclaredMadeForKids: false,
      },
    }),
  });
  if (!init.ok) throw new Error(`YouTube upload init failed (${init.status}): ${await safeText(init)}`);
  const uploadUrl = init.headers.get("Location");
  if (!uploadUrl) throw new Error("YouTube resumable upload URL missing");

  const upload = await fetch(uploadUrl, {
    method: "PUT",
    headers: {
      "Content-Type": contentType,
      "Content-Length": String(videoBytes.byteLength),
    },
    body: videoBytes,
  });
  const data = await upload.json().catch(async () => ({ error: await safeText(upload) }));
  if (!upload.ok || !data.id) throw new Error(`YouTube upload failed (${upload.status}): ${JSON.stringify(data)}`);

  return { ok: true, platform: "YouTube", video_id: data.id, video_url: `https://youtu.be/${data.id}`, raw: data };
}

async function postX(payload, env) {
  const mediaIds = await xMediaIds(payload, env);
  const data = await createXPost(text(payload.text), env, mediaIds);
  const tweetId = data?.data?.id || "";
  if (!tweetId) throw new Error(`X create post did not return an id: ${JSON.stringify(data)}`);

  let replyId = "";
  if (payload.replyText) {
    const reply = await createXPost(text(payload.replyText), env, [], tweetId);
    replyId = reply?.data?.id || "";
  }

  return {
    ok: true,
    platform: "X",
    tweet_id: tweetId,
    tweet_url: `https://x.com/i/web/status/${tweetId}`,
    reply_id: replyId,
  };
}

async function xMediaIds(payload, env) {
  const explicit = Array.isArray(payload.mediaIds) ? payload.mediaIds : [];
  if (explicit.length) return explicit.map(String);

  const map = parseJson(env.X_MEDIA_MAP_JSON || "{}");
  const mediaKey = text(payload.mediaKey);
  if (!mediaKey) return [];
  const mapped = mediaKey ? map[mediaKey] : "";
  if (mapped) return Array.isArray(mapped) ? mapped.map(String) : String(mapped).split(",").map((item) => item.trim()).filter(Boolean);

  const url = mediaUrl(payload, env);
  if (!url || !isImageUrl(url)) return [];

  requireOAuth1(env, "X image upload");
  const image = await fetch(url);
  if (!image.ok) throw new Error(`Unable to fetch X image URL (${image.status})`);
  const blob = await image.blob();
  const form = new FormData();
  form.append("media", new File([blob], filenameFromUrl(url), { type: blob.type || guessImageType(url) }));
  const upload = await fetch(X_MEDIA_UPLOAD_URL, {
    method: "POST",
    headers: {
      Authorization: await oauth1Header("POST", X_MEDIA_UPLOAD_URL, env),
    },
    body: form,
  });
  const data = await upload.json().catch(async () => ({ error: await safeText(upload) }));
  if (!upload.ok) throw new Error(`X media upload failed (${upload.status}): ${JSON.stringify(data)}`);
  const mediaId = data.media_id_string || data.media_id;
  if (!mediaId) throw new Error(`X media upload did not return a media id: ${JSON.stringify(data)}`);
  return [String(mediaId)];
}

async function createXPost(message, env, mediaIds = [], replyTo = "") {
  const payload = { text: message };
  if (mediaIds.length) payload.media = { media_ids: mediaIds };
  if (replyTo) payload.reply = { in_reply_to_tweet_id: replyTo };
  const headers = { "Content-Type": "application/json; charset=UTF-8" };
  if (env.X_USER_ACCESS_TOKEN) headers.Authorization = `Bearer ${env.X_USER_ACCESS_TOKEN}`;
  else headers.Authorization = await oauth1Header("POST", X_CREATE_POST_URL, env);

  const response = await fetch(X_CREATE_POST_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(async () => ({ error: await safeText(response) }));
  if (!response.ok) throw new Error(`X create post failed (${response.status}): ${JSON.stringify(data)}`);
  return data;
}

async function oauth1Header(method, url, env) {
  requireOAuth1(env, "X OAuth 1.0a posting");
  const params = {
    oauth_consumer_key: env.X_API_KEY,
    oauth_nonce: crypto.randomUUID().replaceAll("-", ""),
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: String(Math.floor(Date.now() / 1000)),
    oauth_token: env.X_ACCESS_TOKEN,
    oauth_version: "1.0",
  };
  const encoded = Object.entries(params)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => `${oauthEncode(key)}=${oauthEncode(value)}`)
    .join("&");
  const baseString = [method.toUpperCase(), oauthEncode(url), oauthEncode(encoded)].join("&");
  const key = `${oauthEncode(env.X_API_SECRET)}&${oauthEncode(env.X_ACCESS_TOKEN_SECRET)}`;
  const cryptoKey = await crypto.subtle.importKey("raw", utf8(key), { name: "HMAC", hash: "SHA-1" }, false, ["sign"]);
  const signature = await crypto.subtle.sign("HMAC", cryptoKey, utf8(baseString));
  params.oauth_signature = base64(signature);
  return "OAuth " + Object.entries(params)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([keyName, value]) => `${oauthEncode(keyName)}="${oauthEncode(value)}"`)
    .join(", ");
}

async function formPost(url, params) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8" },
    body: new URLSearchParams(params),
  });
  const data = await response.json().catch(async () => ({ error: await safeText(response) }));
  if (!response.ok) {
    const error = new Error(`API request failed (${response.status}): ${JSON.stringify(data)}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

async function googleAccessToken(env) {
  const refreshParams = {
    client_id: env.GOOGLE_CLIENT_ID,
    refresh_token: env.YOUTUBE_REFRESH_TOKEN,
    grant_type: "refresh_token",
  };
  if (text(env.GOOGLE_CLIENT_SECRET)) refreshParams.client_secret = env.GOOGLE_CLIENT_SECRET;

  const tokenData = await formPost(GOOGLE_TOKEN_URL, refreshParams);
  const token = tokenData.access_token;
  if (!token) throw new Error(`Unable to refresh YouTube access token: ${JSON.stringify(tokenData)}`);
  return token;
}

async function jsonPost(url, payload, headers = {}) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json; charset=UTF-8", ...headers },
    body: JSON.stringify(payload),
  });
  const data = await response.json().catch(async () => ({ error: await safeText(response) }));
  if (!response.ok) {
    const error = new Error(`API request failed (${response.status}): ${JSON.stringify(data)}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

async function jsonGet(url, params = {}) {
  return jsonGetWithHeaders(url, params);
}

async function jsonGetWithHeaders(url, params = {}, headers = {}) {
  const endpoint = new URL(url);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) endpoint.searchParams.set(key, value);
  }
  const response = await fetch(endpoint.toString(), { headers });
  const data = await response.json().catch(async () => ({ error: await safeText(response) }));
  if (!response.ok) {
    const error = new Error(`API request failed (${response.status}): ${JSON.stringify(data)}`);
    error.status = response.status;
    error.data = data;
    throw error;
  }
  return data;
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function corsHeaders(request, env) {
  const origin = request.headers.get("Origin") || "";
  const allowed = allowedOrigins(env);
  const allowAny = allowed.includes("*");
  const responseOrigin = allowAny
    ? "*"
    : (origin && isAllowedOriginValue(origin, allowed) ? origin : (allowed[0] || origin || "*"));
  return {
    "Access-Control-Allow-Origin": responseOrigin,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Lilyroo-Admin-Password",
    "Vary": "Origin",
  };
}

function isAllowedOrigin(request, env) {
  const origin = request.headers.get("Origin");
  const allowed = allowedOrigins(env);
  return !origin || isAllowedOriginValue(origin, allowed);
}

function allowedOrigins(env) {
  return text(env.ALLOWED_ORIGIN).split(",").map((origin) => origin.trim()).filter(Boolean);
}

function isAllowedOriginValue(origin, allowed) {
  return allowed.length === 0 || allowed.includes("*") || allowed.includes(origin);
}

async function authorizationError(request, env) {
  if (await adminPasswordMatches(request, env)) return null;

  const header = request.headers.get("Authorization") || "";
  if (env.EXECUTOR_BEARER_TOKEN && await bearerMatches(header, env.EXECUTOR_BEARER_TOKEN)) return null;

  if (!env.ADMIN_PASSWORD && !env.EXECUTOR_BEARER_TOKEN) {
    return { status: 500, message: "Social executor is missing ADMIN_PASSWORD or EXECUTOR_BEARER_TOKEN" };
  }
  return { status: 401, message: "Unauthorized" };
}

async function adminPasswordMatches(request, env) {
  const expected = text(env.ADMIN_PASSWORD);
  if (!expected) return false;
  const actual = text(request.headers.get("X-Lilyroo-Admin-Password"));
  if (!actual) return false;
  const actualBytes = utf8(actual);
  const expectedBytes = utf8(expected);
  if (actualBytes.byteLength !== expectedBytes.byteLength) return false;
  return timingSafeEqual(actualBytes, expectedBytes);
}

async function bearerMatches(header, expected) {
  if (!header.startsWith("Bearer ")) return false;
  const actual = header.slice("Bearer ".length);
  const actualBytes = utf8(actual);
  const expectedBytes = utf8(expected);
  if (actualBytes.byteLength !== expectedBytes.byteLength) return false;
  return timingSafeEqual(actualBytes, expectedBytes);
}

function jsonResponse(payload, status, request, env) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...corsHeaders(request, env),
    },
  });
}

function requireEnv(env, names, label) {
  const missing = names.filter((name) => !env[name]);
  if (missing.length) throw new Error(`${label} needs Worker secrets/vars: ${missing.join(", ")}`);
}

function requireOAuth1(env, label) {
  requireEnv(env, ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"], label);
}

async function readiness(env) {
  const xOAuth1 = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"];
  const xOAuth1Present = xOAuth1.every((name) => Boolean(env[name]));
  const xTextPostingReady = Boolean(env.X_USER_ACCESS_TOKEN) || xOAuth1Present;
  const youtubeRequired = ["GOOGLE_CLIENT_ID", "YOUTUBE_REFRESH_TOKEN"];
  const youtubeMissing = youtubeRequired.filter((name) => !env[name]);
  const igToken = instagramAccessToken(env);
  const instagramUsesLoginApi = isInstagramLoginToken(igToken);
  const instagramAccount = igToken
    ? await instagramAccountValidation(env, igToken)
    : { ok: false, reason: "instagram_credentials_missing" };

  return {
    ok: true,
    admin_password_auth: Boolean(env.ADMIN_PASSWORD),
    execute_auth: Boolean(env.EXECUTOR_BEARER_TOKEN),
    scheduler: {
      enabled: Boolean(executionStore(env)),
      queue_url: text(env.SOCIAL_QUEUE_URL) || DEFAULT_QUEUE_URL,
      max_attempts: MAX_SCHEDULE_ATTEMPTS,
    },
    platforms: {
      x: {
        text_posting_ready: xTextPostingReady,
        oauth2_user_token_present: Boolean(env.X_USER_ACCESS_TOKEN),
        oauth1_complete: xOAuth1Present,
        media_map_present: Boolean(env.X_MEDIA_MAP_JSON),
      },
      facebook: {
        ready: Boolean(env.META_LONG_LIVED_TOKEN && env.FB_PAGE_ID),
      },
      instagram: {
        ready: Boolean(igToken && instagramAccount.ok),
        api: instagramUsesLoginApi ? "instagram-login" : "facebook-login",
        account_id_source: env.IG_BUSINESS_ACCOUNT_ID ? "IG_BUSINESS_ACCOUNT_ID" : (instagramUsesLoginApi ? "me" : (env.FB_PAGE_ID ? "FB_PAGE_ID" : "")),
        account_resolved: Boolean(instagramAccount.ok),
        account_resolution_reason: instagramAccount.ok ? "" : instagramAccount.reason,
      },
      tiktok: {
        ready: tiktokCredentialsReady(env),
        posting_mode: tiktokPostingMode({}, env),
        upload_ready: tiktokCredentialsReady(env),
        direct_public_ready: tiktokCredentialsReady(env) && env.TIKTOK_PUBLIC_POSTING_APPROVED === "true",
        access_token_present: Boolean(env.TIKTOK_ACCESS_TOKEN),
        refresh_config_present: Boolean(env.TIKTOK_CLIENT_KEY && env.TIKTOK_CLIENT_SECRET && env.TIKTOK_REFRESH_TOKEN),
        missing_secrets: tiktokMissingCredentials(env),
        public_posting_approved: env.TIKTOK_PUBLIC_POSTING_APPROVED === "true",
        default_privacy: text(env.TIKTOK_DEFAULT_PRIVACY) || "PUBLIC_TO_EVERYONE",
        brand_content_toggle: boolish(env.TIKTOK_BRAND_CONTENT, false),
        brand_organic_toggle: boolish(env.TIKTOK_BRAND_ORGANIC, true),
        aigc_label_enabled: env.TIKTOK_IS_AIGC !== "false",
      },
      youtube: {
        ready: youtubeMissing.length === 0,
        missing_secrets: youtubeMissing,
        client_secret_present: Boolean(env.GOOGLE_CLIENT_SECRET),
        media_map_present: Boolean(env.SOCIAL_MEDIA_MAP_JSON),
        privacy_status: text(env.YOUTUBE_PRIVACY_STATUS) || "public",
      },
    },
  };
}

function mediaUrl(payload, env = {}) {
  const keyed = mediaUrlFromMap(payload, env);
  return keyed || text(payload.clipUrl) || text(payload.imageryUrl) || text(payload.mediaUrl);
}

function videoUrl(payload, env = {}) {
  const keyed = mediaUrlFromMap(payload, env);
  return keyed || text(payload.clipUrl) || text(payload.mediaUrl);
}

function mediaUrlFromMap(payload, env = {}) {
  const key = text(payload.mediaKey);
  if (!key) return "";
  const map = parseJson(env.SOCIAL_MEDIA_MAP_JSON || "{}");
  const mapped = map[key];
  return Array.isArray(mapped) ? text(mapped[0]) : text(mapped);
}

function text(value) {
  return String(value ?? "").trim();
}

function boolish(value, fallback = false) {
  const clean = text(value).toLowerCase();
  if (!clean) return fallback;
  return ["1", "true", "yes", "on"].includes(clean);
}

function isHttpUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

function isVideoUrl(value) {
  return /\.(mp4|mov|webm)(\?|$)/i.test(value);
}

function isImageUrl(value) {
  return /\.(png|jpe?g|gif|webp)(\?|$)/i.test(value);
}

function filenameFromUrl(value) {
  try {
    return new URL(value).pathname.split("/").pop() || "media";
  } catch {
    return "media";
  }
}

function guessVideoType(value) {
  if (/\.mov(\?|$)/i.test(value)) return "video/quicktime";
  if (/\.webm(\?|$)/i.test(value)) return "video/webm";
  return "video/mp4";
}

function guessImageType(value) {
  if (/\.png(\?|$)/i.test(value)) return "image/png";
  if (/\.gif(\?|$)/i.test(value)) return "image/gif";
  if (/\.webp(\?|$)/i.test(value)) return "image/webp";
  return "image/jpeg";
}

function parseJson(value) {
  try {
    return JSON.parse(value);
  } catch {
    return {};
  }
}

function truthy(value) {
  const normalized = text(value).toLowerCase();
  return ["1", "true", "yes", "y", "approved"].includes(normalized);
}

function appendCta(message, cta) {
  const cleanMessage = text(message);
  const cleanCta = text(cta);
  if (!cleanCta || cleanMessage.includes(cleanCta)) return cleanMessage;
  return `${cleanMessage}\n\n${cleanCta}`;
}

async function tiktokCreatorInfo(env) {
  return jsonPost(TIKTOK_CREATOR_INFO_URL, {}, {
    Authorization: await tiktokAuthorization(env),
  });
}

async function tiktokPublishStatus(env, publishId) {
  return jsonPost(TIKTOK_STATUS_URL, { publish_id: publishId }, {
    Authorization: await tiktokAuthorization(env),
  });
}

async function tiktokAuthorization(env) {
  return `Bearer ${await tiktokAccessToken(env)}`;
}

async function tiktokAccessToken(env) {
  if (env.TIKTOK_ACCESS_TOKEN) return env.TIKTOK_ACCESS_TOKEN;
  requireEnv(env, ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"], "TikTok OAuth refresh");
  const data = await formPost(TIKTOK_OAUTH_TOKEN_URL, {
    client_key: env.TIKTOK_CLIENT_KEY,
    client_secret: env.TIKTOK_CLIENT_SECRET,
    grant_type: "refresh_token",
    refresh_token: env.TIKTOK_REFRESH_TOKEN,
  });
  const token = text(data.access_token);
  if (!token) throw new Error(`TikTok refresh did not return an access token: ${JSON.stringify(data)}`);
  return token;
}

function tiktokCredentialsReady(env) {
  return Boolean(env.TIKTOK_ACCESS_TOKEN)
    || Boolean(env.TIKTOK_CLIENT_KEY && env.TIKTOK_CLIENT_SECRET && env.TIKTOK_REFRESH_TOKEN);
}

function tiktokMissingCredentials(env) {
  if (env.TIKTOK_ACCESS_TOKEN) return [];
  return ["TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"].filter((name) => !env[name]);
}

function tiktokPostingMode(payload, env) {
  const mode = text(payload.tiktokPostingMode || payload.tiktok_posting_mode || env.TIKTOK_POSTING_MODE || "upload").toLowerCase();
  return mode === "upload" || mode === "draft" || mode === "inbox" ? "upload" : "direct";
}

function tiktokDesiredPrivacy(payload, env) {
  return text(payload.desiredPrivacy) || text(env.TIKTOK_DEFAULT_PRIVACY) || "PUBLIC_TO_EVERYONE";
}

function tiktokDisclosure(payload, env) {
  return {
    brandContent: boolish(payload.brandContent ?? env.TIKTOK_BRAND_CONTENT, false),
    brandOrganic: boolish(payload.brandOrganic ?? env.TIKTOK_BRAND_ORGANIC, true),
  };
}

function tiktokStatusValue(statusPayload) {
  return text(statusPayload?.data?.status);
}

function tiktokPostUrl(statusPayload) {
  const ids = statusPayload?.data?.publicaly_available_post_id || [];
  const postId = Array.isArray(ids) ? text(ids[0]) : text(ids);
  return postId ? `https://www.tiktok.com/@${text(statusPayload?.data?.creator_username) || "lilyroo930"}/video/${postId}` : "";
}

function postUrlFromResult(result) {
  return text(result.post_url || result.tweet_url || result.video_url || result.media_url);
}

function externalIdFromResult(result) {
  return text(result.post_id || result.tweet_id || result.video_id || result.media_id || result.publish_id || result.creation_id);
}

function executionStatusFromResult(result) {
  return text(result.execution_status) || "posted";
}

function isTerminalExecutionStatus(status) {
  return ["posted", "draft_uploaded"].includes(text(status));
}

function numberOrNull(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

function latestInsightValue(payload) {
  const metric = Array.isArray(payload?.data) ? payload.data[0] : null;
  const values = Array.isArray(metric?.values) ? metric.values : [];
  for (const item of values.slice().reverse()) {
    const n = numberOrNull(item?.value);
    if (n !== null) return n;
  }
  return null;
}

function spotifyAlbumId(value) {
  try {
    const url = new URL(value);
    const parts = url.pathname.split("/").filter(Boolean);
    return parts[0] === "album" && parts[1] ? parts[1] : "";
  } catch {
    return "";
  }
}

function metricErrorMessage(error) {
  const apiMessage = error?.data?.error?.message || error?.data?.message || error?.message;
  return text(apiMessage) || "Metric request failed";
}

function lastNDaysPeriod(days) {
  const end = new Date();
  end.setUTCDate(end.getUTCDate() - 1);
  const start = new Date(end);
  start.setUTCDate(start.getUTCDate() - (days - 1));
  return {
    startDate: isoDate(start),
    endDate: isoDate(end),
  };
}

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function youtubeDescription(payload) {
  const base = text(payload.description) || text(payload.replyText) || text(payload.text);
  const platform = text(payload.platform).toLowerCase();
  if (!platform.includes("shorts") || /(^|\s)#shorts(\s|$)/i.test(base)) return base;
  return `${base}\n\n#Shorts`;
}

function youtubeTags(payload) {
  const platform = text(payload.platform).toLowerCase();
  const tags = ["Lily Roo"];
  const song = text(payload.song);
  if (song) tags.push(song);
  if (platform.includes("shorts")) tags.push("Shorts");
  return [...new Set(tags)].slice(0, 10);
}

function looksLikeGitLfsPointer(bytes) {
  const sample = new TextDecoder().decode(bytes.slice(0, Math.min(bytes.byteLength, 256)));
  return sample.startsWith("version https://git-lfs.github.com/spec/v1");
}

function timingSafeEqual(left, right) {
  if (left.byteLength !== right.byteLength) return false;
  let diff = 0;
  for (let i = 0; i < left.byteLength; i += 1) diff |= left[i] ^ right[i];
  return diff === 0;
}

function metaGraphVersion(env) {
  return text(env.META_GRAPH_VERSION) || DEFAULT_GRAPH_VERSION;
}

function metaBase(env) {
  return `https://graph.facebook.com/${metaGraphVersion(env)}`;
}

async function safeText(response) {
  try {
    return await response.text();
  } catch {
    return "";
  }
}

function oauthEncode(value) {
  return encodeURIComponent(String(value))
    .replace(/[!*()']/g, (char) => `%${char.charCodeAt(0).toString(16).toUpperCase()}`);
}

function utf8(value) {
  return new TextEncoder().encode(value);
}

function base64(buffer) {
  let binary = "";
  for (const byte of new Uint8Array(buffer)) binary += String.fromCharCode(byte);
  return btoa(binary);
}
