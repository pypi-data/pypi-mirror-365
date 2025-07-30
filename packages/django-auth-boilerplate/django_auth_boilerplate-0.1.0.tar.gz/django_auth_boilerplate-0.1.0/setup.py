from setuptools import setup, find_packages
import pathlib

# Read the contents of your README file
BASE_DIR = pathlib.Path(__file__).resolve().parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")



setup(
    name="django-auth-boilerplate",
    version="0.1.0",
    author="Emmanuel Ibe",
    author_email="ibehemmanuel32@gmail.com",
    description="A clean Django authentication boilerplate with JWT, rate limiting, and custom exception handling.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Meekemma/auth-boilerplate.git",
    project_urls={
        "Bug Tracker": "https://github.com/Meekemma/auth-boilerplate.git/issues",
        "Documentation": "https://github.com/Meekemma/auth-boilerplate.git#readme",
    },
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "example_project", "example_project.*"]),
    include_package_data=True,
    install_requires=[
        "Django==5.2.4",
        "djangorestframework==3.16.0",
        "djangorestframework_simplejwt==5.5.1",
        "PyJWT==2.10.1",
        "asgiref==3.9.1",
        "sqlparse==0.5.3",
        "tzdata==2025.2",
    ],
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 5.2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    keywords="django authentication jwt rest framework boilerplate",
)
