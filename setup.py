from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="chatbot_query_library",
    version="0.1.0",
    description="Python library for easy querying of popular chatbots",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jacobgelling/chatbot-query-library",
    author="Jacob Gelling",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.7, <4",
    install_requires=[
        "openai>=0.28,<1",
        "asyncio",
        "browser_cookie3",
        "python-gemini-api>=2.4",
        "EdgeGPT @ https://github.com/jacobgelling/EdgeGPT/archive/refs/tags/0.14.1.zip",
        "requests",
        "tqdm",
    ],
    project_urls={
        "Bug Reports": "https://github.com/jacobgelling/chatbot-query-library/issues",
        "Source": "https://github.com/jacobgelling/chatbot-query-library",
    },
)
