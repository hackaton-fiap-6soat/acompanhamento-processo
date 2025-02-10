provider "aws" {
  region = "us-east-1"
}

terraform {
  backend "s3" {
    bucket         = "techchallangebucket"
    key            = "hackaton.tfstate"
    region         = "us-east-1"
    encrypt        = true
  }
}

data "aws_vpc" "hackaton-vpc" {
  filter {
    name   = "tag:Name"
    values = ["fiap-hackathon-vpc"]
  }
}

# Captura todas as subnets privadas dentro da VPC correta
data "aws_subnets" "private_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.hackaton-vpc.id]
  }
}

# Captura as tabelas de roteamento associadas às subnets
data "aws_route_tables" "private_route_tables" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.hackaton-vpc.id]
  }
}

# Captura as subnets individualmente
data "aws_subnet" "private_subnet" {
  for_each = toset(data.aws_subnets.private_subnets.ids)
  id       = each.value
}

resource "aws_security_group" "lambda" {
  name        = "lambda-sg"
  description = "Security group for Lambda"
  vpc_id      = data.aws_vpc.hackaton-vpc.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Permitir todo o tráfego de entrada (ajuste conforme necessário)
    cidr_blocks = ["0.0.0.0/0"]  # Ajuste para permitir apenas o tráfego necessário
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # Permitir todo o tráfego de saída
    cidr_blocks = ["0.0.0.0/0"]  # Ajuste para permitir apenas o tráfego necessário
  }
}

# Captura o API Gateway existente
data "aws_apigatewayv2_apis" "apis" {
  name = "api_gw_api"
}

# Criar um VPC Endpoint para o DynamoDB
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = data.aws_vpc.hackaton-vpc.id
  service_name = "com.amazonaws.us-east-1.dynamodb"
  route_table_ids = data.aws_route_tables.private_route_tables.ids
}

resource "aws_dynamodb_table" "acompanhamento_processo" {
  name           = "AcompanhamentoProcesso"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id_usuario"

  attribute {
    name = "id_usuario"
    type = "S"
  }

  tags = {
    Environment = "Production"
    Project     = "AcompanhamentoProcesso"
  }
}

variable "s3_bucket_name" {
  description = "Nome do bucket S3 para armazenar o código Lambda"
  type        = string
  default     = "lambda-code-acompanhamento-fiap"
}

resource "aws_s3_object" "lambda_api_code" {
  bucket = var.s3_bucket_name
  key    = "lambda-api.zip"
  source = "lambda-api.zip"

  provisioner "local-exec" {
    command = "echo 'Listing directory contents:' && ls -l"
  }
}

# Criar o objeto no S3 para o código da Lambda SQS
resource "aws_s3_object" "lambda_sqs_code" {
  bucket = var.s3_bucket_name
  key    = "lambda-sqs.zip"
  source = "lambda-sqs.zip"

  provisioner "local-exec" {
    command = "echo 'Listing directory contents:' && ls -l"
  }
}

