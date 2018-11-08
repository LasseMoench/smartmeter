from setuptools import setup
from sys import version_info


def readme():
    with open("README.md") as f:
        return f.read()


if version_info < (3, 3):
    raise RuntimeError("Required: Python version > 3.3")


with open("GUI/version.py") as fp:
    d = {}
    exec(fp.read(), d)
    smartmeter_version = d['version']

install_requirements = ['numpy',
                        'PyQt5',
                        'pyqtgraph',
                        'tzlocal'
                        ]

setup(
    name='smartmeter-gui',
    version=smartmeter_version,
    packages=['GUI'],
    url='https://github.com/LasseMoench/smartmeter',
    download_url='https://github.com/LasseMoench/smartmeter',
    license='gpl-3.0',
    author='Lasse Moench, Shashwat Sridhar',
    author_email='shashwat.sridhar.95@gmail.com',
    install_requires=install_requirements,
    description='Python based tool for displaying power consumption data from a remote mysql database.',
    long_description=readme(),
    entry_points='''
                [console_scripts]
                smartmeter-gui=GUI.start:launch
            ''',
    classifiers=[
                    'Development Status :: 2 - Pre-Alpha',
                    'Environment :: X11 Applications :: Qt',
                    'Intended Audience :: Science/Research',
                    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                    'Natural Language :: English',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python :: 3 :: Only',
                    'Topic :: Scientific/Engineering :: Visualization',
                    'Topic :: Scientific/Engineering :: Information Analysis'
    ]
)
