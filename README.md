# certbot-dns-multi

[![certbot-dns-multi](https://snapcraft.io/certbot-dns-multi/badge.svg)](https://snapcraft.io/certbot-dns-multi) ![build status](https://github.com/alexzorin/certbot-dns-multi/actions/workflows/build-and-publish.yml/badge.svg)  ![snap test status](https://github.com/alexzorin/certbot-dns-multi/actions/workflows/test-snap.yml/badge.svg)

DNS plugin for [Certbot](https://certbot.eff.org/) which integrates with the 117+ DNS providers from the [`lego` ACME client](https://github.com/go-acme/lego/).

At the last check, the supported providers are:

> Akamai EdgeDNS, Alibaba Cloud DNS, all-inkl, Amazon Lightsail, Amazon Route 53, ArvanCloud, Aurora DNS, Autodns, Azure (deprecated), Azure DNS, Bindman, Bluecat, Brandit, Bunny, Checkdomain, Civo, Cloud.ru, CloudDNS, Cloudflare, ClouDNS, CloudXNS, ConoHa, Constellix, CPanel/WHM, Derak Cloud, deSEC.io, Designate DNSaaS for Openstack, Digital Ocean, DNS Made Easy, dnsHome.de, DNSimple, DNSPod (deprecated), Domain Offensive (do.de), Domeneshop, DreamHost, Duck DNS, Dyn, Dynu, EasyDNS, Efficient IP, Epik, Exoscale, External program, freemyip.com, G-Core, Gandi Live DNS (v5), Gandi, Glesys, Go Daddy, Google Cloud, Google Domains, Hetzner, Hosting.de, Hosttech, HTTP request, http.net, Hurricane Electric DNS, HyperOne, IBM Cloud (SoftLayer), IIJ DNS Platform Service, Infoblox, Infomaniak, Internet Initiative Japan, Internet.bs, INWX, Ionos, IPv64, iwantmyname, Joker, Joohoi's ACME-DNS, Liara, Linode (v4), Liquid Web, Loopia, LuaDNS, Mail-in-a-Box, Manual, Metaname, MyDNS.jp, MythicBeasts, Name.com, Namecheap, Namesilo, NearlyFreeSpeech.NET, Netcup, Netlify, Nicmanager, NIFCloud, Njalla, Nodion, NS1, Open Telekom Cloud, Oracle Cloud, OVH, plesk.com, Porkbun, PowerDNS, Rackspace, RcodeZero, reg.ru, RFC2136, RimuHosting, Sakura Cloud, Scaleway, Selectel, Servercow, Shellrent, Simply.com, Sonic, Stackpath, Tencent Cloud DNS, TransIP, UKFast SafeDNS, Ultradns, Variomedia, VegaDNS, Vercel, Versio.\[nl/eu/uk\], VinylDNS, VK Cloud, Vscale, Vultr, Webnames, Websupport, WEDOS, Yandex 360, Yandex Cloud, Yandex PDD, Zone.ee, Zonomi

## Installation

### via `snap`

Using the `certbot` snap is the easiest way to use this plugin. See [here](https://certbot.eff.org/instructions?ws=other&os=snap) for instructions on installing Certbot via `snap`.

```bash
sudo snap install certbot-dns-multi
sudo snap set certbot trust-plugin-with-root=ok
sudo snap connect certbot:plugin certbot-dns-multi
```

### via `pip`

Compiled wheels [are available](https://pypi.org/project/certbot-dns-multi/#files) for most `x86_64`/`amd64` Linux distributions. On other platforms, `pip` will try to compile the plugin, which requires [Go 1.19 or newer](https://go.dev/dl) to be installed on your server.

| How did you install Certbot?                                                                          | How to install the plugin                             |
|-------------------------------------------------------------------------------------------------------|-------------------------------------------------------|
| From `snap`                                                                                           | Don't use `pip`! Use the snap instructions above.     |
| Using the [official Certbot `pip` instructions](https://certbot.eff.org/instructions?ws=other&os=pip) | `sudo /opt/certbot/bin/pip install certbot-dns-multi` |
| From `apt`, `yum`, `dnf` or any other distro package manager. (Requires Certbot 1.12.0 or newer.)     | `pip install certbot-dns-multi`                       |

### via `docker`

Docker images for `linux/amd64` and `linux/arm64` are available from [`ghcr.io/alexzorin/certbot-dns-multi`](https://ghcr.io/alexzorin/certbot-dns-multi).

e.g.

```bash
docker run --rm -it -v /etc/letsencrypt:/etc/letsencrypt \
ghcr.io/alexzorin/certbot-dns-multi certonly \
-a dns-multi --dns-multi-credentials /etc/letsencrypt/dns-multi.ini \
-d "*.example.com" -d "example.com" --dry-run
```

## Usage

`certbot-dns-multi` is controlled via a credentials file.

1. Head to https://go-acme.github.io/lego/dns/ and find your DNS provider in the list.
In this example, we'll use `cloudflare`.
2. Create `/etc/letsencrypt/dns-multi.ini` and enter the name of your provider, all lowercase, as below:

    ```ini
    dns_multi_provider = cloudflare
    ```

3. Following the instructions on https://go-acme.github.io/lego/dns/cloudflare/, we add the required configuration items:

    ```ini
    dns_multi_provider = cloudflare
    CLOUDFLARE_DNS_API_TOKEN="1234567890abcdefghijklmnopqrstuvwxyz"
    ```

4. Save the file and secure it:

    ```bash
    chmod 0600 /etc/letsencrypt/dns-multi.ini
    ```

5. Try issue a certificate now:

    ```bash
    certbot certonly -a dns-multi \
    --dns-multi-credentials=/etc/letsencrypt/dns-multi.ini \
    -d "*.example.com" \
    --dry-run
    ```

6. 🥳, or if not, ask on [the community forums](https://community.letsencrypt.org/) for help.
