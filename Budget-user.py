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
# IAM Policy Document
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
                "budgets:DescribeBudgets"
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
# Create IAM User
# -----------------------------
def create_user():
    try:
        iam.create_user(UserName=USER_NAME)
        logging.info(f"Created IAM user: {USER_NAME}")
        print(f"Created IAM user: {USER_NAME}")
    except iam.exceptions.EntityAlreadyExistsException:
        logging.info("User already exists.")
        print("User already exists.")
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        print(f"Error: {e}")

# -----------------------------
# Create IAM Policy
# -----------------------------
def create_policy():
    try:
        response = iam.create_policy(
            PolicyName=POLICY_NAME,
            PolicyDocument=json.dumps(policy_document)
        )
        policy_arn = response["Policy"]["Arn"]
        logging.info(f"Created policy: {policy_arn}")
        print(f"Created policy: {policy_arn}")
        return policy_arn
    except iam.exceptions.EntityAlreadyExistsException:
        policy_arn = f"arn:aws:iam::YOUR_ACCOUNT_ID:policy/{POLICY_NAME}"
        logging.info("Policy already exists.")
        print("Policy already exists.")
        return policy_arn
    except Exception as e:
        logging.error(f"Error creating policy: {e}")
        print(f"Error: {e}")

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
# Create Access Key
# -----------------------------
def create_access_key():
    try:
        response = iam.create_access_key(UserName=USER_NAME)
        access_key = response["AccessKey"]["AccessKeyId"]
        secret_key = response["AccessKey"]["SecretAccessKey"]

        logging.info("Access key created.")
        print("\n=== ACCESS KEY CREATED ===")
        print("Save these securely:")
        print(f"Access Key: {access_key}")
        print(f"Secret Key: {secret_key}")

        return access_key, secret_key
    except Exception as e:
        logging.error(f"Error creating access key: {e}")
        print(f"Error: {e}")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    create_user()
    policy_arn = create_policy()
    attach_policy(policy_arn)
    create_access_key()

    logging.info("Script finished.")
