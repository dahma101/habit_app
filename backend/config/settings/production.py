"""Production settings: DEBUG off, hosts/CORS/CSRF locked down, behind Caddy + Cloudflare."""

from .base import *  # noqa: F401, F403
from .base import MIDDLEWARE, BASE_DIR, env

DEBUG = False
# ALLOWED_HOSTS is read from env in base.py; supply it via backend/.env.prod.

# Trust the X-Forwarded-Proto header set by Caddy so Django knows requests are HTTPS.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# Static files served by WhiteNoise (Django admin, DRF browsable API, swagger sidecar).
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
}
# Insert WhiteNoise directly after SecurityMiddleware.
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# Lock CORS down (only relevant if the SPA ever calls the api. subdomain directly;
# normal usage is same-origin through the frontend nginx /api proxy).
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["https://meinhabit.de", "https://www.meinhabit.de"],
)
CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "https://meinhabit.de",
        "https://www.meinhabit.de",
        "https://api.meinhabit.de",
    ],
)

# HTTPS hardening (TLS is terminated at Caddy/Cloudflare; we emit secure cookies + HSTS).
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
