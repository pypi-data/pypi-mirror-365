from setuptools import setup, find_packages

setup(
    name='emoji-diamond',
    version='0.1',
    author='Joseph Bonsu 🇬🇭',
    author_email='your_email@example.com',
    description='A Python package that generates a diamond shape using random emojis.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/OligoCodes/emoji_diamond',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
