# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="plugllm",
    version="0.1.0",
    author="Yash Kumar Firoziya",
    url="https://github.com/firoziya/plugllm",
    description="Unified LLM API interface for OpenAI, Gemini, Mistral, Groq etc.",
    packages=find_packages(),
    install_requires=["requests"],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
