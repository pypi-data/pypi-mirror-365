import setuptools
import pathlib

here = pathlib.Path(__file__).parent.resolve()

with open(here / "README.md", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="anipy-server",
    version="0.1.1",
    description="A modern, self-hosted anime scrapper and streaming server.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="B14CK-KN1GH7",
    author_email="nafisfuad340@gmail.com",
    url="https://github.com/nfs-tech-bd/anipy-server",
    project_urls={
        "Documentation": "https://github.com/nfs-tech-bd/anipy-server#readme",
        "Source": "https://github.com/nfs-tech-bd/anipy-server",
        "SERVER": "https://anipy.fun",
    },
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "jinja2",
        "requests",
        "selenium",
        "undetected-chromedriver",
        "python-dotenv",
    ],
    entry_points={
        "console_scripts": [
            "anipy=anipy_server.main:main",
        ],
    },
    python_requires=">=3.7",
    keywords=["anime", "server", "streaming", "web", "self-hosted", "media"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Video :: Display",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
)