import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bigfastapi",                     # This is the name of the package
    version="0.5.1",                        # The initial release version
    author="BigFastAPI Team",                     # Full name of the author
    author_email="support@rijen.tech",
    description="Adding lots of functionality to FastAPI",
    long_description=long_description,      # Long description read from the the readme file
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(include=['bigfastapi', 
                                                'bigfastapi.schemas', 
                                                'bigfastapi.models', 
                                                'bigfastapi.templates', 
                                                'bigfastapi.utils', 
                                                'bigfastapi.db'
                                                'bigfastapi.data']),    # List of all python modules to be installed
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.9',                # Minimum version requirement of the package
    install_requires=['Jinja2'],                     # Install other dependencies if any
    url='https://bigfastapi.com',
    keywords='fastapi, bigfastapi, auth',  # Optional
    package_data={  # Optional
        'bigfastapi': ['data/countries.json'],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/rijentech/bigfastapi',
        'Funding': 'https://bigfastapi.com',
        'Source': 'https://github.com/rijentech/bigfastapi',
    },
)