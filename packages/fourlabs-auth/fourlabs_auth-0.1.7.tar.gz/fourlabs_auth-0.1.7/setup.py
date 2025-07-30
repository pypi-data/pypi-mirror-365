from setuptools import setup, find_packages

setup(
    name='fourlabs-auth',
    version='0.1.7',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Autenticação por email fourlabs para Django',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Fourlabs',
    author_email='fourlabs-un2@foursys.com.br',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=5.2',
    ],
    python_requires='>=3.8',
)