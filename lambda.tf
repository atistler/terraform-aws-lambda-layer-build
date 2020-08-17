resource "aws_lambda_layer_version" "this" {
  layer_name = var.layer_name
  filename = data.external.built.result.filename
  depends_on = [
    null_resource.archive]
  compatible_runtimes = [
    var.runtime]
  lifecycle {
    create_before_destroy = true
  }
}
