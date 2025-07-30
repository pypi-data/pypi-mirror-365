from setuptools import setup, find_packages


setup(
    name="rootlearn",  
    version="0.1.1",
    author="Pranjal Kumar",
    description="A simple Linear Regression implementation from scratch",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Automatiscally find all packages (like modelss)
    install_requires=[        # From requirements.txt (or just list them)
        "numpy",
        "pandas",
        'scikit-learn>=1.0.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)