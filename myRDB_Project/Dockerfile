# The first instruction is what image we want to base our container on
# We Use an official Python runtime as a parent image
FROM python:3.7

WORKDIR /myRDB_Project

# By copying over requirements first, we make sure that Docker will cache
# our installed requirements rather than reinstall them on every build
COPY requirements.txt /myRDB_Project/requirements.txt
RUN pip install -r requirements.txt

# Now copy in our code, and run it
COPY . /myRDB_Project
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
