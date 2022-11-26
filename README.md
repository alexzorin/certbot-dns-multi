# certbot-dns-multi

[![certbot-dns-multi](https://snapcraft.io/certbot-dns-multi/badge.svg)](https://snapcraft.io/certbot-dns-multi) ![build status](https://github.com/alexzorin/certbot-dns-multi/actions/workflows/build-and-publish.yml/badge.svg)  ![snap test status](https://github.com/alexzorin/certbot-dns-multi/actions/workflows/test-snap.yml/badge.svg)

DNS plugin for [Certbot](https://certbot.eff.org/) which integrates with the 100+ DNS providers from the [`lego` ACME client](https://github.com/go-acme/lego/).

At the last check, the supported providers are:

> Akamai EdgeDNS, Alibaba Cloud DNS, all-inkl, Amazon Lightsail, Amazon Route 53, ArvanCloud, Aurora DNS, Autodns, Azure, Bindman, Bluecat, Checkdomain, Civo, CloudDNS, Cloudflare, ClouDNS, CloudXNS, ConoHa, Constellix, deSEC.io, Designate DNSaaS for Openstack, Digital Ocean, DNS Made Easy, DNSimple, DNSPod (deprecated), Domain Offensive (do.de), Domeneshop, DreamHost, Duck DNS, Dyn, Dynu, EasyDNS, Epik, Exoscale, External program, freemyip.com, G-Core Labs, Gandi, Gandi Live DNS (v5), Glesys, Go Daddy, Google Cloud, Hetzner, Hosting.de, Hosttech, HTTP request, Hurricane Electric DNS, HyperOne, IBM Cloud (SoftLayer), IIJ DNS Platform Service, Infoblox, Infomaniak, Internet Initiative Japan, Internet.bs, INWX, Ionos, iwantmyname, Joker, Joohoi's ACME-DNS, Linode (v4), Liquid Web, Loopia, LuaDNS, Manual, MyDNS.jp, MythicBeasts, Name.com, Namecheap, Namesilo, NearlyFreeSpeech.NET, Netcup, Netlify, Nicmanager, NIFCloud, Njalla, NS1, Open Telekom Cloud, Oracle Cloud, OVH, Porkbun, PowerDNS, Rackspace, reg.ru, RFC2136, RimuHosting, Sakura Cloud, Scaleway, Selectel, Servercow, Simply.com, Sonic, Stackpath, Tencent Cloud DNS, TransIP, UKFast SafeDNS, Variomedia, VegaDNS, Vercel, Versio.[nl|eu|uk], VinylDNS, VK Cloud, Vscale, Vultr, WEDOS, Yandex Cloud, Yandex PDD, Zone.ee, Zonomi.


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
    CLOUDFLARE_DNS_API_TOKEN=1234567890abcdefghijklmnopqrstuvwxyz
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
