import boto3
import logging
from datetime import datetime

# -----------------------------
# Logging Setup
# -----------------------------

logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Script started.")

# -----------------------------
# AWS Clients
# -----------------------------
session = boto3.Session(profile_name="budget-user")
budgets = session.client("budgets")
ec2 = session.client("ec2")
sts = session.client("sts")

# -----------------------------
# Configuration
# -----------------------------
ACCOUNT_ID = "YOUR_AWS_ACCOUNT_ID"  # 12-digit ID goes here
BUDGET_NAME = "FortyDollarBudgetAlert"

# -----------------------------
# Create Budget
# -----------------------------
def create_budget():
    try:
        response = budgets.create_budget(
            AccountId=ACCOUNT_ID,
            Budget={
                "BudgetName": BUDGET_NAME,
                "BudgetLimit": {
                    "Amount": "40",
                    "Unit": "USD"
                },
                "CostFilters": {},
                "CostTypes": {
                    "IncludeTax": True,
                    "IncludeSubscription": True,
                    "UseBlended": False
                },
                "TimeUnit": "MONTHLY",
                "BudgetType": "COST"
            },
            NotificationsWithSubscribers=[
                {
                    "Notification": {
                        "NotificationType": "ACTUAL",
                        "ComparisonOperator": "GREATER_THAN",
                        "Threshold": 100,  # 100% of $40 = $40
                        "ThresholdType": "PERCENTAGE"
                    },
                    "Subscribers": [
                        {
                            "SubscriptionType": "EMAIL",
                            "Address": "gagisc@example.com"
                        }
                    ]

                }
            ]
        )
        logging.info("Budget created successfully.")
    except Exception as e:
        logging.error(f"Error creating budget: {e}")
        print(f"Error: {e}")

# -----------------------------
# Shutdown EC2 Instances
# -----------------------------
def shutdown_instances():
    try:
        instances = ec2.describe_instances(
            Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
        )

        instance_ids = []
        for reservation in instances["Reservations"]:
            for instance in reservation["Instances"]:
                instance_ids.append(instance["InstanceId"])

        if instance_ids:
            ec2.stop_instances(InstanceIds=instance_ids)
            logging.info(f"Stopped EC2 instances: {instance_ids}")
            print(f"Stopped EC2 instances: {instance_ids}")
        else:
            logging.info("No running EC2 instances found.")
            print("No running EC2 instances found.")

    except Exception as e:
        logging.error(f"Error stopping EC2 instances: {e}")
        print(f"Error: {e}")

# -----------------------------
# Main Execution
# -----------------------------
if __name__ == "__main__":
    logging.info("Creating AWS budget...")
    create_budget()

    # This function would normally be triggered by SNS → Lambda
    # You can test it manually:
    # shutdown_instances()

    logging.info("Script finished.")
