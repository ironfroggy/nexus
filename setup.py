from distutils.core import setup

setup(
    name='nexus',
    packages=['nexus'],
    entry_points={
        'console_scripts': [
            'nexus=nexus:main',
        ],
    },
)