from setuptools import setup, find_packages

setup(
    name="uipath-code-reviewer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "PyGithub>=2.1.1",
        "Flask>=3.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
        "PyYAML>=6.0.1",
    ],
    python_requires=">=3.8",
    author="UiPath Code Reviewer Bot",
    description="A bot that uses Azure OpenAI to review UiPath automation code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
