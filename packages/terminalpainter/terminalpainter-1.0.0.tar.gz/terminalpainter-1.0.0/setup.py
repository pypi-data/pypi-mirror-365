from setuptools import setup, find_packages

setup(
    name='terminalpainter',
    version='1.0.0',
    packages=find_packages(),
    author='professionalincpp',
    author_email='griguchaev@yandex.ru',
    description='Terminal painter',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/professionalincpp/your_project',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.10',
    install_requires=[
        'Pillow>=10.0.0'
    ],
    tests_require=[],
    setup_requires=[],
)