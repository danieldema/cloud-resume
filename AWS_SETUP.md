# AWS ECS CI/CD Setup Guide

## Prerequisites
- AWS CLI installed and configured
- GitHub repository created
- Your AWS Account ID

## Step 1: AWS Infrastructure Setup

### 1.1 Create ECR Repository
```bash
aws ecr create-repository --repository-name resume-app --region us-east-2
```

### 1.2 Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name resume-cluster --region us-east-2
```

### 1.3 Create IAM Roles

**ECS Task Execution Role:**
```bash
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'

aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

**ECS Task Role:**
```bash
aws iam create-role --role-name ecsTaskRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'
```

### 1.4 Store Database Secrets in Parameter Store
```bash
aws ssm put-parameter --name "/resume-app/rds-host" --value "resume-database.c1gwgeywogbx.us-east-2.rds.amazonaws.com" --type "SecureString" --region us-east-2
aws ssm put-parameter --name "/resume-app/rds-user" --value "admin" --type "SecureString" --region us-east-2
aws ssm put-parameter --name "/resume-app/rds-password" --value "Saturn24!!" --type "SecureString" --region us-east-2
aws ssm put-parameter --name "/resume-app/db-name" --value "resume_tracker" --type "SecureString" --region us-east-2
```

### 1.5 Update IAM Role for Parameter Store Access
```bash
aws iam attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess
```

## Step 2: Update Configuration Files

### 2.1 Update task-definition.json
Replace `YOUR_ACCOUNT_ID` with your actual AWS Account ID in:
- `executionRoleArn`
- `taskRoleArn` 
- `image` URL
- All Parameter Store ARNs

### 2.2 Create GitHub Secrets
In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:

- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key

## Step 3: Register Task Definition
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json --region us-east-2
```

## Step 4: Create ECS Service
```bash
aws ecs create-service \
  --cluster resume-cluster \
  --service-name resume-service \
  --task-definition resume-task-def \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxx,subnet-yyyyyy],securityGroups=[sg-xxxxxx],assignPublicIp=ENABLED}" \
  --region us-east-2
```

**Note:** Replace subnet and security group IDs with your VPC values.

## Step 5: Set Up Load Balancer (Optional but Recommended)

### 5.1 Create Application Load Balancer
```bash
aws elbv2 create-load-balancer \
  --name resume-alb \
  --subnets subnet-xxxxxx subnet-yyyyyy \
  --security-groups sg-xxxxxx \
  --region us-east-2
```

### 5.2 Create Target Group
```bash
aws elbv2 create-target-group \
  --name resume-targets \
  --protocol HTTP \
  --port 5000 \
  --vpc-id vpc-xxxxxx \
  --target-type ip \
  --health-check-path / \
  --region us-east-2
```

### 5.3 Create Listener
```bash
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:us-east-2:ACCOUNT:loadbalancer/app/resume-alb/xxxxx \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:us-east-2:ACCOUNT:targetgroup/resume-targets/xxxxx
```

## Step 6: Test the Pipeline

1. Push changes to your main branch
2. Check GitHub Actions for deployment status
3. Monitor ECS service deployment
4. Access your application via the load balancer DNS name

## Troubleshooting

### Common Issues:
- **IAM permissions**: Ensure roles have correct policies attached
- **Networking**: Check security groups allow traffic on port 5000
- **Task definition**: Verify all ARNs and account IDs are correct
- **Secrets**: Ensure Parameter Store values are accessible

### Useful Commands:
```bash
# Check ECS service status
aws ecs describe-services --cluster resume-cluster --services resume-service

# View task logs
aws logs get-log-events --log-group-name /ecs/resume-app --log-stream-name ecs/resume-app/TASK_ID

# Check task definition
aws ecs describe-task-definition --task-definition resume-task-def
```

## Next Steps

1. **Custom Domain**: Point your domain to the load balancer
2. **HTTPS**: Add SSL certificate via ACM
3. **Monitoring**: Set up CloudWatch alarms
4. **Auto Scaling**: Configure ECS service auto scaling