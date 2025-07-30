from setuptools import setup, find_packages

setup(
    name="django-monnaie-converter",
    version="0.1.3",
    description="Un convertisseur de monnaies simple pour Django",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Nicosidick",
    author_email="abou210traore@gmail.com",
    url="https://github.com/toncompte/django-monnaie-converter",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Django>=3.0"
    ],
    python_requires=">=3.6",
)
