import os, setuptools

setuptools.setup(
    name = "mumen-dream-tools",
    version = "1.0.0a0",
    zip_safe = True,
    packages=setuptools.find_packages(where='./lib'),
    package_dir={
        "DMShared":"./lib/DMShared",
        "Shared":"./lib/Shared",
        "dream_collider":"./lib/dream_collider"
    }
)