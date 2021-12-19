from setuptools import setup, find_packages


VERSION = '0.1'
DESCRIPTION = "Implementation tools for Zoho CRM"
LONG_DESCRIPTION = "A pet project I'm working, makes API calls to Zoho APIS"

setup(
    name="zohoDevKit",
    version=VERSION,
    author="Dylan Garrett",
    author_email="dylan.g@zohocorp.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    pages=find_packages(),
    install_requires=['requests', 'json'],
    keywords=['zoho', 'crm', 'api']
)
