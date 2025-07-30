from setuptools import find_namespace_packages, setup

with open("requirements.txt") as f:
    required = f.read().splitlines()
    requirements_dev = open("requirements-dev.txt").read().splitlines()

    setup(
        name="traxix.rsq",
        version="0.2.5",
        url="https://gitlab.com/traxix/python/rsq",
        packages=find_namespace_packages(include=["traxix"]),
        scripts=["rsq"],
        license="GPLv3",
        author="trax Omar Givernaud",
        author_email="o.givernaud@gmail.com",
        install_requires=required,
        extras_require={"dev": requirements_dev},
    )
