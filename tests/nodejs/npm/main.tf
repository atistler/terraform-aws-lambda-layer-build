module "deps" {
  source = "../../../"
  layer_name = "my-nodejs-npm-deps"
  runtime = "nodejs10.x"
  package_manager = "npm"
  package_lock_file = "${path.cwd}/package-lock.json"
  docker_image = "node:current-alpine3.10"
#  pre_install_docker_commands = [
#    "yum install -y postgresql-devel"]
}