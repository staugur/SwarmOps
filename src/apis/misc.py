# -*- coding:utf-8 -*-

from utils.public import logger
from flask import Blueprint, request, g, jsonify
from flask_restful import Api, Resource

misc_blueprint = Blueprint(__name__, __name__)
api = Api(misc_blueprint)

