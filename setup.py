from setuptools import setup


setup(
    name='tequila-cli',
    version='0.1',
    py_modules=['tequila'],
    install_requires=['click'],
    entry_points={
        'console_scripts': ['tequila=tequila:cli'],
    },
)