resource "aws_lambda_function" "api_lambda" {
  function_name    = "AcompanhamentoAPI"
  s3_bucket        = aws_s3_object.lambda_api_code.bucket
  s3_key           = aws_s3_object.lambda_api_code.key
  handler          = "app.main.handler"
  runtime          = "python3.10"
  role             = "arn:aws:iam::529515678525:role/LabRole"
  memory_size      = 128
  timeout          = 30
  architectures    = ["x86_64"]

  vpc_config {
    subnet_ids         = values(data.aws_subnet.private_subnet)[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }
}

resource "aws_lambda_function" "sqs_lambda" {
  function_name    = "AcompanhamentoSQS"
  s3_bucket        = aws_s3_object.lambda_sqs_code.bucket
  s3_key           = aws_s3_object.lambda_sqs_code.key
  handler          = "app.adapter.adapters_in.handler"
  runtime          = "python3.10"
  role             = "arn:aws:iam::529515678525:role/LabRole"
  memory_size      = 128
  timeout          = 30
  architectures    = ["x86_64"]

  vpc_config {
    subnet_ids         = values(data.aws_subnet.private_subnet)[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }
}

resource "aws_sqs_queue" "queue_acompanhamento" {
  name = "queue-acompanhamento"
}

resource "aws_lambda_permission" "allow_sqs" {
  statement_id  = "AllowSQSTrigger"
  action        = "lambda:InvokeFunction"
  principal     = "sqs.amazonaws.com"
  source_arn    = aws_sqs_queue.queue_acompanhamento.arn
  function_name = aws_lambda_function.sqs_lambda.function_name
}

resource "aws_lambda_event_source_mapping" "sqs_trigger" {
  event_source_arn  = aws_sqs_queue.queue_acompanhamento.arn
  function_name     = aws_lambda_function.sqs_lambda.arn
  batch_size        = 10
  enabled           = true

  depends_on = [
    aws_sqs_queue.queue_acompanhamento
  ]

  lifecycle {
    ignore_changes = [event_source_arn]
  }
}

#Criar o API Gateway
resource "aws_api_gateway_rest_api" "acompanhamento_api" {
  name        = "GatewayAcompanhamento"
  description = "API Gateway para a Lambda AcompanhamentoAPI"
}

resource "aws_api_gateway_resource" "acompanhamentos_resource" {
  rest_api_id = aws_api_gateway_rest_api.acompanhamento_api.id
  parent_id   = aws_api_gateway_rest_api.acompanhamento_api.root_resource_id
  path_part   = "api"
}

resource "aws_api_gateway_resource" "v1_resource" {
  rest_api_id = aws_api_gateway_rest_api.acompanhamento_api.id
  parent_id   = aws_api_gateway_resource.acompanhamentos_resource.id
  path_part   = "v1"
}

resource "aws_api_gateway_resource" "acompanhamentos_path" {
  rest_api_id = aws_api_gateway_rest_api.acompanhamento_api.id
  parent_id   = aws_api_gateway_resource.v1_resource.id
  path_part   = "acompanhamentos"
}

resource "aws_api_gateway_resource" "id_path" {
  rest_api_id = aws_api_gateway_rest_api.acompanhamento_api.id
  parent_id   = aws_api_gateway_resource.acompanhamentos_path.id
  path_part   = "{id}"
}

# Configurar o método GET
resource "aws_api_gateway_method" "get_acompanhamentos" {
  rest_api_id   = aws_api_gateway_rest_api.acompanhamento_api.id
  resource_id   = aws_api_gateway_resource.id_path.id
  http_method   = "GET"
  authorization = "NONE"

  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.acompanhamento_api.id
  resource_id             = aws_api_gateway_resource.id_path.id
  http_method             = aws_api_gateway_method.get_acompanhamentos.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_lambda.invoke_arn
}

resource "aws_lambda_permission" "api_gateway_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.acompanhamento_api.execution_arn}/*/*"
}

resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [aws_api_gateway_integration.lambda_integration]
  rest_api_id = aws_api_gateway_rest_api.acompanhamento_api.id
}

resource "aws_api_gateway_stage" "prod_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.acompanhamento_api.id
  stage_name    = "prod"
}

resource "aws_api_gateway_usage_plan" "usage_plan" {
  name = "AcompanhamentoAPIUsagePlan"

  api_stages {
    api_id = aws_api_gateway_rest_api.acompanhamento_api.id
    stage  = aws_api_gateway_stage.prod_stage.stage_name
  }

  throttle_settings {
    rate_limit  = 1000
    burst_limit = 1000
  }

  quota_settings {
    limit  = 1000
    period = "MONTH"
  }
}

resource "aws_api_gateway_api_key" "api_key" {
  name    = "AcompanhamentoAPIKey"
  enabled = true
}

resource "aws_api_gateway_usage_plan_key" "usage_plan_key" {
  key_id        = aws_api_gateway_api_key.api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.usage_plan.id
}

# Outputs
output "sqs_lambda_function_name" {
  value = aws_lambda_function.sqs_lambda.function_name
}

output "data_query_lambda_function_name" {
  value = aws_lambda_function.api_lambda.function_name
}

output "sqs_queue_url" {
  value = aws_sqs_queue.queue_acompanhamento.url
}

output "api_url" {
  value = "https://${aws_api_gateway_rest_api.acompanhamento_api.id}.execute-api.us-east-1.amazonaws.com/prod/api/v1/acompanhamentos/{id}"
}
