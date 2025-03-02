# image-compression-system

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

uvicorn server:app --reload

------

venv\Scripts\activate

python cron_job.py