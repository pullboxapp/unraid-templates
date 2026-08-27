# Pullbox for Unraid Community Applications

This repository contains the official Unraid Community Applications templates
for [Pullbox](https://pullbox.app) and its optional production direct-download
providers.

## Available applications

| Application | Purpose | Image |
| --- | --- | --- |
| Pullbox | Comic library management, acquisition, imports, and reading | `ghcr.io/pullboxapp/pullbox:latest` |
| Pullbox Provider - GetComics | GetComics discovery and supported artifact-route resolution | `ghcr.io/pullboxapp/pullbox-provider-getcomics:latest` |
| Pullbox Provider - Anna's Archive | Anna's Archive discovery and member fast-download resolution | `ghcr.io/pullboxapp/pullbox-provider-annas-archive:latest` |

The provider containers are optional and independently versioned. The synthetic
provider image in the provider source repository is a protocol test tool, not a
production application, and is intentionally not published here.

## Install Pullbox

Once this repository is accepted into Community Applications:

1. Open **Apps** in Unraid and search for **Pullbox**.
2. Review the path mappings and fixed-user permission requirement.
3. Install Pullbox and open its WebUI.
4. Complete the first-run account setup.

Pullbox runs as the fixed non-root UID/GID `65532:65532`; it does not use
`PUID` or `PGID`. Follow the
[NAS and Unraid permissions guide](https://pullbox.app/docs/getting-started/nas-and-unraid-permissions)
before first start.

## Recommended provider network

Keep Pullbox and its providers on the same user-defined private Docker network.
This allows Pullbox to use stable container names and keeps provider API ports
off the LAN.

Create the network once from the Unraid terminal:

```bash
docker network create pullbox
```

Choose `pullbox` as **Network Type** for the Pullbox, GetComics, and Anna's
Archive templates. If Pullbox was already installed, edit its container,
select the `pullbox` network, and apply the change before installing providers.

With the recommended network, leave each provider's optional fallback port
blank and register these endpoints in **Pullbox -> Settings -> Direct
Downloads**:

| Provider | Endpoint |
| --- | --- |
| GetComics | `http://Pullbox-Provider-GetComics:8780` |
| Anna's Archive | `http://Pullbox-Provider-Annas-Archive:8780` |

Select Pullbox's acknowledgement for unencrypted HTTP on a trusted private
network when registering either endpoint.

## Bridge-network fallback

The providers can also work without the dedicated network. Leave the
containers on `bridge`, assign a distinct host port in each provider's optional
**Fallback API Port** field, and register the Unraid server's private LAN
address in Pullbox. For example:

| Provider | Suggested host port | Example endpoint |
| --- | --- | --- |
| GetComics | `8780` | `http://192.168.1.20:8780` |
| Anna's Archive | `8781` | `http://192.168.1.20:8781` |

Replace the example address with the Unraid server's LAN address. Do not use
`localhost`, because that refers to the Pullbox container itself. Do not
port-forward provider API ports to the internet. Public or remote provider
endpoints must use HTTPS.

## Provider tokens and registration

Generate a different bearer token for each provider. From the Unraid terminal:

```bash
openssl rand -hex 32
```

Enter the token in the provider template, then enter the same token when
registering that provider in Pullbox. Provider tokens must contain at least 32
characters. Pullbox stores them encrypted and does not expose them again.

After installing a provider:

1. Open **Settings -> Direct Downloads** in Pullbox.
2. Select **Add Provider**.
3. Enter the private-network or bridge-fallback endpoint.
4. Enter the matching bearer token.
5. Acknowledge private HTTP when using a trusted private address.
6. Test, save, configure, and enable the provider.

Anna's Archive member fast-download credentials are entered later in Pullbox's
provider settings. They are not container environment variables.

## Template contract

The templates preserve the production container contracts:

- Pullbox exposes `8585/tcp` and mounts `/data`, `/comics`, `/downloads`, and
  optional `/imports` paths.
- Provider services expose `8780/tcp` only inside their container network by
  default and require no host volumes.
- Provider services run as UID/GID `65532:65532` with a read-only root
  filesystem, all Linux capabilities dropped, `no-new-privileges`, and a
  bounded `/tmp` tmpfs.
- Every provider receives only its own bearer token. It does not receive
  Pullbox paths, its database, or unrelated credentials.

Keep these templates synchronized with Pullbox's production
[`docker/docker-compose.yml`](https://github.com/pullboxapp/pullbox/blob/main/docker/docker-compose.yml)
and the provider
[deployment contract](https://github.com/pullboxapp/pullbox-direct-providers#deployment-and-registration).

## Validation and submission

Run the local repository contract before submitting changes:

```bash
make validate
```

After changes reach `main`, run **Validate** and **Scan** through the
[Unraid Community Applications submission flow](https://ca.unraid.net/submit).

## Support

- [Documentation](https://pullbox.app/docs/)
- [Direct-download setup](https://pullbox.app/docs/configuration/direct-downloads)
- [GitHub issues](https://github.com/pullboxapp/pullbox/issues)
- [Discord](https://discord.gg/mg6GQkATaA)

Security reports should follow the private reporting instructions in Pullbox's
[`SECURITY.md`](https://github.com/pullboxapp/pullbox/blob/main/SECURITY.md).

## License

The templates in this repository are licensed under GPL-3.0-or-later, matching
Pullbox and the official direct-download providers. See `LICENSE` for details.
