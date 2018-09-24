resource "aws_ecs_task_definition" "pgbouncer" {
  family                   = "query-pgbouncer-service-${var.env}"
  requires_compatibilities = ["FARGATE"]

  container_definitions = <<DEFINITION
[
  {
    "portMappings": [
      {
        "hostPort": 5432,
        "protocol": "tcp",
        "containerPort": 5432
      }
    ],
    "environment": [
      {
        "name": "DATABASE_URL",
        "value": "postgresql://${var.db_username}:${var.db_password}@${aws_rds_cluster.query.endpoint}/query_${var.env}"
      },
      {
        "name": "DEFAULT_POOL_SIZE",
        "value": "100"
      },
      {
        "name": "MIN_POOL_SIZE",
        "value": "20"
      },
      {
        "name": "MAX_CLIENT_CONN",
        "value": "4000"
      },
      {
        "name": "POOL_MODE",
        "value": "transaction"
      }
    ],
    "ulimits": [
      {
        "softLimit": 4100,
        "hardLimit": 4100,
        "name": "nofile"
      }
    ],
    "memory": 1024,
    "cpu": 512,
    "image": "quay.io/humancellatlas/docker-pgbouncer:master",
    "name": "pgbouncer-${var.env}"
  }
]
DEFINITION

  network_mode = "awsvpc"
  cpu          = "512"
  memory       = "1024"
}

resource "aws_ecs_cluster" "pgbouncer" {
  name = "query-pgbouncer-${var.env}"
}

resource "aws_ecs_service" "pgbouncer" {
  name            = "query-pgbouncer-${var.env}"
  cluster         = "${aws_ecs_cluster.pgbouncer.id}"
  task_definition = "${aws_ecs_task_definition.pgbouncer.arn}"
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = ["${aws_security_group.rds-postgres.id}"]
    subnets          = ["${var.pgbouncer_subnet_id}"]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = "${aws_lb_target_group.pgbouncer.id}"
    container_name   = "pgbouncer-${var.env}"
    container_port   = "5432"
  }

  depends_on = [
    "aws_lb_listener.front_end",
    "aws_rds_cluster_instance.cluster_instances",
  ]
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = "${aws_lb.main.id}"
  port              = "5432"
  protocol          = "TCP"

  default_action {
    target_group_arn = "${aws_lb_target_group.pgbouncer.id}"
    type             = "forward"
  }
}

resource "aws_lb" "main" {
  name               = "query-pgbouncer-${var.env}"
  subnets            = ["${var.lb_subnet_ids}"]
  load_balancer_type = "network"
  internal           = false
}

resource "aws_lb_target_group" "pgbouncer" {
  name        = "query-pgbouncer-${var.env}"
  port        = "5432"
  protocol    = "TCP"
  vpc_id      = "${var.vpc_id}"
  target_type = "ip"
}

resource "aws_cloudwatch_log_group" "pgbouncer" {
  name              = "/aws/service/query-pgbouncer-${var.env}"
  retention_in_days = 90
}
