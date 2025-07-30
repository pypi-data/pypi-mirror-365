from setuptools import setup, find_packages
import os

# Read README.md if it exists
if os.path.exists("README.md"):
    with open("README.md", "r") as fh:
        long_description = fh.read()
else:
    long_description = ""

setup(
    name='expense_bot',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'python-telegram-bot==20.3',
    ],
    entry_points={
        'console_scripts': [
            'expense-bot=expense_bot.bot:main',
        ],
    },
    author='Your Name',
    description='A Telegram bot for monthly expense calculation',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/asm-shaikat',  # update if needed
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.7',
)
