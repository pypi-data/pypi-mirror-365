from setuptools import setup, find_packages

setup(
    name='hidden_selenium',
    version='0.1.2',
    author='Max Base',
    description='A stealthy undetected browser automation tool using Selenium.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'undetected-chromedriver>=3.5.3',
    ],
    python_requires='>=3.7',
)
