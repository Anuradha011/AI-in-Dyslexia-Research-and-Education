# 🧠 AI in Dyslexia Research and Education

An AI-powered web application built with Django that supports dyslexia research and education. It combines a machine learning model with a web interface to help with screening, learning support, and data management.

## ✨ Features

- 🤖 **ML-based dyslexia analysis**: a trained model for screening and prediction
- 🗄️ **Database-backed**: stores users, assessments, and results
- 🛠️ **Admin dashboard**: manage data through the Django admin panel
- 📊 **Sample data loader**: quickly populate the app for testing and demos
- 📚 **Education support**: tools aimed at learners, educators, and researchers

## 🧰 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Django |
| Machine Learning | <scikit-learn / TensorFlow / etc.> |
| Database | <MySQL / PostgreSQL> |
| Frontend | HTML, CSS, JavaScript |

## 📁 Project Structure

```
AI-in-Dyslexia-Research-and-Education/
├── core/                  # Django project (apps, models, ML scripts)
│   ├── manage.py
│   ├── requirements.txt
│   ├── train_model.py     # Trains the ML model
│   └── load_sample_data.py# Loads demo data
└── README.md
```

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.9+
- <MySQL / PostgreSQL> installed and running
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Anuradha011/AI-in-Dyslexia-Research-and-Education.git
cd AI-in-Dyslexia-Research-and-Education
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
cd core
pip install -r requirements.txt
```

### 4. Create the database
```sql
CREATE DATABASE dyslexia_db;
```
Then update the database credentials in `core/settings.py` (or your `.env` file).

### 5. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Train the ML model
```bash
python train_model.py
```

### 7. Load sample data
```bash
python load_sample_data.py
```

### 8. Create an admin user
```bash
python manage.py createsuperuser
```
Follow the prompts to set your own username, email, and a strong password.

### 9. Run the server
```bash
python manage.py runserver
```
Open **http://127.0.0.1:8000/** in your browser. The admin panel is at **http://127.0.0.1:8000/admin/**.

## 🚀 Usage

1. Log in or register.
2. Complete the assessment or use the learning tools.
3. View AI-generated results and insights.
4. Admins can manage users and data from the admin panel.

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push: `git push origin feature/your-feature`
5. Open a Pull Request

## ⚠️ Disclaimer

This project is for **research and educational purposes only**. It is **not a medical diagnostic tool**. Please consult a qualified professional for any dyslexia diagnosis.

## 📄 License

<Add a license, e.g. MIT>

## 👤 Author

**Anuradha** — [@Anuradha011](https://github.com/Anuradha011)
