# Image Analysis service
This is a service to trigger image analysis process.

### Concept of the project
- By isolating the data in data lakes: raw, stage, and result to make the workflow more transparent with Minio.
- Make prediction(analysis) with the model on demand

### Dependencies

- Python 3.9.x
- Pyenv
- Docker

for development purpose, we consider you want to run locally:

### Run Service locally
#### 1. Setting up Python
content in progress

#### 2. Apply a virtual environment for Python

It is recommended to use a virtual environment to keep a given Python version and the project dependencies from the system Python and other projects.
There are several virtual environment managers (`venv`, `virtualenv`, `pyenv`, `pipenv`, `conda`...) and the developer is free to choose among them.

Run the commands below in the **root project folder** to build a virtual environment:
###### a way manage and control virtual environment in the same repo folder
```
brew install pyenv pyenv-virtualenv
pyenv install 3.9.12
pyenv local 3.9.12
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