from setuptools import setup, find_packages

setup(
    name="triz_ai_patent_assistant",
    version="0.1.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "openai",
        "pymystem3",
        "pytest"
    ],
    author="Sergei Voronin",
    author_email="your@email.com",
    description="AI + TRIZ system for patent formula generation and analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    url="https://github.com/voroninsergei/triz-ai-patent-assistant",
    project_urls={
        "Documentation": "https://github.com/voroninsergei/triz-ai-patent-assistant/wiki",
        "Source": "https://github.com/voroninsergei/triz-ai-patent-assistant",
        "Tracker": "https://github.com/voroninsergei/triz-ai-patent-assistant/issues",
    },
    python_requires='>=3.10',
)