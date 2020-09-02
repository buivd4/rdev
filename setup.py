from setuptools import setup, find_packages


install_requires = []
for line in open('requirements.txt', 'r'):
    install_requires.append(line.strip())

setup(
    name='rdev',
    version='0.1',
    keywords=('remote','dev','code','sync', 'rsync'),
    description='Remote sync tool for developer.',
    url='http://github.com/buivd4/rdev',
    license='MIT License',
    author='duongbv',
    author_email='buivd4@hotmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'rdev=rdev:main',
        ],
    },
    zip_safe=False,
    install_requires=install_requires
)
