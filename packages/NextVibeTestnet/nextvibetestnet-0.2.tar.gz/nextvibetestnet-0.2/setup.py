from setuptools import setup, find_packages

setup(
    name='NextVibeTestnet',
    version='0.2',
    packages=find_packages(),
    install_requires=["solana==0.27.0", "tronpy==0.5.0", "bitcoinlib==0.7.1", "requests==2.32.3", "python-dotenv==1.0.1"],
    tests_require=['pytest'],
    test_suite='tests',
    author='Hard',
    author_email='danylo29bro@gmail.com',
    description='A library for work with testnet wallets bitcoin, solana and tron',
    long_description_content_type='text/markdown',
    url='https://github.com/hardusss/TestnetWallets.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
