"""Package setup for PDF Chat Assistant."""

from setuptools import setup, find_packages

setup(
    name="pdf-chat-assistant",
    version="1.0.0",
    description="Ask questions about PDF documents using a local LLM",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.10",
    install_requires=[
        "requests",
        "rich",
        "click",
        "PyPDF2",
        "PyYAML",
        "streamlit",
    ],
    entry_points={
        "console_scripts": [
            "pdf-chat=pdf_chat.cli:main",
        ],
    },
)
