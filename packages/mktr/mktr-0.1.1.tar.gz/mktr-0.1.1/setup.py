from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="mktr",
    version="0.1.1",
    description="Convert tree structure into actual folders/files via GUI",
    author="Kamil Małek",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="truckdriverbuck@gmail.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mktr = mktr.main:main',
        ]
    },
    include_package_data=True,
    install_requires=[]
)
