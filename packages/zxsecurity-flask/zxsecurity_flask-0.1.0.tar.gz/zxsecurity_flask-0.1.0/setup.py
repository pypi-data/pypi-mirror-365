from setuptools import setup, find_packages

setup(
    name="zxsecurity-flask",
    version="0.1.0",
    description="A Flask-adapted version of ZXsecurity in Python",
    author="ZXstudios",
    packages=find_packages(),
    install_requires=[
        'psutil>=5.9.8',
        'requests>=2.31.0',
        'flask',
        'python-dateutil>=2.8.2',
        'cryptography',
    ],
    python_requires='>=3.7',
)