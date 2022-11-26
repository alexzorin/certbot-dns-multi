import json
import logging
from time import sleep
from typing import Any, Callable, List, Mapping

from acme import challenges
from certbot import achallenges, errors
from certbot.display import util as display_util
from certbot.plugins import dns_common
from josepy import encode_b64jose
from lego_bridge import cmd

logger = logging.getLogger(__name__)


class backwards_compatible_authenticator(object):
    """Provides support for both Certbot <1.19.0 and >=2.0.0."""
    def __call__(self, obj):
        try:
            import zope.interface
            from certbot.interfaces import IAuthenticator, IPluginFactory
            zope.interface.implementer(IAuthenticator)(obj)
            zope.interface.provider(IPluginFactory)(obj)
        except ImportError:
            pass
        finally:
            return obj


@backwards_compatible_authenticator()
class Authenticator(dns_common.DNSAuthenticator):
    description = "Obtain certificate using any of lego's supported DNS providers"

    _do_cleanup = False

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(
        cls, add: Callable[..., None], default_propagation_seconds: int = 60
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

    # We are overriding perform and cleanup rather than
    # _perform and _cleanup, owing due to the fact that lego wants access
    # to the challenge token but it's not exposed via _perform.
    def perform(
        self, achalls: List[achallenges.AnnotatedChallenge]
    ) -> List[challenges.ChallengeResponse]:
        self._do_cleanup = False
        self._setup_credentials()
        self._do_cleanup = True

        responses = []
        for achall in achalls:
            logger.debug(
                "Asking lego to create record %s for domain %s",
                achall.validation(achall.account_key),
                achall.domain,
            )
            LegoClient.present(
                achall.domain,
                encode_b64jose(achall.token),
                achall.key_authorization(achall.account_key),
            )
            responses.append(achall.response(achall.account_key))

        sleep_duration = self.conf("propagation-seconds")
        display_util.notify(
            f"Waiting {sleep_duration} seconds for DNS changes to propagate"
        )
        sleep(sleep_duration)

        return responses

    def cleanup(self, achalls: List[achallenges.AnnotatedChallenge]) -> None:
        if not self._do_cleanup:
            return

        for achall in achalls:
            try:
                logger.debug(
                    "Asking lego to clean up record %s for domain %s",
                    achall.validation(achall.account_key),
                    achall.domain,
                )
                LegoClient.cleanup(
                    achall.domain,
                    encode_b64jose(achall.token),
                    achall.key_authorization(achall.account_key),
                )
            except Exception as e:
                logger.warning(f"Cleanup of {achall.domain} failed: {e}")
                logger.debug("Cleanup error was", exc_info=True)

    def auth_hint(self, failed_achalls: List[achallenges.AnnotatedChallenge]) -> str:
        """See certbot.plugins.common.Plugin.auth_hint."""
        provider = self.credentials.conf("provider")
        return (
            "The Certificate Authority failed to verify the DNS TXT records created by "
            f"Lego. Ensure the above domains are hosted by {provider.capitalize()} and "
            f"check https://go-acme.github.io/lego/dns/{provider} for further details "
            "on configuring this provider. Try increasing "
            "--dns-multi-propagation-seconds from its current value of "
            f"{self.conf('propagation-seconds')} as well."
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
