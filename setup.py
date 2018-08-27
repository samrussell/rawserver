from setuptools import setup

long_description = """
    Rawserver is a wrapper for raw ethernet sockets that plays nicely with eventlet.

    More information at https://github.com/samrussell/rawserver
"""

setup(
    name='rawserver',
    description='A wrapper for raw ethernet sockets',
    long_description=long_description,
    version='0.0.1',
    url='https://github.com/samrussell/rawserver',
    author='Sam Russell',
    author_email='sam.h.russell@gmail.com',
    license='Apache2',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3'
    ],
    keywords='raw sockets',
    packages=['rawserver'],
    python_requires='>=3',
    install_requires=[
        'netils==0.0.1'
    ]
)
