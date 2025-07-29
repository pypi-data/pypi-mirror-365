from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='pyAsciiEngine',
    version='0.0.12',
    author='Arizel79',
    author_email='arizel79@gmail.com',
    description='Ascii games engine',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/Arizel79/pyAsciiEngine',
    packages=find_packages(),
    install_requires=[
        'windows-curses; platform_system=="Windows"',
    ],
    classifiers=[
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='ascii, ascii game',
    project_urls={
        'Documentation': 'https://github.com/Arizel79/pyAsciiEngine'
    },
    python_requires='>=3.8'
)
