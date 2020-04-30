# Required variables.

variable "runtime" {
  type = string
}
variable "layer_name" {
  type = string
}
variable "package_manager" {
  type = string
}
variable "package_lock_file" {
  type = string
}
# Optional variables specific to this module.
variable "build_command" {
  description = "The command to run to create the Lambda package zip file"
  type = string
  default = "python build.py '$filename' '$runtime' '$package_manager' '$package_lock_file' '$yum_packages'"
}
variable "build_paths" {
  description = "The files or directories used by the build command, to trigger new Lambda package builds whenever build scripts change"
  type = list(string)
  default = [
    "build.py"]
}
variable "yum_packages" {
  description = "List of rpm package names to install via yum"
  type = list(string)
  default = []
}

