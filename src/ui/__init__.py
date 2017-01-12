# -*- coding:utf-8 -*-
#
# SwarmOps views for ui
#

from flask import Blueprint, render_template, url_for, redirect, g, request

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')

@ui_blueprint.route("/")
@ui_blueprint.route("/swarm/")
def index():
    if g.auth:
        return render_template("swarm.html")
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

@ui_blueprint.route("/misc/")
def misc():
    if g.auth:
        return render_template("misc.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/storage/")
def storage():
    if g.auth:
        return render_template("storage.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/nginx/")
def nginx():
    if g.auth:
        return render_template("nginx.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/network/")
def network():
    if g.auth:
        return render_template("network.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/registry/")
def registry():
    if g.auth:
        return render_template("registry.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/registry/<imageId>")
def registryImageId(imageId):
    if g.auth:
        return render_template("image.html")
    else:
        return redirect(url_for("login"))
