# whatjacketdoineed.com

A simple serverless site built on AWS with serverless technologies using Terraform, with CI/CD on github workflows.

> "What jacket do I need today?"  
> This site tells you what jacket do you need based on your location and current weather conditions.

---

## Architecture Overview

This project is built entirely using **Terraform** and deployed via **GitHub Actions** on every push to `main`.

### AWS Components

| Component        | Purpose                                  |
|------------------|-------------------------------------------|
| **S3**           | Hosts static frontend (HTML/JS)           |
| **CloudFront**   | CDN in front of S3 with HTTPS             |
| **Lambda**       | Backend weather logic for recommendations |
| **API Gateway**  | Exposes the Lambda over HTTP              |
| **Route 53**     | Domain routing (`whatjacketdoineed.com`) |
| **ACM**          | SSL cert for HTTPS                        |

---

## Architecture Diagram

```text
+------------------+
|   User Browser   |
+--------+---------+
         |
         v
+--------+---------+
|    Route 53      |
+--------+---------+
         |
         v
+--------+---------+
|    CloudFront    |
+--------+---------+
    |         |
    |         v
    |   +-----+-----+
    |   |     S3    | (Static Frontend)
    |   +-----------+
    |
    v
+--------+---------+
|  API Gateway     |
+--------+---------+
         |
         v
+--------+---------+
|     Lambda        | ---> Calls FreeWeather API
+--------+---------+
         |
         v
+------------------+
| Jacket Recommendation|
| Returned to Browser|
+------------------+
```

---

## Implementation Details

Using this project to learn how to host site with serverless techologies and how to set it up with TF.

### Tools & Technologies

- **Terraform** – Used to provision all infrastructure (S3, Lambda, CloudFront, API Gateway, Route 53, ACM)
- **GitHub Actions** – CI/CD pipeline to deploy frontend and backend on every push to `main`
- **AWS Lambda** – Python-based function that returns jacket recommendations
- **API Gateway** – Routes HTTP requests to Lambda
- **FreeWeather API** – Provide weather data
- **CloudFront + S3** – S3 Static Site as origin serves with Cloudfront
- **Route 53 + ACM** – Custom domain (whatjacketdoineed.com) certificate

---

### CI/CD Workflow Summary

GitHub Actions automatically:

1. Syncs frontend files to S3 (`terraform/frontend/`)
2. Invalidates CloudFront cache
3. Zips and deploys the Lambda function (`terraform/lambda/handler.py`)

```bash
aws s3 sync terraform/frontend/ s3://<bucket> --delete
aws cloudfront create-invalidation --distribution-id <id> --paths "/*"
aws lambda update-function-code --function-name <name> --zip-file fileb://...
```

---

### Project Structure

```
terraform/
├── backend/         # Lambda and API Gateway infra
├── frontend/        # Static HTML/CSS/JS
├── lambda/          # Python Lambda function
└── main.tf          # Root Terraform config and module wiring
```

---

### Terraform Highlights

- Modular design for clarity and reusability
- Lambda and API Gateway configured via Terraform
- Secure S3 bucket with static hosting and CloudFront origin
- DNS + SSL cert automation with Route 53 and ACM
- Lambda deployed using GitHub Actions (not Terraform `archive_file`)

---

### Future Improvements

- Write better logic into what type of jacket is needed (Shell + parka / Just layer?)

