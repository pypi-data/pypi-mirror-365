from setuptools import setup, find_packages

setup(
    name="mktr",
    version="0.1.0",
    description="Convert tree structure into actual folders/files via GUI",
    author="Kamil Małek",
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
