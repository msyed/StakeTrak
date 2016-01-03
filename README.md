# StakeTrak

StakeTrak is an internal search tool for local files. Type a name and find relevant articles and information about the person in question!

## Setup

1. Get pip. First open 'terminal' and run 'pip -V' to see if you have it installed. If so, you should see it print the version and the version of python it is running. If not, you can get it simply by running 'python get-pip.py' while in the StakeTrak directory. if that doesn't work for whatever reason, you can get pip [here](https://pip.pypa.io/en/latest/installing.html#install-pip). pip is a widely used installation tool for python dependencies and libraries like flask.
2. Please follow the instructions at [Hitchhiker's Guide to Python](http://docs.python-guide.org/en/latest/dev/virtualenvs/) in order to set up a virtual environment. A virtualenv is like a playground where you can install certain python libraries and other dependencies that only exist while the environment is activated.
3. Next, activate youre newly created virtualenv and [install Flask](http://flask.pocoo.org/docs/0.10/installation/). Just get the normal dev version, not the newest version.
4. Finally, navigate to the RetaskFlask directory and run 'python index.py' to start the server. If it is running you can navigate to the url that it provides (something like http://localhost:5000/). If it didn't work, you might need to follow the steps at the Flask website to install other dependencies (try 'pip install x', where x is the name of the dependency. Also make sure you are still within your virtual environment!) 
