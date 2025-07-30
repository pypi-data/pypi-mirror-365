from setuptools import setup, find_packages, findall

print("packages: " + str(find_packages()))

setup(
    name='bayserver',
    version='3.0.0',
    packages=find_packages(),
    author='Michisuke-P',
    author_email='michisukep@gmail.com',
    description='BayServer for Python',
    license='MIT',
    python_requires=">=3.7",
    url='https://baykit.yokohama/',
    package_data={
    },
    install_requires=[
      "bayserver-core==3.0.0",
      "bayserver-docker-cgi==3.0.0",
      "bayserver-docker-http3==3.0.0",
      "bayserver-docker-fcgi==3.0.0",
      "bayserver-docker-maccaferri==3.0.0",
      "bayserver-docker-ajp==3.0.0",
      "bayserver-docker-http==3.0.0",
      "bayserver-docker-wordpress==3.0.0",
    ],
    scripts=['bayserver_py'],
    include_package_data = True,
)

