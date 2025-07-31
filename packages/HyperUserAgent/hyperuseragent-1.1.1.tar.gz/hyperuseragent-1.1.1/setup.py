from setuptools import setup, find_packages

setup(
    name="HyperUserAgent",
    version="1.1.1",
    description="Hyper-UA ─ ultra-realistic User-Agent & fingerprint generator.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Hritu",
    author_email="hrituraj5717@gmail.com",
    url="https://github.com/TheHritu/HyperUserAgent",
    license="MIT",
    packages=find_packages(),
    package_data={
        "HyperUserAgent.config": ["*.json", "*.yaml"],
    },
    install_requires=[
        "httpx==0.28.1",
        "Pillow==11.3.0",
        "PyYAML==6.0.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
    ],
)
