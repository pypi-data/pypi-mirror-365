from setuptools import setup, find_packages

# Read README.md content for long_description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='devops_automation_cli',
    version='1.0',
    description='AI-powered CLI tool for automating DevOps workflows like setup, Git, CI/CD, Docker, and documentation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Dinesh',
    author_email='dinesh121104@gmail.com',
    url='https://github.com/Dinesh-4/Devops-Automation',
    packages=find_packages(),
    install_requires=[
        'click',
        'rich',
        'sh',
        'loguru',
        'python-dotenv',
        'openai'
    ],
    entry_points={
        'console_scripts': [
            'autodevops=devops_automation_cli.cli:autodevops',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
    python_requires='>=3.6',
)
