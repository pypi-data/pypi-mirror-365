from setuptools import find_packages, setup

setup(
    name="page-encryptor",
    version="0.1.0",
    description="Offline HTML encryption with in-browser decryption, inspired by PageCrypt",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Carlos Asmat",
    url="https://gitlab.com/sotilrac/page-encryptor",
    packages=find_packages(),
    install_requires=["pycryptodome>=3.23.0"],
    python_requires=">=3.12",
    entry_points={
        "console_scripts": [
            "page-encryptor=page_encryptor.encryptor:main",
        ],
    },
    include_package_data=True,
    package_data={"page_encryptor": ["decryptor_template.html"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
    ],
)
