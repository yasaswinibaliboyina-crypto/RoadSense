\# RoadSense 🚦

\### AI-Powered Road Safety and Risk Monitoring Prototype



RoadSense is a road safety prototype designed to identify potential road risks using video-based vehicle detection, visibility analysis, machine learning, and an interactive map.



\## ✨ Features



\- \*\*Vehicle Detection:\*\* Detects vehicles in road video footage using YOLO and OpenCV.

\- \*\*Visibility Analysis:\*\* Estimates road visibility using video brightness.

\- \*\*AI-Based Risk Prediction:\*\* Uses a trained machine learning model to estimate road risk.

\- \*\*Interactive Map:\*\* Displays road-related locations and mobility information.

\- \*\*EV Station Discovery:\*\* Shows available EV station information and supports nearest-station routing.

\- \*\*Local Report History:\*\* Saves and retrieves locally stored road safety reports.



\## 🛠️ Technology Stack



\- Python

\- OpenCV

\- YOLO

\- XGBoost

\- FastAPI

\- HTML, CSS, and JavaScript

\- Leaflet

\- Git and GitHub



\## 📁 Project Structure



```text

RoadSense/

├── backend/

│   ├── app.py

│   ├── aws\_storage.py

│   ├── report\_history.py

│   └── video\_stream.py

├── cleaned/

├── data/

│   └── preprocessing/

├── frontend/

│   ├── index.html

│   ├── script.js

│   └── style.css

├── ml/

│   ├── risk\_engine.py

│   ├── mobility\_engine.py

│   ├── integrated\_detection.py

│   ├── risk\_model.pkl

│   └── label\_encoder.pkl

├── opencv/

│   ├── road.mp4

│   └── road\_video.py

├── processed/

├── yolo26n.pt

└── README.md

```



\## ⚙️ Getting Started



\### 1. Clone the repository



```bash

git clone https://github.com/yasaswinibaliboyina-crypto/RoadSense.git

cd RoadSense

```



\### 2. Install Python dependencies



Create and activate a virtual environment if desired, then install the packages required by the project.



For Windows PowerShell:



```powershell

python -m venv .venv

.\\.venv\\Scripts\\Activate.ps1

```



Install the dependencies used by the project, including the required versions of FastAPI, Uvicorn, OpenCV, Ultralytics, XGBoost, pandas, and NumPy.



\### 3. Run the backend



From the project root, try:



```powershell

uvicorn backend.app:app --reload

```



If the application uses a different startup command or requires additional configuration, follow the instructions in the backend code.



\### 4. Open the frontend



Open `frontend/index.html` in a browser if the frontend is configured to run directly. Some features may require the backend server to be running.



\## 🗺️ Prototype Scope



RoadSense is a prototype for demonstrating road-risk monitoring and mobility-related features. Predictions and visibility estimates depend on the available video, trained model, and configured data. They should not be treated as guaranteed real-world safety assessments.



\## 🚀 Future Improvements



\- Integrate cloud-based report storage.

\- Improve risk predictions using validated road and accident datasets.

\- Add more road locations and mobility stations.

\- Improve deployment and setup automation.



\## 👩‍💻 Repository



GitHub: https://github.com/yasaswinibaliboyina-crypto/RoadSense



