# Use the specified Python image
FROM --platform=linux/amd64 python:3.10-slim

#uncomment this and comment the above one for making imgage for mac m1 arm
# FROM python:3.10-slim
# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY ./requirements.txt /app/requirements.txt

# Install the dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# Copy the rest of the application code into the container
COPY ./app /app/

# Install uvicorn
RUN pip install uvicorn

# Expose port 8080 to the outside world
EXPOSE 8080

# Set the command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# CMD ["fastapi", "run", "main.py", "--port", "8000"]