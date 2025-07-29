from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="logiliteal",
    version="0.1.1",
    description="简洁,高扩展性,可自定义的日志库 / Simple, high extensibility, and customizable logging library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nanaloveyuki/py-logiliteal",
    author="Nanaloveyuki",
    author_email="3541766758@qq.com",
    license="MIT",
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
    ],
    keywords="logging, color, format",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.12, <4",
    install_requires=[],
    project_urls={
        "Bug Reports": "https://github.com/Nanaloveyuki/py-logiliteal/issues",
        "Source": "https://github.com/Nanaloveyuki/py-logiliteal/",
    },
)

