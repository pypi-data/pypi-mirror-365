from setuptools import setup, find_packages

setup(
    name='paperbase',
    version='2.0',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'paperbase': ['addon/auth_handler.exe']
    },
    install_requires=[],
    author='PaperCode',
    author_email='aritra.paper.code@gmail.com',
    description='Simple file-based database with user auth',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
    ]
)
