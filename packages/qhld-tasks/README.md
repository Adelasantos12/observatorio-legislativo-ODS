# TIPI TASKS

A list of tasks for celery to manage tasks from users

## Setup

This project uses [pipenv](https://pipenv.readthedocs.io/en/latest/), you
should install pipenv to configure and run this project.

```
$ pipenv install
```

You can find a requirements.txt file too, so if you don't want to install
pipenv you can install all dependencies using normal pip:

```
$ pip install -r requirements.txt
```

## Run

```
$ celery -A tipi_tasks worker -B -l info
```

If you're using pipenv environment you should run with the pipenv run command

```
$ pipenv run celery -A tipi_tasks worker -B -l info
```

## Docker

There's a docker-compose for development that deploys a mongodb a redis and the
python app with all deps.

To run this you should edit the .env file in: `dockerdev/.env` and set your
path in the `APP_PATH` variable.

To run all services:

```
$ cd dockerdev
$ docker-compose up -d
```

You'll have three containers running:

 * tipi\_tasks
 * tipi\_db
 * tipi\_redis

You should be able to enter in any of this containers with the `docker exec`, like:

```
# to get a shell
$ docker exec -ti tipi_tasks sh
# to get a python shell
$ docker exec -ti tipi_tasks pipenv run ipython
# to run the test script
$ docker exec -ti tipi_tasks pipenv run ./test-task.py
```

```
$ docker exec -ti tipi_redis sh
```

```
$ docker exec -ti tipi_db bash
```

## Load test data in mongo db

```
$ docker cp testdb.js tipi_db:/tmp/
$ docker exec -ti tipi_db mongo /tmp/testdb.js
```

## Launching a task

To launch a task you should import the task from the `tipi_tasks` module and
then call with the delay, for example:

```python
from tipi_tasks import test
task = test.test_task.apply_async((3, 2))
```

The task will be sent to the celery queue and will be executed by the broker.

## Configuring

This module uses a python file as a configuration, if you use this project
copying the source code you can edit the config file `tipi_tasks/config.py`.

To avoid conflicts in deployment with git the config file tries to load a
`local_config.py` file if exists that replaces all defined variables there.
So to use a custom configuration you should create a file called
`local_config.py` and place it in the directory where you'll launch the
celery worker and tasks.

## Custom Validation email template

The email template used to validate searches is placed in
`tipi_tasks/templates/validation.html`, but this can be replaced with the
configuration. There's a config variable called `TEMPLATE_DIR` that you
can override to use a custom template directory. For example:

```python
# local_config.py


TEMPLATE_DIR = '/var/www/templates/'

DEBUG = True

CLEAN_EMAILS_TIMEOUT = 10
```

In this example, the file `validation.html` should exists inside the directory
`/var/www/templates`.

You can use some variables in the template that will be replaced with the
corresponding values:

  * Email: email
  * Email hash: email\_id
  * Search hash: hash
  * Days left to confirm: timeout

To use this inside the html file you should follow the handlebars-style template
language, something like:

```html
<html>
    <body>
        Confirmation for the Email: {{email}}. You've {{timeout}} days to confirm this.
        <br/>
        Please, click in the following link to validate:
        <a href="http://mydomain.com/validate/email/{{email_id}}/{{hash}}/>Validate</a>
    </body>
</html>
```

## Add more tasks

Add new tasks to this project is really easy, you can add a new module with more
`shared_task` or `periodic_task` and then do the `import *` in the `__init__.py`
file.

## Tasks tracking and return values

In this version it's not possible to define custom tasks that return values or to
track the task status. To be able to do that the celery app must define a backend
and there's a problem right now with the latest python version (3.7) and the current
celery version (4.2.0).  This problem should be fixed in the next celery release.

## Contributing

This projects uses [celery](http://docs.celeryproject.org) for all tasks, so
it's really easy to extend the list of tasks available to use in other modules.
