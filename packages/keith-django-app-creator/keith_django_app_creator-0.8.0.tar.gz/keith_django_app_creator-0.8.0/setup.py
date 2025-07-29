from setuptools import setup, find_packages

setup(
    name='keith-django-app-creator',
    version='0.8.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Générateur de structure d\'app Django personnalisée',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Keith44',
    author_email='keitamohamed1432@gmail.com',
    entry_points={
        'console_scripts': [
            'newapp = app_creator.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[],
)
