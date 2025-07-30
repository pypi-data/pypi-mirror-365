from setuptools import setup, find_packages

setup(
    name="web_show",
    version="0.1.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    description="Un package Django simple qui affiche une page HTML",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Tieba",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
)
