# Cloud secret manager

This is a python package to handle secrets in cloud environments, handling GCP and AWS secrets.

It also helps to create a manifest to generate fake secrets for development while using external-secrets.io.

## Setup

Initialize secrets manager:

```shell
./init_secret_manager.sh
```

Run secret manager:

```shell
# Either activate with poetry shell and run it
poetry -C . shell
es-cloud-secret-manager --help
# deactive when done
deactivate

# Either run it through poetry
poetry -C . run es-cloud-secret-manager --help
```

Format the code:

```shell
# Format the code with isort and autopep8
./format.sh
```

## Yaml format

For secret with yaml format, if you want it to have a better formatting, better install yq and sponge.

```shell
# eg. for Ubuntu
sudo apt install yq moreutils
```

## GCP

```shell
# First authenticate to your GCP project
gcloud auth application-default login --project <project id>

es-cloud-secret-manager --project project gcp --gcp-project <project id> list --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> create --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> initialize --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> details --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> import --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> export --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> diff --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> fake --secrets cluster external
es-cloud-secret-manager --project project gcp --gcp-project <project id> delete --secret-name external --version 1
```

## AWS

```shell
# First configure AWS
aws configure

es-cloud-secret-manager --project project aws --aws-region eu-west-1 list --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 create --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 initialize --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 details --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 import --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 export --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 diff --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 fake --secrets cluster external
es-cloud-secret-manager --project project aws --aws-region eu-west-1 delete --secret-name external --version 84e8c4e5-27c7-4nov-z9f5-50c398fe4911
```

## Release in testpypi

You can either build it with twine or with poetry.

You would need to have a ~/.pypirc file with the API token for twine.

```shell
python3 -m pip install --upgrade build
python3 -m build
python3 -m pip install --upgrade twine
# twine would automatically look for the API token in the ~/.pypirc file
python3 -m twine upload --repository testpypi dist/es_cloud_secret_manager-$(grep -e '^version' pyproject.toml | head -1 | cut -d= -f2 | xargs printf)*
```

```shell
poetry config pypi-token.testpypi <YOUR_API_TOKEN>
# You can get it from your ~/.pypirc file
poetry config pypi-token.testpypi "$(git config -f ~/.pypirc --get testpypi.password | xargs printf)"

poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish --repository testpypi
```

Once deployed on testpypi, you can install it as follow:

```shell
python3 -m pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ es-cloud-secret-manager
```

## Release in pypi

Update the version in pyproject.toml and run:

```shell
./release.sh
```

Once deployed on pypi, you can install it as follow:

```shell
python3 -m pip install --upgrade es-cloud-secret-manager
```
