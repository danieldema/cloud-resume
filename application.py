from app import app

# Beanstalk looks for 'application' variable
application = app

if __name__ == "__main__":
    application.run()