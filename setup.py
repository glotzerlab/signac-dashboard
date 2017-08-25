from setuptools import setup, find_packages

setup(
    name='signac-dashboard',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
        'Flask-Assets',
        'Flask-Turbolinks',
        'libsass',
        'cssmin',
        'jsmin'
    ],

    author='Bradley Dice',
    author_email='bdice@bradleydice.com',
    description="Data visualization based on signac.",
    keywords='visualization dashboard signac framework',
    url='https://bitbucket.org/bdice/signac-dashboard',

)
