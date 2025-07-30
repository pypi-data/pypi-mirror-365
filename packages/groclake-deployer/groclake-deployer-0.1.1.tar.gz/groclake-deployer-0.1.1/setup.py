from setuptools import setup, find_packages

setup(
    name='groclake-deployer',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'groclake-deploy=groclake_deployer.deploy:full_deploy',
        ],
    },
    description='Installs Docker and runs groclake container',
    python_requires='>=3.6',
)

