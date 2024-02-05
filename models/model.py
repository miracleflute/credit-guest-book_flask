from flask import Flask, render_template, request, redirect, url_for, Response, Blueprint, current_app
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import time
import json



db = SQLAlchemy()

class Name(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    content = db.Column(db.String(500), nullable=True)
    created_date = db.Column(db.DateTime(), nullable=True, default=datetime.now)


