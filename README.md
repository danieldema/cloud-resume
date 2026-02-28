# Cloud Resume

A full-stack cloud-hosted resume website with visitor analytics, built with Flask and deployed to AWS using a CI/CD pipeline.

## What It Does

- Serves an interactive online resume with a downloadable PDF
- Tracks visitor activity (IP logging, visit counts)
- Provides an analytics dashboard with daily and monthly visitor charts (Chart.js)
- Auto-deploys on every push to `main` via GitHub Actions

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, Flask |
| **Frontend** | HTML/CSS, Jinja2, Chart.js |
| **Database** | MySQL (AWS RDS) |
| **Deployment** | Docker, AWS Elastic Beanstalk |
| **CI/CD** | GitHub Actions |
| **Infrastructure** | AWS ECS Fargate, ECR, ALB, IAM, SSM Parameter Store, CloudWatch |

## Architecture

```
GitHub (push to main)
  |
  v
GitHub Actions --> Build zip --> Deploy to Elastic Beanstalk
                                        |
                                        v
                              Flask app (Gunicorn)
                                        |
                                        v
                              AWS RDS (MySQL)
                                - Visit tracking
                                - Analytics queries
```

The app is also containerized with Docker and has an alternate deployment path via ECS Fargate with an Application Load Balancer (see `task-definition.json` and `AWS_SETUP.md`).

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/` | Resume page |
| GET | `/stats` | Visitor analytics dashboard |
| GET | `/visit` | Get total visit count |
| POST | `/store_ip` | Log visitor IP |
| GET | `/ips` | List all logged IPs |
| GET | `/monthly_stats` | Visit count for a given month/year |
| GET | `/daily_stats` | Daily visit breakdown for a given month/year |

## Project Structure

```
.
├── app.py                  # Flask application
├── application.py          # Beanstalk entry point
├── Dockerfile              # Container configuration
├── requirements.txt        # Python dependencies
├── task-definition.json    # ECS Fargate task definition
├── AWS_SETUP.md            # AWS infrastructure setup guide
├── templates/
│   ├── index.html          # Resume page
│   └── stats.html          # Analytics dashboard
├── static/
│   └── Daniel_Dema_Resume.pdf
├── beanstalk/
│   └── app.py              # Beanstalk-specific app copy
└── .github/
    └── workflows/
        └── deploy.yml      # CI/CD pipeline
```

## Running Locally

```bash
# Set environment variables
export RDS_HOST=<your-db-host>
export RDS_USER=<your-db-user>
export RDS_PASSWORD=<your-db-password>
export DB_NAME=<your-db-name>

# Install dependencies
pip install -r requirements.txt

# Run
python app.py
```

Or with Docker:

```bash
docker build -t cloud-resume .
docker run -p 5000:5000 \
  -e RDS_HOST=<your-db-host> \
  -e RDS_USER=<your-db-user> \
  -e RDS_PASSWORD=<your-db-password> \
  -e DB_NAME=<your-db-name> \
  cloud-resume
```

## AWS Infrastructure

The full AWS setup is documented in [`AWS_SETUP.md`](AWS_SETUP.md), covering:

- ECR repository and ECS cluster creation
- IAM roles for task execution
- Secrets management via SSM Parameter Store
- ECS Fargate service deployment
- Application Load Balancer configuration
- CI/CD via GitHub Actions
