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
  source = "git://github.com/atistler/terraform-aws-lambda-layer-build.git"
  layer_name = "my-dependencies"
  package_lock_file = "${path.cwd}/../poetry.lock"
  package_manager = "poetry"
  runtime = "python3.6"
  yum_packages = [
    "postgresql-devel"]
}

resource "aws_lambda_function" "tagger" {
  function_name = "${local.prefix}-tagger"
  role = module.tagger_role.this_iam_role_arn
  s3_bucket = aws_s3_bucket_object.src.bucket
  s3_key = aws_s3_bucket_object.src.key
  handler = "services.tagger.handler.lambda_handler"
  runtime = "python3.6"
  source_code_hash = data.archive_file.src.output_base64sha256
  layers = [
    module.dependencies.layer_arn
  ]
}
```

## Providers

The following providers are used by this module:

- aws

- external

- null

## Required Inputs

The following input variables are required:

### layer\_name

Description: n/a

Type: `string`

### package\_lock\_file

Description: n/a

Type: `string`

### package\_manager

Description: n/a

Type: `string`

### runtime

Description: n/a

Type: `string`

## Optional Inputs

The following input variables are optional (have default values):

### build\_command

Description: The command to run to create the Lambda package zip file

Type: `string`

Default: `"python build.py '$filename' '$runtime' '$package_manager' '$package_lock_file' '$yum_packages'"`

### build\_paths

Description: The files or directories used by the build command, to trigger new Lambda package builds whenever build scripts change

Type: `list(string)`

Default:

```json
[
  "build.py"
]
```

### yum\_packages

Description: List of rpm package names to install via yum

Type: `list(string)`

Default: `[]`

## Outputs

The following outputs are exported:

### layer\_arn

Description: The ARN of the Lambda layer

