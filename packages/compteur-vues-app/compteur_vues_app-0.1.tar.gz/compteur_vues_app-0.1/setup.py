# setup.py

from setuptools import setup, find_packages

setup(
    name='compteur_vues_app',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='Un package Django simple et efficace pour compter automatiquement le nombre de fois que un article a été vu',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author=' ',
    author_email='Midev@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 4.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    install_requires=[
        'django>=4.0',
    ],
 python_requires='>=3.10',
)