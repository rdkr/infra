# infra

## core

* terraform on terraform cloud
    * dns on cloudflare
    * k8s cluster on digitalocean

## csgo

* base
    * packer to build LGSM csgo base server on digitalocean
* other files with config for servers built on top of base

## hermes

12 factor app (work in progress) to manage csgo servers

### v1
* start / stop csgo servers on digital oceaan

### v2
* added control over discord commands

### v3
* added deployment to k8s with prometheus metrics exposed

### v4 (todo)
* make stateless / scaleable
