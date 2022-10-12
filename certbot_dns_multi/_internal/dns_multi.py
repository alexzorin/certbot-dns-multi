import json
import logging
from typing import Any, Callable, List, Mapping

from acme import challenges
from certbot import achallenges, errors
from certbot.plugins import dns_common
from josepy import encode_b64jose
from lego_bridge import cmd

logger = logging.getLogger(__name__)


class Authenticator(dns_common.DNSAuthenticator):
    description = "Obtain certificate using any of lego's supported DNS providers"

    _env_vars_to_unset: List[str] = []
    _do_cleanup = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(
        cls, add: Callable[..., None], default_propagation_seconds: int = 10
    ) -> None:
        super().add_parser_arguments(add, default_propagation_seconds)
        add("credentials", help="MultiDNS credentials INI file.")

    def more_info(self) -> str:
        return (
            "This plugin performs DNS challenges using one of the DNS providers "
            "available via lego"
        )

    def _setup_credentials(self) -> None:
        self.credentials = self._configure_credentials(
            "credentials",
            "MultiDNS credentials INI file",
            {"provider": "Name of the DNS provider to use"},
        )

        lego_environ = {
            k: self.credentials.confobj.get(k)
            for k in self.credentials.confobj
            if k != "dns_multi_provider"
        }

        provider = self.credentials.conf("provider")
        logger.debug(
            "Configuring lego for provider %s with %d options",
            provider,
            len(lego_environ),
        )
        LegoClient.configure(provider, lego_environ)

    # The reasons we override perform rather than _perform are:
    # - Lego wants access to the challenge token, which is not exposed
    #   via _perform.
    # - We don't want to sleep, this is handled via lego.
    def perform(
        self, achalls: List[achallenges.AnnotatedChallenge]
    ) -> List[challenges.ChallengeResponse]:
        self._setup_credentials()
        self._do_cleanup = True

        responses = []
        for achall in achalls:
            domain = achall.validation_domain_name(achall.domain)
            key_authz = achall.validation(achall.account_key)
            try:
                logger.debug(
                    "Asking lego to create record %s for domain %s", key_authz, domain
                )
                LegoClient.present(
                    domain,
                    encode_b64jose(achall.token),
                    key_authz,
                )
            except Exception as e:
                logger.warning(f"Perform of {domain} failed: {e}")
                logger.debug("Perform error was", exc_info=True)

            responses.append(achall.response(achall.account_key))

        return responses

    def cleanup(self, achalls: List[achallenges.AnnotatedChallenge]) -> None:
        if not self._do_cleanup:
            return

        for achall in achalls:
            domain: str = achall.validation_domain_name(achall.domain)
            key_authz = achall.validation(achall.account_key)
            try:
                logger.debug(
                    "Asking lego to clean up record %s for domain %s", key_authz, domain
                )
                LegoClient.cleanup(
                    domain,
                    encode_b64jose(achall.token),
                    key_authz,
                )
            except Exception as e:
                logger.warning(f"Cleanup of {domain} failed: {e}")
                logger.debug("Cleanup error was", exc_info=True)

    def auth_hint(self, failed_achalls: List[achallenges.AnnotatedChallenge]) -> str:
        """See certbot.plugins.common.Plugin.auth_hint."""
        provider = self.credentials.conf("provider")
        return (
            "The Certificate Authority failed to verify the DNS TXT records created by "
            f"Lego. Ensure the above domains are hosted by {provider.capitalize()} and "
            f"check https://go-acme.github.io/lego/dns/{provider} for further details "
            "on configuring this provider."
        )

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        ...

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        ...


class LegoClient:
    @staticmethod
    def configure(provider: str, credentials: Mapping[str, str]):
        LegoClient._raise_for_response(
            cmd(
                json.dumps(
                    {
                        "action": "configure",
                        "provider": provider,
                        "credentials": credentials,
                    }
                )
            )
        )

    @staticmethod
    def present(domain: str, token: str, key_authorization: str):
        LegoClient._raise_for_response(
            cmd(
                json.dumps(
                    {
                        "action": "perform",
                        "domain": domain,
                        "token": token,
                        "key_authorization": key_authorization,
                    }
                )
            )
        )

    @staticmethod
    def cleanup(domain: str, token: str, key_authorization: str):
        LegoClient._raise_for_response(
            cmd(
                json.dumps(
                    {
                        "action": "cleanup",
                        "domain": domain,
                        "token": token,
                        "key_authorization": key_authorization,
                    }
                )
            )
        )

    @staticmethod
    def _raise_for_response(resp: str) -> None:
        resp = json.loads(resp)
        if not resp["success"]:
            raise errors.PluginError(resp["error"])
