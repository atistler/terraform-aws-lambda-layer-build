module "deps" {
  source = "../../../"
  layer_name = "my-nodejs-npm-deps"
  runtime = "nodejs10.x"
  package_manager = "npm"
  package_lock_file = "${path.cwd}/package-lock.json"
}