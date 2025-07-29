from setuptools import setup, find_packages

setup(
    name='fixcmd',
    version='0.1.1',
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
    author='Your Name',
    description='GPT-powered terminal assistant',
    python_requires='>=3.7',
)
