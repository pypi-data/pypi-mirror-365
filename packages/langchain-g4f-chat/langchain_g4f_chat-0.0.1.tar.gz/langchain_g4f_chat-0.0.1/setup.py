import os
from setuptools import setup, find_packages

# Dynamically get absolute path to requirements.txt
current_dir = os.path.abspath(os.path.dirname(__file__))
requirements_path = os.path.join(current_dir, "requirements.txt")

with open(requirements_path, "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Read the README.md file - use the new comprehensive README
readme_file = "README_NEW.md" if os.path.exists(os.path.join(current_dir, "README_NEW.md")) else "README.md"
with open(os.path.join(current_dir, readme_file), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="langchain-g4f-chat",
    version="0.0.1",    
    author="AIMLStudent",
    author_email="aistudentlearn4@gmail.com",
    description="LangChain integration for GPT4Free (g4f) with chat, image generation, and text processing capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=[
        "langchain_g4f",
        "langchain_g4f.core",
        "langchain_g4f.text", 
        "langchain_g4f.images"
    ],
    package_dir={
        "langchain_g4f": ".",
        "langchain_g4f.core": "core",
        "langchain_g4f.text": "text",
        "langchain_g4f.images": "images"
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
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
    keywords="langchain, gpt4free, g4f, openai, chatgpt, llm, ai, image-generation, text-processing",
    include_package_data=True,
    package_data={
        "langchain_g4f": ["*.md", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/MeetSolanki530/langchain-gpt4free/issues",
        "Source": "https://github.com/MeetSolanki530/langchain-gpt4free",
        "Documentation": "https://github.com/MeetSolanki530/langchain-gpt4free/blob/main/README.md",
    },
)
