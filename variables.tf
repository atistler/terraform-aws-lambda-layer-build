# Required variables.

variable "runtime" {
  description = "The lambda runtime to use (python3.7, nodejs10.x, etc).  In the case that a docker_image or docker_file is NOT used, the runtime will be used to determine the AWS build docker image to use."
  type = string
}
variable "layer_name" {
  description = "The name to give the lambda layer"
  type = string
}
variable "package_manager" {
  description = "The package manager to use.  Nodejs supported package_managers are `npm` and `yarn`.  Python currently supports `poetry`"
  type = string
}
variable "package_lock_file" {
  description = "The file path to your package_manager specific package_lock_file.  In the case of `npm` that would be `package-lock.json`, `yarn` would be `yarn.lock`, and `poetry` would be `poetry.lock`"
  type = string
}
# Optional variables specific to this module.
variable "build_command" {
  description = "The command to run to create the Lambda package zip file"
  type = string
  default = "python build.py '$filename' '$runtime' '$package_manager' '$package_lock_file' '$pre_install_docker_commands' '$extra_package_manager_args' '$docker_image'"
}
variable "build_paths" {
  description = "The files or directories used by the build command, to trigger new Lambda package builds whenever build scripts change"
  type = list(string)
  default = [
    "build.py"]
}
variable "pre_install_docker_commands" {
  description = "List of commands to run in your docker container before running the package manager install"
  type = list(string)
  default = []
}
variable "extra_package_manager_args" {
  description = "Extra arguments to pass to the given package manager install command"
  type = string
  default = ""
}
variable "docker_image" {
  description = "Docker image to use to run package_manager in, if left empty, an AWS docker build container will be used based off of the `runtime`"
  type = string
  default = ""
}

