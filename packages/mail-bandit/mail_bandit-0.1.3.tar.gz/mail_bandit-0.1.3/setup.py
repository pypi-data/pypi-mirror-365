from setuptools import setup, find_packages

setup(
    name="mail_bandit",
    version="0.1.3",  # 🚨 increment this every time you re-upload
    author="Jabez Gershon Aldrin",
    author_email="Jabez123jaze@gmail.com",
    description="Mail Bandit is a fast, lightweight tool that classifies emails into five categories using DistilBERT and XGBoost.",
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
