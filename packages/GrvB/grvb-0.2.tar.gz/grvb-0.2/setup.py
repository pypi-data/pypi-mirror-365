from setuptools import setup, find_packages 

setup(
    name = 'GrvB',
    version = '0.2',
    author = 'Gourav Barnwal',
    author_email = 'barnwalgourav547@gmail.com',
    description = 'This is speech to text package created by Gourav Barnwal',
)
packages = find_packages()
install_requirement = [
    'selenium',
    'webdriver_manager'

]