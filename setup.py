from setuptools import setup, Extension

setup(
    ext_modules=[
        Extension(
            "lego_bridge",
            [
                "certbot_dns_multi/_internal/bridge/main.go",
            ],
        )
    ],
    setup_requires=["setuptools-golang"],
    build_golang={
        "root": (
            "github.com/alexzorin/certbot-dns-multi/certbot_dns_multi/"
            "_internal/bridge"
        ),
        "strip": False,
    },
)
