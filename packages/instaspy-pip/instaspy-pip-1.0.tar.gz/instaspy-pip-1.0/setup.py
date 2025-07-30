from setuptools import setup, find_packages

setup(
    name='instaspy-pip',
    version='1.0',
    description='A tool to fetch Instagram user data and media.',
    author='spyboy',
    author_email='spyboy.co@gmail.com',
    url='https://github.com/IM-SPYBOY/instaspy',  
    packages=find_packages(),  
    install_requires=[
        'requests',                
        'instagrapi',             
        'googlesearch-python',     
        'colorama',                
        'termcolor',               
    ],
    entry_points={
        'console_scripts': [
            'instaspy=instaspy.instaspy:main',  # Corrected entry point
            'instaspy-pip=instaspy.instaspy:main',  # Corrected entry point
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3', 
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
