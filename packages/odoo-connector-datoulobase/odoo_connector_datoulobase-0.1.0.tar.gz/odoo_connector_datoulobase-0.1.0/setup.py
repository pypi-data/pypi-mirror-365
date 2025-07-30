from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='odoo-connector-datoulobase',
    version='0.1.0',
    description='A simple and clean Python connector for Odoo XML-RPC API',
    author='D. Ben Aziz Ouattara (Datoulobase)',
    author_email='datoulobaben@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/mistermerlin/odoo_connector.git',  
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
