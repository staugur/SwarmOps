# -*- coding:utf-8 -*-
#
# SwarmOps views for ui
#

from flask import Blueprint, render_template, url_for, redirect, g, abort
from utils.public import logger

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')

''' swarm route'''
@ui_blueprint.route("/")
@ui_blueprint.route("/swarm/")
def index():
    if g.auth:
        return render_template("swarm/swarm.html")
    else:
        return abort(403)

@ui_blueprint.route("/swarm/add/")
def swarm_add():
    if g.auth:
        return render_template("swarm/add.html")
    else:
        return abort(403)

@ui_blueprint.route("/swarm/init/")
def swarm_init():
    if g.auth:
        return render_template("swarm/init.html")
    else:
        return abort(403)

'''service route'''
@ui_blueprint.route("/service/")
def service():
    if g.auth:
        return render_template("service/service.html")
    else:
        return abort(403)

@ui_blueprint.route("/service/delete/")
def service_delete():
    if g.auth:
        return render_template("service/delete.html")
    else:
        return abort(403)

@ui_blueprint.route("/service/update/")
def service_update():
    if g.auth:
        return render_template("service/update.html")
    else:
        return abort(403)

@ui_blueprint.route("/service/create/")
def service_create():
    if g.auth:
        return render_template("service/create.html")
    else:
        return abort(403)

@ui_blueprint.route("/service/detail/")
def service_detail():
    if g.auth:
        return render_template("service/detail.html")
    else:
        return abort(403)

@ui_blueprint.route("/service/nginx/")
def service_nginx():
    if g.auth:
        return render_template("service/nginx.html")
    else:
        return abort(403)

'''node route'''
@ui_blueprint.route("/node/")
def node():
    if g.auth:
        return render_template("node/node.html")
    else:
        return abort(403)

@ui_blueprint.route("/node/add/")
def node_add():
    if g.auth:
        return render_template("node/add.html")
    else:
        return abort(403)

@ui_blueprint.route("/node/update/")
def node_update():
    if g.auth:
        return render_template("node/update.html")
    else:
        return abort(403)

@ui_blueprint.route("/node/delete/")
def node_delete():
    if g.auth:
        return render_template("node/delete.html")
    else:
        return abort(403)

'''misc route'''
@ui_blueprint.route("/misc/")
def misc():
    if g.auth:
        return render_template("misc.html")
    else:
        return abort(403)

@ui_blueprint.route("/storage/")
def storage():
    if g.auth:
        return render_template("misc/storage.html")
    else:
        return abort(403)

'''network route'''
@ui_blueprint.route("/network/")
def network():
    if g.auth:
        return render_template("network/network.html")
    else:
        return abort(403)

'''registry route'''
@ui_blueprint.route("/registry/")
def registry():
    if g.auth:
        return render_template("registry/registry.html")
    else:
        return abort(403)

@ui_blueprint.route("/registry/<namespace>/<repository_name>/")
def registryImageName(namespace, repository_name):
    if g.auth:
        return render_template("registry/imageName.html", imageName="{}/{}".format(namespace, repository_name).replace("_/", ""))
    else:
        return abort(403)

@ui_blueprint.route("/registry/<imageId>/")
def registryImageId(imageId):
    if g.auth:
        return render_template("registry/imageId.html", imageId=imageId)
    else:
        return abort(403)
