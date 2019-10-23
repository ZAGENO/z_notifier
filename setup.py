import os
import codecs
from setuptools import setup, find_packages


__version__ = None
exec(open("version.py").read())

pwd = os.path.abspath(os.path.dirname(__file__))
long_description = ""
with codecs.open(os.path.join(pwd, "README.md"), encoding="utf-8") as readme:
    long_description = readme.read()

install_requires = ['requests>=2.22.0']
tests_require = ["pytest", "pytest-cov", "codecov", "flake8", "black"]

setup(
    name="z_notifier",
    version=__version__,
    description="Slack API to send messages via webhook URLs based on programmatic implementation or logger handler",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZAGENO/z_notifier",
    author="David Vartanian",
    author_email="david.vartanian@zageno.com",
    python_requires=">=3.7.0",
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=["pytest-runner"],
    test_suite="tests",
    tests_require=tests_require,
    packages=find_packages(
        exclude=["tests", "tests.*"]
    ),
)
