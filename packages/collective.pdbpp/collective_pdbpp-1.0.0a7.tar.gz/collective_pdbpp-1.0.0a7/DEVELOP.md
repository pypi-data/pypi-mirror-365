# Using the development buildout

## plonecli

The convenient way, use plonecli build ;):

```shell
$ plonecli build
```

or with `--clear`` if you want to clean your existing venv:

```shell
$ plonecli build --clear
```

Start your instance:

```shell
$ plonecli serve
```

# Without plonecli

Create a virtualenv in the package:

```shell
$ python3 -m venv venv
```

or with `--clear` if you want to clean your existing venv:

```shell
$ python3 -m venv venv --clear
```

Install requirements with pip:

```shell
$ ./venv/bin/pip install -r requirements.txt
```

Run buildout:

```shell
$ ./venv.bin/buildout
```

Start Plone in foreground:

```shell
$ ./bin/instance fg
```

# Running tests

Run the tests with tox:

```shell
$ tox
```

list all tox environments:

```shell
$ tox -l
py38-Plone52
py39-Plone60
py310-Plone60
py311-Plone60
```

Run a specific tox environment:

```shell
$ tox -e py37-Plone52
```

# CI Github-Actions / codecov

The first time you push the repo to github, you might get an error from
codecov. Either you activate the package here:
https://app.codecov.io/gh/collective/+ Or you just wait a bit, codecov will activate your package automatically.
