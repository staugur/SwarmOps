# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, alert
from utils.public import logger

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')


@ui_blueprint.route("/")
def index():
    if g.auth:
         Swarms      = g.swarm.GET("all", True)
         ActiveSwarm = g.swarm.GET("active")
         return render_template("index.html", Swarms=Swarms, SwarmsLength=len(Swarms), ActiveSwarm=ActiveSwarm)
    else:
        alert(403)



