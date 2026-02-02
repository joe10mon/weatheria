# Weather App - Microservices Architecture Tutorial

A complete weather application demonstrating microservices architecture, REST APIs, frontend-backend communication, and cloud deployment.

## 🏗️ Architecture Overview

```
┌─────────────────┐         REST API          ┌──────────────────┐         External API       ┌────────────────┐
│                 │  ───────────────────────>  │                  │  ────────────────────────> │                │
│   Frontend      │    HTTP Request (JSON)     │  Backend Flask   │    HTTP Request           │  OpenWeather   │
│   (HTML/JS)     │                             │   Microservice   │                            │     API        │
│                 │  <───────────────────────  │                  │  <──────────────────────── │                │
└─────────────────┘         JSON Response       └──────────────────┘         JSON Response      └────────────────┘
   Port: 8080                                        Port: 5000                                    External Cloud
```

## 📁 Project Structure

```
weather-app/
├── weather-frontend/
│   └── index.html              # Frontend HTML + JavaScript
├── weather-backend/
│   ├── app.py                  # Flask REST API
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container configuration
│   └── .env.example           # Environment variables template
├── docker-compose.yml         # Orchestration configuration
└── README.md                  # This file
```

## 🚀 Quick Start Guide

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Docker & Docker Compose (for containerization)
- A web browser
- OpenWeatherMap API key (free)

### Step 1: Get Your API Key

