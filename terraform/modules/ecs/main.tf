resource "aws_ecs_cluster" "this" {
  name = var.cluster_name
}

output "cluster_arn" {
  value = aws_ecs_cluster.this.arn
}
