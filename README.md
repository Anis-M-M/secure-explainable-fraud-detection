# Fraud Detection System — MSc Practicum

**Students:** Anis Mohammed Metkari · Sharwari Rajendra Nimbalkar  
**Supervisor:** Irina Tal  
**Programme:** MSc in Computing — Dublin City University

---

## About the Project

This project implements a fraud detection system that compares four detection approaches — a rule-based system, Logistic Regression, XGBoost, and a Neural Network — against the Kaggle credit card fraud dataset. The second part looks at how well SHAP and LIME explain the model decisions, and whether those explanations are stable under small input changes.

**RQ1:** How do rule-based, LR, XGBoost and Neural Network models compare on highly imbalanced fraud data?  
**RQ2:** How do SHAP and LIME differ in stability and consistency across models?

---

## Dataset

The dataset is not included in the repository (143 MB). Download it from Kaggle and place it at `data/creditcard.csv`:

Dataset: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud

284,807 transactions, 492 fraud cases (0.17%), features V1-V28 are PCA-transformed for privacy.

---

## Repository Structure

```
FRAUD DETECTION/
├── data/                          # put creditcard.csv here (not in git)
├── ml-service/
│   ├── src/                       # Python source code
│   │   ├── models/                # classifiers, rule engine, neural net
│   │   ├── explainability/        # SHAP and LIME explainers, stability
│   │   ├── training/              # training and evaluation scripts
│   │   └── utils/                 # data loader, preprocessing
│   ├── models/saved/              # trained model files (pkl, keras)
│   └── requirements.txt
├── fraud-detection-api/           # Spring Boot backend (Java)
├── fraud-detection-frontend/      # React frontend
├── Fraud_Detection_Presentation.ipynb   # main analysis notebook
├── create_notebook.py             # script to regenerate the notebook
├── docker-compose.yml
└── docs/
    ├── 01_PROJECT_SETUP_GUIDE.md
    ├── 02_ARCHITECTURE_DESIGN.md
    └── 03_IMPLEMENTATION_ROADMAP.md
```

---

## Running the ML Analysis (Notebook)

Make sure you have Python 3.11 and the dataset at `data/creditcard.csv`.

```bash
# Set up the environment
cd ml-service
python -m venv .venv

# Windows
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\pip install jupyter seaborn ipykernel
.venv\Scripts\python -m ipykernel install --user --name fraud-detection-venv --display-name "Python 3.11 (fraud detection)"

# Generate and open the notebook
.venv\Scripts\python ..\create_notebook.py
.venv\Scripts\jupyter lab ..\Fraud_Detection_Presentation.ipynb
```

Select the kernel **"Python 3.11 (fraud detection)"** when it opens.

Note: the stability analysis cell (Section 7d) takes around 5-10 minutes depending on your machine, so run it before the presentation rather than live.

---

## Running the Full Stack

Requirements: Java 17, Node 18, Docker, PostgreSQL 13+

```bash
# Create your local secrets file, then edit the values in .env
cp .env.example .env

# Start everything with Docker
docker-compose up -d

# Services:
# Frontend  http://localhost:3000
# API       http://localhost:8080/api/v1
# ML        http://localhost:8001
# Postgres  localhost:5432
```

On first start, the API creates an admin account from `ADMIN_USERNAME`, `ADMIN_EMAIL` and `ADMIN_PASSWORD` in `.env`. The password must be at least 12 characters.

Or run each service separately — see `01_PROJECT_SETUP_GUIDE.md` for step-by-step instructions.

---

## Tech Stack

Backend: Java 17, Spring Boot 3.2, Spring Security (JWT), PostgreSQL 15, Flyway  
ML service: Python 3.11, scikit-learn, XGBoost, TensorFlow, SHAP, LIME, FastAPI  
Frontend: React 18, Redux Toolkit, Tailwind CSS, Recharts  
Infrastructure: Docker, Docker Compose

---

## References

[1] A. M B et al., "Explainable AI for Credit Card Fraud Detection," ICSSAS 2025.  
[2] S. B. Shah, "Advancing Financial Security with Scalable AI," ICDCECE 2025.  
[3] V. Gokhale and A. Naik, "Credit Card Fraud Detection using ML and XAI," ICAET 2025.  
[4] W. Olabiyi et al., "Explainable AI for Fraud Detection," Oct 2023.  
[5] R. Gangavarapu et al., "Enhancing Fraud Detection with Explainable AI," ICDS 2024.