1. Go to [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Navigate to "API keys" section
4. Copy your API key

### Step 2: Set Up the Backend

```bash
# Navigate to backend directory
cd weather-backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your API key
# OPENWEATHER_API_KEY=your_actual_api_key_here
```

### Step 3: Run the Backend

```bash
# Option 1: Run directly with Python
python app.py

# The backend will start on http://localhost:5000
```

### Step 4: Run the Frontend

```bash
# Open a new terminal
cd weather-frontend

# Option 1: Use Python's built-in server
python -m http.server 8080

# Option 2: Use any other local web server
# The frontend will be available at http://localhost:8080
```

### Step 5: Test the Application

1. Open your browser and go to `http://localhost:8080`
2. Enter a city name (e.g., "London", "Tokyo", "New York")
3. Click "Search" to see the weather information

## 🔧 Understanding the Architecture

### 1. REST API Communication

**Frontend → Backend:**
```javascript
// JavaScript fetch request
fetch('http://localhost:5000/api/weather?city=London')
```

**Backend → External API:**
```python
# Python requests to OpenWeatherMap
response = requests.get(
    'https://api.openweathermap.org/data/2.5/weather',
    params={'q': city, 'appid': API_KEY}
)
```

### 2. Microservices Pattern

This app demonstrates microservices through:

- **Separation of Concerns**: Frontend and backend are independent services
- **API Gateway Pattern**: Backend acts as a gateway to external services
- **Service Independence**: Each service can be deployed/scaled independently
- **Communication via REST**: Services communicate using HTTP/JSON

### 3. Key REST API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/api/health` | GET | Health check for monitoring |
| `/api/weather?city=London` | GET | Get weather data |

### 4. Data Flow

1. User enters city name in frontend
2. Frontend sends HTTP GET request to backend
3. Backend validates the request
4. Backend calls OpenWeatherMap API
5. Backend transforms the data
6. Backend sends JSON response to frontend
7. Frontend displays the weather information

## 🐳 Docker Deployment

### Build and Run with Docker Compose

```bash
# Make sure you're in the root directory
cd weather-app

# Create .env file with your API key
echo "OPENWEATHER_API_KEY=your_api_key_here" > .env

# Build and start all services
docker-compose up --build

# Access the app at http://localhost:8080
```

### Individual Container Commands

```bash
# Build backend container
docker build -t weather-backend ./weather-backend

# Run backend container
docker run -p 5000:5000 -e OPENWEATHER_API_KEY=your_key weather-backend

# Run frontend container
docker run -p 8080:80 -v $(pwd)/weather-frontend:/usr/share/nginx/html nginx:alpine
```

## ☁️ Cloud Deployment Guide

### Option 1: Deploy to AWS (EC2)

```bash
# 1. Launch an EC2 instance (Ubuntu 22.04)
# 2. SSH into your instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y

# 4. Clone your project
git clone your-repo-url
cd weather-app

# 5. Set up environment variables
echo "OPENWEATHER_API_KEY=your_key" > .env

# 6. Run with Docker Compose
sudo docker-compose up -d

# 7. Configure security group to allow ports 5000 and 8080
# Access: http://your-instance-ip:8080
```

### Option 2: Deploy to Heroku

```bash
# Backend deployment
cd weather-backend
heroku login
heroku create weather-backend-app
heroku config:set OPENWEATHER_API_KEY=your_key
git init
git add .
git commit -m "Initial commit"
git push heroku main

# Frontend deployment
cd ../weather-frontend
# Update API_BASE_URL in index.html to your Heroku backend URL
heroku create weather-frontend-app
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

### Option 3: Deploy to Google Cloud Platform (Cloud Run)

```bash
# 1. Install gcloud CLI
# 2. Authenticate
gcloud auth login
gcloud config set project your-project-id

# 3. Build and deploy backend
cd weather-backend
gcloud builds submit --tag gcr.io/your-project-id/weather-backend
gcloud run deploy weather-backend \
  --image gcr.io/your-project-id/weather-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENWEATHER_API_KEY=your_key

# 4. Deploy frontend
cd ../weather-frontend
# Update API_BASE_URL in index.html
gcloud app deploy
```

### Option 4: Deploy to Azure

```bash
# 1. Install Azure CLI
# 2. Login
az login

# 3. Create resource group
az group create --name weather-app-rg --location eastus

# 4. Create container registry
az acr create --resource-group weather-app-rg \
  --name weatherappregistry --sku Basic

# 5. Build and push backend
cd weather-backend
az acr build --registry weatherappregistry \
  --image weather-backend:v1 .

# 6. Deploy to Azure Container Instances
az container create \
  --resource-group weather-app-rg \
  --name weather-backend \
  --image weatherappregistry.azurecr.io/weather-backend:v1 \
  --dns-name-label weather-backend-unique \
  --ports 5000 \
  --environment-variables OPENWEATHER_API_KEY=your_key
```

## 🔄 Scaling to True Microservices

To expand this into a production microservices architecture:

### 1. Add More Services

```
weather-app/
├── weather-service/        # Current backend
├── forecast-service/       # 7-day forecast
├── location-service/       # Geocoding
├── cache-service/          # Redis caching
├── notification-service/   # Weather alerts
└── api-gateway/           # Kong or Nginx
```

### 2. Add Service Discovery

Use Consul, Eureka, or Kubernetes DNS:

```yaml
# kubernetes-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: weather-service
spec:
  selector:
    app: weather-service
  ports:
    - protocol: TCP
      port: 5000
      targetPort: 5000
```

### 3. Add Load Balancing

```yaml
# docker-compose with load balancer
services:
  weather-service:
    deploy:
      replicas: 3
  
  nginx-lb:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
```

### 4. Add Message Queue (RabbitMQ/Kafka)

```python
# For async communication between services
import pika

connection = pika.BlockingConnection()
channel = connection.channel()
channel.queue_declare(queue='weather_updates')
channel.basic_publish(
    exchange='',
    routing_key='weather_updates',
    body=json.dumps(weather_data)
)
```

### 5. Add Monitoring & Logging

```python
# Add Prometheus metrics
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Add structured logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

## 🧪 Testing the API

### Using cURL

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Test weather endpoint
curl "http://localhost:5000/api/weather?city=London"

# Test with invalid city
curl "http://localhost:5000/api/weather?city=InvalidCity123"
```

### Using Python

```python
import requests

# Test the API
response = requests.get('http://localhost:5000/api/weather', 
                       params={'city': 'London'})
print(response.json())
```

### Using Postman

1. Open Postman
2. Create GET request to: `http://localhost:5000/api/weather`
3. Add query parameter: `city = London`
4. Send request and view response

## 📊 Monitoring & Health Checks

```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f weather-service

# Health check
curl http://localhost:5000/api/health

# Monitor resource usage
docker stats
```

## 🔒 Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Enable HTTPS** in production
3. **Add rate limiting** to prevent abuse
4. **Validate all inputs** on the backend
5. **Use API authentication** (JWT tokens)
6. **Enable CORS properly** - Don't use `*` in production

## 🐛 Troubleshooting

### Backend won't start
- Check if port 5000 is already in use: `lsof -i :5000`
- Verify Python dependencies: `pip list`
- Check API key is set: `echo $OPENWEATHER_API_KEY`

### Frontend can't connect to backend
- Verify backend is running: `curl http://localhost:5000/api/health`
- Check CORS is enabled in Flask
- Verify API_BASE_URL in frontend matches backend URL

### Docker issues
- Check Docker is running: `docker ps`
- View logs: `docker-compose logs`
- Rebuild containers: `docker-compose up --build`

## 📚 Learning Resources

- [REST API Design](https://restfulapi.net/)
- [Microservices Patterns](https://microservices.io/patterns/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Docker Documentation](https://docs.docker.com/)
- [OpenWeatherMap API](https://openweathermap.org/api)

## 🎯 Next Steps

1. Add user authentication (JWT)
2. Implement caching (Redis)
3. Add a database (PostgreSQL)
4. Create more microservices (forecast, alerts)
5. Add automated tests
6. Set up CI/CD pipeline
7. Implement service mesh (Istio)
8. Add monitoring (Prometheus + Grafana)

## 📝 License

This project is for educational purposes.

## 👨‍💻 Contributing

Feel free to fork and enhance this project!

---

**Happy Learning! 🚀**

For questions or issues, please check the troubleshooting section or create an issue.
