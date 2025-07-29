from setuptools import setup, find_packages
import pathlib

# Load README.md content
this_directory = pathlib.Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='fixcmd',
    version='0.1.4',
    packages=find_packages(),
    install_requires=[
        'openai>=1.0.0',
        'python-dotenv'
    ],
    entry_points={
        'console_scripts': [
            'fixcmd = terminal_gpt.suggest:main'
        ]
    },
    author='Parishith Ragumar',
    author_email='ragupari07@gmail.com',
    description='GPT-powered terminal assistant',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ragupari/terminal-gpt',
    python_requires='>=3.7',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',  # Change if you're using a different license
    ],
)
