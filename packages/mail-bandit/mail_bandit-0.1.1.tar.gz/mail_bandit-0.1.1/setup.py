from setuptools import setup, find_packages

setup(
    name="mail_bandit",
    version="0.1.1",  # 🚨 increment this every time you re-upload
    author="Your Name",
    author_email="your.email@example.com",
    description="Email classifier into 5 types using DistilBERT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mail-bandit",  # Replace if needed
    packages=find_packages(),
    install_requires=[
        "transformers",
        "scikit-learn",
        "pandas",
        "joblib",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'mailbandit = mailbandit.main:main',  # if main.py has a main()
        ],
    },
)
