from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    description = f.read()

setup(
    name="github_oss_contributions",
    version="0.3.0",
    description="Fetch organizations where a user created issues or PRs for Open Source",
    packages=find_packages(),
    author="Mohit Upadhyay and Anuj Kumar Upadhyay",
    install_requires=[],
    python_requires=">=3.7",
    long_description=description,
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "github-oss-contributions=github_oss_contributions.cli:main"
        ]
    },
)
