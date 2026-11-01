venv\Scripts\activate
 
cd core

pip install -r requirements.txt

CREATE DATABASE dyslexia_db;

python manage.py migrate


python manage.py migrate

python train_model.py


python load_sample_data.py



python manage.py createsuperuser

Username: admin
Email:    admin123@gmail.com
Password: Admin@1234


python manage.py runserver