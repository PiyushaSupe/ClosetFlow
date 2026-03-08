from flask import Flask
import sys
import os

# add root directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app import app

# Vercel looks for "app"
app = app