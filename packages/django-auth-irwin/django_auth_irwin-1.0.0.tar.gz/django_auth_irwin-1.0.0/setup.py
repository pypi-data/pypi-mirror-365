from setuptools import setup, find_packages

setup(
    name='django-auth-irwin',  # ← Changé
    version='1.0.0',           # ← Nouvelle version
    packages=find_packages(),
    include_package_data=True,
    description='Package Django pour authentification simple avec templates Bootstrap',  # ← Changé
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Irwin',            # ← Votre nom
    author_email='irwindjriga@gmail.com',  # ← Votre email
    license='MIT',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=[
        'django>=4.0',         # ← Version plus récente
    ],
)