import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

def get_requirements(file_path: str) -> list[str]:
    requirements = []
    with open(file_path) as file_obj:
        requirements = file_obj.readlines()
        requirements = [req.replace("\n", "") for req in requirements]
        
        if "-e ." in requirements:
            requirements.remove("-e .")
    return requirements

__version__ = "1.1.0"
REPO_NAME = "aydie-genai"
AUTHOR = "Aditya (Aydie) Dinesh K"
AUTHOR_GITHUB_USER_NAME = "aydiegithub" 
SRC_REPO = "aydie_genai"
AUTHOR_EMAIL = "business@aydie.in"
LISCENCE = 'MIT'
DESCRIPTION = "A simple and unified Python library to interact with various Large Language Models (LLMs) like Gemini, GPT, Claude, and more by abstracting provider-specific code and authentication."

setuptools.setup(
    name=SRC_REPO,
    version=__version__,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION, 
    license=LISCENCE,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f"https://github.com/{AUTHOR_GITHUB_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_GITHUB_USER_NAME}/{REPO_NAME}/issues",
    },
    package_dir={"": "."}, 
    packages=setuptools.find_packages(where="."), 
    python_requires='>=3.9', 
    install_requires=[
        "google-generativeai",
        "openai",
        "anthropic",
        "groq",
        "deepseek",
        "mistralai",
        "python-dotenv",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)