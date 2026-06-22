# Build Caddy with the Cloudflare DNS plugin (needed for the DNS-01 ACME challenge,
# since the origin sits behind Cloudflare's proxy). The stock caddy:2 image lacks it.
FROM caddy:2-builder AS builder
RUN xcaddy build --with github.com/caddy-dns/cloudflare

FROM caddy:2
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
