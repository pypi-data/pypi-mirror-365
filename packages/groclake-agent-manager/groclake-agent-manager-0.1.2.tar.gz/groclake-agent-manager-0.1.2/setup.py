# setup.py
from setuptools import setup
from setuptools.command.install import install
import subprocess

class PostInstallCommand(install):
    def run(self):
        # Run your post-install script here
        subprocess.call(['python3', '-m', 'groclake_agent_manager.agent_manager'])
        install.run(self)

setup(
    name='groclake-agent-manager',
    version='0.1.2',
    packages=['groclake_agent_manager'],
    install_requires=[
        'requests>=2.0.0',
    ],
    entry_points={
        'console_scripts': [
            'groclake-agent-manager = groclake_agent_manager.agent_manager:main'
        ],
    },
    cmdclass={
        'install': PostInstallCommand,
    },
)

