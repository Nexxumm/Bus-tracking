
FROM python:3.8-slim

# Set environment variables to prevent Python from writing pyc files and to buffer outputs
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of your project code into the container
COPY . /

# Command to run the Django application with Gunicorn
CMD ["gunicorn", "Dvm.wsgi:application", "--bind", "0.0.0.0:8000"]
