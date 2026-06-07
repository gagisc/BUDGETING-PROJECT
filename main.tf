########################
# Provider & Basics
########################

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1" # calgary-west-1 is planned for a future change
}

########################
# IAM User & Policy
########################

resource "aws_iam_user" "budget_user" {
  name = "budget-user"
}

resource "aws_iam_policy" "budget_user_policy" {
  name        = "BudgetUserPolicy"
  description = "Permissions for AWS Budgets + SNS + EC2 shutdown"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "budgets:CreateBudget",
          "budgets:UpdateBudget",
          "budgets:DeleteBudget",
          "budgets:DescribeBudget",
          "budgets:DescribeBudgets",
          "budgets:ModifyBudget"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "sns:Publish",
          "sns:CreateTopic",
          "sns:Subscribe"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:StopInstances"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "budget_user_attach" {
  user       = aws_iam_user.budget_user.name
  policy_arn = aws_iam_policy.budget_user_policy.arn
}

# Optional: access key for budget-user (treat outputs as secrets)
resource "aws_iam_access_key" "budget_user_key" {
  user = aws_iam_user.budget_user.name
}

########################
# AWS Budget (Email Only)
########################

resource "aws_budgets_budget" "monthly_budget" {
  name         = "FortyDollarBudgetAlert"
  budget_type  = "COST"
  limit_amount = "40"
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  notification {
    comparison_operator = "GREATER_THAN"
    threshold           = 100
    threshold_type      = "PERCENTAGE"
    notification_type   = "ACTUAL"

    subscriber {
      subscription_type = "EMAIL"
      address           = "gagisc@example.com" # real email goes here
    }
  }
}

########################
# Outputs (Sensitive)
########################

output "budget_user_access_key_id" {
  value       = aws_iam_access_key.budget_user_key.id
  description = "Access key ID for budget-user"
  sensitive   = true
}

output "budget_user_secret_access_key" {
  value       = aws_iam_access_key.budget_user_key.secret
  description = "Secret access key for budget-user"
  sensitive   = true
}
