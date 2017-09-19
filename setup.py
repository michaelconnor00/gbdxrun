from setuptools import setup

setup(
    name='gbdxrun',
    version='0.0.1',
    description='GBDX Local Workflow Execution',
    install_requires=[
        'gbdxtools',
        'docker',
        'toposort'
    ],
    packages=['gbdxrun'],
    author='Michael Connor',
    author_email='mike@sparkgeo.com',
    url='https://github.com/michaelconnor00/gbdxrun',
    license='MIT'
)
