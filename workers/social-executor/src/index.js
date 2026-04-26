const DEFAULT_GRAPH_VERSION = "v25.0";
const X_CREATE_POST_URL = "https://api.x.com/2/tweets";
const X_MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json";
const TIKTOK_CREATOR_INFO_URL = "https://open.tiktokapis.com/v2/post/publish/creator_info/query/";
const TIKTOK_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/";
const GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token";
const YOUTUBE_UPLOAD_INIT_URL = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status";

export default {
  async fetch(request, env, ctx) {
    try {
      return await handleRequest(request, env, ctx);
    } catch (error) {
      console.error(JSON.stringify({ level: "error", message: error.message, stack: error.stack }));
      return jsonResponse({ ok: false, error: error.message || "Unknown error" }, 500, request, env);
    }
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

    return jsonResponse(readiness(env), 200, request, env);
  }

  if (url.pathname !== "/api/social/execute" || request.method !== "POST") {
    return jsonResponse({ ok: false, error: "Not found" }, 404, request, env);
  }

  const authError = await authorizationError(request, env);
  if (authError) {
    return jsonResponse({ ok: false, error: authError.message }, authError.status, request, env);
  }

  const payload = await request.json();
  const result = await executePost(payload, env);
  return jsonResponse(result, 200, request, env);
}

async function executePost(payload, env) {
  const platform = text(payload.platform).toLowerCase();
  const bodyText = text(payload.text);

  if (!platform) throw new Error("platform is required");
  if (!bodyText) throw new Error("text is required");

  if (payload.dryRun) {
    return {
      ok: true,
      dry_run: true,
      platform: payload.platform,
      post_id: payload.postId || "",
      media_url: mediaUrl(payload, env),
      media_key: payload.mediaKey || "",
    };
  }

  if (platform === "x" || platform.startsWith("x")) return postX(payload, env);
  if (platform.includes("instagram")) return postInstagram(payload, env);
  if (platform.includes("facebook")) return postFacebook(payload, env);
  if (platform.includes("tiktok")) return postTikTok(payload, env);
  if (platform.includes("youtube")) return postYouTube(payload, env);

  throw new Error(`Unsupported platform: ${payload.platform || ""}`);
}

async function postFacebook(payload, env) {
  requireEnv(env, ["META_LONG_LIVED_TOKEN", "FB_PAGE_ID"], "Facebook posting");
  const url = mediaUrl(payload, env);
  const endpoint = url ? `${metaBase(env)}/${env.FB_PAGE_ID}/photos` : `${metaBase(env)}/${env.FB_PAGE_ID}/feed`;
  const params = {
    access_token: env.META_LONG_LIVED_TOKEN,
  };
  if (url) {
    params.url = url;
    params.caption = text(payload.text);
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

async function postTikTok(payload, env) {
  requireEnv(env, ["TIKTOK_ACCESS_TOKEN"], "TikTok posting");
  const url = videoUrl(payload, env);
  if (!url || !isHttpUrl(url)) {
    throw new Error("TikTok posting from the website needs a public clipUrl video URL");
  }

  const creator = await jsonPost(TIKTOK_CREATOR_INFO_URL, {}, {
    Authorization: `Bearer ${env.TIKTOK_ACCESS_TOKEN}`,
  });
  const options = creator?.data?.privacy_level_options || [];
  const privacy = options.includes("SELF_ONLY") ? "SELF_ONLY" : (options[0] || "SELF_ONLY");

  const init = await jsonPost(TIKTOK_INIT_URL, {
    post_info: {
      title: text(payload.text),
      privacy_level: privacy,
      disable_comment: false,
      disable_duet: false,
      disable_stitch: false,
      is_aigc: env.TIKTOK_IS_AIGC !== "false",
    },
    source_info: {
      source: "PULL_FROM_URL",
      video_url: url,
    },
  }, {
    Authorization: `Bearer ${env.TIKTOK_ACCESS_TOKEN}`,
  });

  const publishId = init?.data?.publish_id || "";
  if (!publishId) throw new Error(`TikTok init failed: ${JSON.stringify(init)}`);
  return { ok: true, platform: "TikTok", publish_id: publishId, status: "submitted_for_processing", raw: init };
}

async function postYouTube(payload, env) {
  requireEnv(env, ["GOOGLE_CLIENT_ID", "YOUTUBE_REFRESH_TOKEN"], "YouTube posting");
  const url = videoUrl(payload, env);
  if (!url || !isHttpUrl(url)) {
    throw new Error("YouTube posting from the website needs a public clipUrl video URL");
  }

  const refreshParams = {
    client_id: env.GOOGLE_CLIENT_ID,
    refresh_token: env.YOUTUBE_REFRESH_TOKEN,
    grant_type: "refresh_token",
  };
  if (text(env.GOOGLE_CLIENT_SECRET)) refreshParams.client_secret = env.GOOGLE_CLIENT_SECRET;

  const tokenData = await formPost(GOOGLE_TOKEN_URL, refreshParams);
  const token = tokenData.access_token;
  if (!token) throw new Error(`Unable to refresh YouTube access token: ${JSON.stringify(tokenData)}`);

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
        privacyStatus: env.YOUTUBE_PRIVACY_STATUS || "public",
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
  const endpoint = new URL(url);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null) endpoint.searchParams.set(key, value);
  }
  const response = await fetch(endpoint.toString());
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
  const allowed = env.ALLOWED_ORIGIN || origin || "*";
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Lilyroo-Admin-Password",
    "Vary": "Origin",
  };
}

function isAllowedOrigin(request, env) {
  const allowed = env.ALLOWED_ORIGIN;
  const origin = request.headers.get("Origin");
  return !allowed || !origin || origin === allowed;
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

function readiness(env) {
  const xOAuth1 = ["X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"];
  const xOAuth1Present = xOAuth1.every((name) => Boolean(env[name]));
  const xTextPostingReady = Boolean(env.X_USER_ACCESS_TOKEN) || xOAuth1Present;
  const youtubeRequired = ["GOOGLE_CLIENT_ID", "YOUTUBE_REFRESH_TOKEN"];
  const youtubeMissing = youtubeRequired.filter((name) => !env[name]);
  const igToken = instagramAccessToken(env);
  const instagramUsesLoginApi = isInstagramLoginToken(igToken);

  return {
    ok: true,
    admin_password_auth: Boolean(env.ADMIN_PASSWORD),
    execute_auth: Boolean(env.EXECUTOR_BEARER_TOKEN),
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
        ready: Boolean(igToken && (instagramUsesLoginApi || env.IG_BUSINESS_ACCOUNT_ID || env.FB_PAGE_ID)),
        api: instagramUsesLoginApi ? "instagram-login" : "facebook-login",
        account_id_source: env.IG_BUSINESS_ACCOUNT_ID ? "IG_BUSINESS_ACCOUNT_ID" : (instagramUsesLoginApi ? "me" : (env.FB_PAGE_ID ? "FB_PAGE_ID" : "")),
      },
      tiktok: {
        ready: Boolean(env.TIKTOK_ACCESS_TOKEN),
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
