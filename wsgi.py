import sys
import os

sys.path.insert(0, '/home/coding/Job_App')

os.environ.setdefault('FLASK_ENV', 'production')

from app import app as app 