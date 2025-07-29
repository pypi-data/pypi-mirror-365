from setuptools import setup, find_packages
import pathlib

long_description = pathlib.Path("README.md").read_text(encoding="utf-8")

setup(
    name="PY_TELUGU_VERSION",
    version="1.2",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "PY_TELUGU_VERSION": ["keywords_te.json"],
    },
    entry_points={
        'console_scripts': [
            'pythontel = PY_TELUGU_VERSION.auto_update:main',
            'pythonrun = PY_TELUGU_VERSION.main:main',
        ],
    },
    author="sunstromium",
    description="Literal Telugu package for Python programming",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Markdown content type
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
