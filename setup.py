import os
from setuptools import setup, Extension

install_requires = []
if not os.environ.get("SNAP_BUILD"):
    install_requires.extend(["certbot>=1.12.0", "acme>=1.12.0", "josepy>=1.1.0"])
else:
    install_requires.append("packaging")

setup(
    ext_modules=[
        Extension(
            "lego_bridge",
            [
                "certbot_dns_multi/_internal/bridge/main.go",
            ],
        )
    ],
    install_requires=install_requires,
    setup_requires=["setuptools-golang"],
    build_golang={
        "root": (
            "github.com/alexzorin/certbot-dns-multi/certbot_dns_multi/"
            "_internal/bridge"
        ),
        "strip": False,
    },
)
