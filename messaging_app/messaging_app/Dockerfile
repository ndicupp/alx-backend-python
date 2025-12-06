pip install --upgrade pip
pip freeze > requirements.txt

Django>=4.0
djangorestframework

sudo apt update
sudo apt install ca-certificates curl gnupg -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y

docker --version
docker run hello-world

# Base image
FROM python:3.10

# Set work directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose Django default port
EXPOSE 8000

# Default command to run the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


docker build -t robust-api-app .

docker images

docker run -p 8000:8000 robust-api-app

docker run -p 8000:8000 -v $(pwd):/app robust-api-app


Open your browser and visit:

http://localhost:8000

You should see:

Django default page
or

Your “Building Robust APIs” endpoints / DRF UI

If you have a /api/ endpoint, test it:

curl http://localhost:8000/api/





