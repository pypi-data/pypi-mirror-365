from setuptools import setup, find_packages

setup(
    name='adpkg', 
    version='0.1.0', 
    author='Amit Dutta',
    author_email='amitdutta4255@gmail.com',
    description='A package for advanced mathematical calculations including interest, custom math, and geometry.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/notamitgamer', 
    packages=find_packages(), 
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', 
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    python_requires='>=3.6', 
)