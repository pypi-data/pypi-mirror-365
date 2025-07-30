from setuptools import setup, find_packages

requirements = [
    'pillow',
    'pygments',
]

with open('README.md', encoding='UTF-8') as f:
    readme = f.read()

setup(
    name = 'pycodesnap',
    version = '0.2',
    author='Shayan Heidari',
    author_email = 'contact@shayanheidari.info',
    description = 'PyCodeSnap for format codes and code to image.',
    keywords = ['codesnap', 'code', 'image'],
    long_description = readme,
    python_requires='~=3.6',
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/shayanheidari01/pycodesnap',
    packages = find_packages(),
    exclude_package_data = {'': ['*.pyc', '*__pycache__*']},
    install_requires = requirements,
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'License :: OSI Approved :: MIT License',
    ],
)