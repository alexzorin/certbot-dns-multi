# certbot-dns-multi

DNS plugin for [Certbot](https://certbot.eff.org/) which integrates with the 100+ DNS providers from the [`lego` ACME client](https://github.com/go-acme/lego/).


## Installation

### via `snap`

Using the `certbot` snap is the easiest way to use this plugin. See [here](https://certbot.eff.org/instructions?ws=other&os=snap) for instructions on installing Certbot via `snap`.

```bash
sudo snap install certbot-dns-multi
sudo snap set certbot trust-plugin-with-root=ok
sudo snap connect certbot:plugin certbot-dns-multi
```

### via `pip`

Because `lego` is written in Go, compiling and installing the plugin via `pip` requires you to have [Go 1.19 or newer](https://go.dev/dl) installed on the system. This project does not publish any binary wheels (yet).  For this reason, using the `snap` is recommended.

```bash
pip install certbot-dns-multi
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
    CLOUDFLARE_EMAIL=you@example.com
    CLOUDFLARE_API_KEY=b9841238feb177a84330febba8a83208921177bffe733
    ```

4. Save the file.

5. Try issue a certificate now:

    ```bash
    certbot certonly -a dns-multi \
    --dns-multi-credentials=/etc/letsencrypt/dns-multi.ini \
    -d "*.example.com" \
    --dry-run
    ```

6. 🥳, or if not, ask on [the community forums](https://community.letsencrypt.org/) for help.
