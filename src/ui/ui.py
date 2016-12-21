# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, url_for, redirect, g
from utils.public import logger

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')


@ui_blueprint.route("/")
@ui_blueprint.route("/swarm/")
def index():
    if g.auth:
         Swarms      = g.swarm.GET("all", True).get("data")
         ActiveSwarm = g.swarm.GET("active").get("data")
         logger.debug(Swarms)
         logger.debug(ActiveSwarm)
         return render_template("swarm.html", Swarms=Swarms, ActiveSwarm=ActiveSwarm)
    else:
         return redirect(url_for("login"))

@ui_blueprint.route("/service/")
def service():
    if g.auth:
        return render_template("service.html")
    else:
         return redirect(url_for("login"))

@ui_blueprint.route("/node/")
def node():
    if g.auth:
        return render_template("node.html")
    else:
         return redirect(url_for("login"))

