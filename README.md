📡 Router Telemetry
A lightweight Python-based system designed to collect and transmit telemetry data from routers or devices to a central server using the MQTT protocol. It features a Flask-based web dashboard, JWT-based authentication, Slack notifications, and Docker support for streamlined deployment.

🚀 Features
Telemetry Collection: Gathers data such as uptime, CPU temperature, and WAN IP.

MQTT Integration: Publishes telemetry data to an MQTT broker.

Web Dashboard: Displays collected data in a user-friendly HTML interface.

JWT Authentication: Secures API endpoints with JSON Web Tokens.

Slack Notifications: Sends alerts to a configured Slack channel upon receiving new telemetry data.

Dockerized Deployment: Simplifies setup and deployment using Docker.

Automated Testing: Includes unit tests with coverage reports for reliability.

🧰 Prerequisites
Python 3.11+

Docker (for containerized deployment)

MQTT Broker (e.g., Mosquitto)

Slack Webhook URL (for notifications)

🛠️ Installation
1. Clone the Repository
git clone https://github.com/udaybhadauria/router_telemetry.git
cd router_telemetry

2. Set Up Environment Variables
Create a .env file in the project root with the following content:

ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
JWT_SECRET=supersecretkey123
SLACK_WEBHOOK_ROUTER_TELEMETRY=https://hooks.slack.com/services/your/webhook/url

3. Install Dependencies
pip install -r requirements.txt

4. Run the Application
python mqtt_broker.py
The application will start on https://0.0.0.0:9090.

🐳 Docker Deployment
1. Build the Docker Image
docker build -t router-telemetry .

2. Run the Docker Container
docker run --rm -p 9090:9090 \
  -v $(pwd)/telemetry_log.json:/app/telemetry_log.json \
  --env-file .env \
  router-telemetry

🔐 Authentication
Obtain a JWT token by sending a POST request to the /login endpoint with valid credentials:

{
  "username": "admin",
  "password": "admin123"
}
Use the received token in the Authorization header for subsequent requests:

Authorization: Bearer <your_token>

📡 API Endpoints
POST /login

Authenticates the user and returns a JWT token.

POST /mqtt

Accepts telemetry data (requires JWT).

GET /

Displays the telemetry dashboard.

GET /api/latest-result

Returns the most recent telemetry entry (requires JWT).

GET /api/results

Returns all telemetry entries (requires JWT).

🧪 Running Tests
pytest --cov=mqtt_broker test_app.py
This command will run the unit tests and display a coverage report.

📂 Project Structure

router_telemetry/
├── mqtt_broker.py           # Main Flask application
├── test_app.py              # Unit tests
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── telemetry_log.json       # Stores telemetry data
├── .env                     # Environment variables
└── README.md                # Project documentation

🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.
