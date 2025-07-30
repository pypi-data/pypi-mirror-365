from setuptools import setup

setup(
    name='html2css',
    version='1.0.2',
    py_modules=['html2css'],
    entry_points={
        'console_scripts': [
            'html2css = html2css:main',
        ],
    },
    author='Your Name',
    author_email='your@email.com',
    description='A simple CLI tool to generate CSS skeleton from HTML',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/html2css',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
