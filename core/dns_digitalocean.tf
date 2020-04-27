resource "digitalocean_domain" "dm_rdkr_uk" {
  name = "dm.rdkr.uk"
}

resource "cloudflare_record" "dm_rdkr_uk_1" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "dm"
  value   = "ns1.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "cloudflare_record" "dm_rdkr_uk_2" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "dm"
  value   = "ns2.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "cloudflare_record" "dm_rdkr_uk_3" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "dm"
  value   = "ns3.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "digitalocean_domain" "pug_rdkr_uk" {
  name = "pug.rdkr.uk"
}

resource "cloudflare_record" "pug_rdkr_uk_1" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "pug"
  value   = "ns1.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "cloudflare_record" "pug_rdkr_uk_2" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "pug"
  value   = "ns2.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "digitalocean_domain" "k8s_rdkr_uk" {
  name = "k8s.rdkr.uk"
}

resource "cloudflare_record" "pug_rdkr_uk_3" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "pug"
  value   = "ns3.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "cloudflare_record" "k8s_rdkr_uk_1" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "k8s"
  value   = "ns1.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "cloudflare_record" "k8s_rdkr_uk_2" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "k8s"
  value   = "ns2.digitalocean.com"
  type    = "NS"
  ttl     = 1
}

resource "cloudflare_record" "k8s_rdkr_uk_3" {
  zone_id = "f6d706e06f5fdb858d0c78bafb1194ec"
  name    = "k8s"
  value   = "ns3.digitalocean.com"
  type    = "NS"
  ttl     = 1
}
