# terraform-aws-lambda-layer-build

---

Terraform module that assists in building a lambda layer for your projects external dependencies.
Builds are automatically done within AWS-supported docker build containers (obviously docker is required).

Supported runtimes / package managers are:

* Python
    * poetry
* Nodejs    
    * npm
    * yarn

Example:
```hcl-terraform
module "dependencies" {
  source = "github.com/atistler/terraform-aws-lambda-layer-build.git"
  layer_name = "my-dependencies"
  package_lock_file = "${path.cwd}/../poetry.lock"
  package_manager = "poetry"
  runtime = "python3.6"
  pre_install_docker_commands = ["yum install -y postgresql-devel"]
}

resource "aws_lambda_function" "tagger" {
  function_name = "my-function"
  role = "some_role_arn"
  s3_bucket = "some_bucket"
  s3_key = "some_key"
  handler = "handler.lambda_handler"
  runtime = "python3.6"
  layers = [
    module.dependencies.layer_arn
  ]
}
```

## Providers

| Name | Version |
|------|---------|
| aws | >=2.10.0 |
| external | n/a |
| null | n/a |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:-----:|
| build\_command | The command to run to create the Lambda package zip file | `string` | `"python build.py '$filename' '$runtime' '$package_manager' '$package_lock_file' '$pre_install_docker_commands' '$extra_package_manager_args' '$docker_image'"` | no |
| build\_paths | The files or directories used by the build command, to trigger new Lambda package builds whenever build scripts change | `list(string)` | <pre>[<br>  "build.py"<br>]</pre> | no |
| docker\_image | Docker image to use to run package\_manager in, if left empty, an AWS docker build container will be used based off of the `runtime` | `string` | `""` | no |
| extra\_package\_manager\_args | Extra arguments to pass to the given package manager install command | `string` | `""` | no |
| layer\_name | The name to give the lambda layer | `string` | n/a | yes |
| package\_lock\_file | The file path to your package\_manager specific package\_lock\_file.  In the case of `npm` that would be `package-lock.json`, `yarn` would be `yarn.lock`, and `poetry` would be `poetry.lock` | `string` | n/a | yes |
| package\_manager | The package manager to use.  Nodejs supported package\_managers are `npm` and `yarn`.  Python currently supports `poetry` | `string` | n/a | yes |
| pre\_install\_docker\_commands | List of commands to run in your docker container before running the package manager install | `list(string)` | `[]` | no |
| runtime | The lambda runtime to use (python3.7, nodejs10.x, etc).  In the case that a docker\_image or docker\_file is NOT used, the runtime will be used to determine the AWS build docker image to use. | `string` | n/a | yes |

## Outputs

| Name | Description |
|------|-------------|
| layer\_arn | The ARN of the Lambda layer |