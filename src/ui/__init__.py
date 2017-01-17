# -*- coding:utf-8 -*-
#
# SwarmOps views for ui
#

from flask import Blueprint, render_template, url_for, redirect, g, request

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')

''' swarm route'''
@ui_blueprint.route("/")
@ui_blueprint.route("/swarm/")
def index():
    if g.auth:
        return render_template("swarm/swarm.html")
    else:
        return redirect(url_for("login"))

'''service route'''
@ui_blueprint.route("/service/")
def service():
    if g.auth:
        return render_template("service/service.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/service/delete/")
def service_delete():
    if g.auth:
        return render_template("service/delete.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/service/update/")
def service_update():
    if g.auth:
        return render_template("service/update.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/service/create/")
def service_create():
    if g.auth:
        return render_template("service/create.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/service/detail/")
def service_detail():
    if g.auth:
        return render_template("service/detail.html")
    else:
        return redirect(url_for("login"))

'''node route'''
@ui_blueprint.route("/node/")
def node():
    if g.auth:
        return render_template("node/node.html")
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
        return render_template("misc/storage.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/nginx/")
def nginx():
    if g.auth:
        return render_template("service/nginx.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/network/")
def network():
    if g.auth:
        return render_template("network/network.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/registry/")
def registry():
    if g.auth:
        return render_template("registry/registry.html")
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/registry/<namespace>/<repository_name>/")
def registryImageName(namespace, repository_name):
    if g.auth:
        return render_template("registry/imageName.html", imageName="{}/{}".format(namespace, repository_name))
    else:
        return redirect(url_for("login"))

@ui_blueprint.route("/registry/<imageId>")
def registryImageId(imageId):
    if g.auth:
        return render_template("registry/imageId.html", imageId=imageId)
    else:
        return redirect(url_for("login"))
