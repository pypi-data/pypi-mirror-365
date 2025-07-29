import os
from setuptools import setup, find_packages

# Dynamically get absolute path to requirements.txt
current_dir = os.path.abspath(os.path.dirname(__file__))
requirements_path = os.path.join(current_dir, "requirements.txt")

with open(requirements_path, "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read the README.md file
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="langchain-g4f-chat",
    version="0.1.2",
    author="Meet Solanki",
    author_email="solankimeet530@gmail.com",
    description="LangChain integration for GPT4Free (g4f)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MeetSolanki530/langchain-gpt4free",
    packages=["langchain_g4f", "langchain_g4f.chat_models"],
    package_dir={"langchain_g4f": "."},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="langchain, gpt4free, g4f, openai, chatgpt, llm",
)
