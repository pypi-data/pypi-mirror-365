from setuptools import setup, find_packages

setup(
    name='RAGnificentAI',
    version='1.3',
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "langchain",
        "langchain-core",
        "langchain-community",
        "langchain-groq",
        "langchain-openai",
        "langgraph",
        "python-dotenv",
        "click"
    ],
    entry_points={
        "console_scripts": [
            "ragnificentai = RAGnificentAI.cli.commands:cli",
        ],
    },
    author='K. M. Abul Farhad-Ibn-Alam',
    author_email='abulfarhad.ibnalam@gmail.com',
    description='A simple RAG chatbot supporting multiple LLM providers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Abul-Farhad/RAGnificentAI',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
    python_requires='>=3.9',
    keywords='llm chatbot rag openai groq gemini',
    project_urls={
        # 'Bug Reports': 'https://github.com/Abul-Farhad/simple-rag/issues',
        'Source': 'https://github.com/Abul-Farhad/RAGnificentAI',
    },
    license="Custom",
    license_files=('LICENSE',),
)