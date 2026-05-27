import boto3
import json
import logging

# -----------------------------
# Logging Setup
# -----------------------------
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Script started.")

iam = boto3.client("iam")

USER_NAME = "budget-user"
POLICY_NAME = "BudgetUserPolicy"

# -----------------------------
# Updated IAM Policy Document
# -----------------------------
policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "budgets:CreateBudget",
                "budgets:UpdateBudget",
                "budgets:DeleteBudget",
                "budgets:DescribeBudget",
                "budgets:DescribeBudgets",
                "budgets:ModifyBudget"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sns:Publish",
                "sns:CreateTopic",
                "sns:Subscribe"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:StopInstances"
            ],
            "Resource": "*"
        }
    ]
}

# -----------------------------
# Create or Update Policy
# -----------------------------
def create_or_update_policy():
    try:
        # Try to create a new policy
        response = iam.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document)
        )
        policy_arn = response["Policy"]["Arn"]
        logging.info(f"Created new policy: {policy_arn}")
        print(f"Created new policy: {policy_arn}")
        return policy_arn

    except iam.exceptions.EntityAlreadyExistsException:
        # Policy already exists — update it
        account_id = iam.get_user(UserName=USER_NAME)["User"]["Arn"].split(":")[4]
        policy_arn = f"arn:aws:iam::{account_id}:policy/{POLICY_NAME}"

        logging.info(f"Policy exists, creating new version: {policy_arn}")
        print(f"Policy exists, creating new version: {policy_arn}")

        iam.create_policy_version(
            PolicyArn=policy_arn,
            PolicyDocument=json.dumps(policy_document),
            SetAsDefault=True
        )

        logging.info("Policy updated with new version.")
        print("Policy updated with new version.")

        return policy_arn

# -----------------------------
# Attach Policy to User
# -----------------------------
def attach_policy(policy_arn):
    try:
        iam.attach_user_policy(
            UserName=USER_NAME,
            PolicyArn=policy_arn
        )
        logging.info("Policy attached to user.")
        print("Policy attached to user.")
    except Exception as e:
        logging.error(f"Error attaching policy: {e}")
        print(f"Error: {e}")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    policy_arn = create_or_update_policy()
    attach_policy(policy_arn)
    logging.info("Script finished.")
