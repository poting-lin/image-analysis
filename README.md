# Image Analysis service
This is a service to trigger image analysis process.


### Dependencies

- Python 3.8.x
- Pyenv
- Docker

## How to run it
There are 3 ways to run the application:
* Run locally
* Deploy to local docker and run it locally
* Deploy to docker in cloud and run it from cloud

for development purpose, we consider you want to run locally:

### Run Service locally
#### 1. Setting up Python
content in progress

#### 2. Apply a virtual environment for Python

It is recommended to use a virtual environment to isolate a given Python version and the project dependencies from the system Python and other projects.
There are several virtual environment managers (`venv`, `virtualenv`, `pyenv`, `pipenv`, `conda`...) and the developer is free to choose among them.

For convenience, below we provide instructions on how to set up this project using `pyenv`.
For a deeper understanding of `pyenv`, check out [Managing Multiple Python Versions With pyenv](https://realpython.com/intro-to-pyenv/).


Run the commands below in the **root project folder** to build a virtual environment:
##### Option 1: venv
###### a way manage and control virtual environment in the same repo folder
```
brew install pyenv pyenv-virtualenv
pyenv install 3.8.9
pyenv local 3.8.9
python -m venv .venv
python -m pip install --upgrade pip
source .venv/bin/activate

```
###### Activate manually if you can not see it activate on terminal by below:
```
source .venv/bin/activate
```

#### 3. Installing dependencies
Once clone the repo to local, run below command from terminal
```
./run.sh dep-install
```

#### 4. Prepare .env file
make sure you have a .env file including above content in root folder.


#### 5. Running the Service locally

```
./run.sh start
```


##### then you can make request vis Postman or any api tool by http://0.0.0.0:8080


### Other commands
#### 1. Running tests

```
./run.sh test
```
#### 2. Linting code

- At the very minimum, any code MUST pass `./run.sh check` (this is enforced during CI).
- Code need to pass `./run.sh lint`.
- For a full linting (including style), run `pylint src` at the root folder.


#### 3. generate unit tst report
pytest --junitxml=junit/test-results.xml --cov=src --cov-report=xml --cov-report=html filename

coverage html filename