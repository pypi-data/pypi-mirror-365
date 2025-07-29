from setuptools import setup, find_packages

setup(
    name="app-creator-location",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests", "django"],
    entry_points={
        'console_scripts': [
            'get-location=app_creator.cli:get_location',
        ],
    },
    author="Traoré",
    author_email="trasouleymane980@gmail.com",
    description="Un petit outil Django/CLI pour récupérer l'emplacement IP",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/tonprofil/app-creator-location",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
