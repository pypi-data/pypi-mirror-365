# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    desc = f.read()
setup(
    name="plugllm",
    version="0.1.1",
    author="Yash Kumar Firoziya",
    url="https://github.com/firoziya/plugllm",
    description="Unified LLM API interface for OpenAI, Gemini, Mistral, Groq etc.",
    long_description=desc,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["requests"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
