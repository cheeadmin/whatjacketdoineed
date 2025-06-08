output "website_url" {
  value = "https://${aws_cloudfront_distribution.cdn.domain_name}"
}

output "api_url" {
  value = aws_apigatewayv2_stage.default.invoke_url
}

output "cloudfront_distribution_id" {
  value = aws_cloudfront_distribution.cdn.id
}

