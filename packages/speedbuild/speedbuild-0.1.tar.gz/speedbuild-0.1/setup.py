from setuptools import setup, find_packages

setup(
    name="speedbuild",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "django",
        "pyyaml",
        "openai",
        "python-dotenv",
        "websockets"
    ],
    entry_points={
        'console_scripts': [
            'speedbuild=speedbuild.sb:start',
        ],
    },
)
