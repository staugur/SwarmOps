# -*- coding:utf-8 -*-
#
# SwarmOps views for ui
#

from flask import Blueprint, render_template, url_for, redirect, g, request
from utils.public import logger

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')

@ui_blueprint.route("/")
@ui_blueprint.route("/swarm/")
def index():
    if g.auth:
        update      = True if request.args.get("UpdateManager", False) in ('true', 'True', True) else False
        Swarms      = g.swarm.GET("all", checkState=True, UpdateManager=update).get("data")
        ActiveSwarm = g.swarm.GET("active").get("data")
        return render_template("swarm.html", Swarms=Swarms, ActiveSwarm=ActiveSwarm)
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/service/")
def service():
    if g.auth:
        service = request.args.get("id", request.args.get("name", None))
        Services = g.service.GET(service, core=True, core_convert=True).get("data")
        return render_template("service.html", Services=Services)
    else:
         return redirect(url_for("login"))

@ui_blueprint.route("/node/")
def node():
    if g.auth:
        Nodes = g.node.GET().get("data")
        return render_template("node.html", Nodes=Nodes)
    else:
         return redirect(url_for("login"))

@ui_blueprint.route("/misc/")
def misc():
    if g.auth:
        return render_template("misc.html")
    else:
        return redirect(url_for("login"))
