# -*- coding:utf-8 -*-
#
# SwarmOps views for ui
#

from flask import Blueprint, render_template, url_for, redirect, g, abort
from utils.web import login_required

ui_blueprint = Blueprint("ui", __name__, template_folder="templates", static_folder='static')

''' swarm route'''
@ui_blueprint.route("/")
@ui_blueprint.route("/swarm/")
@login_required
def index():
    return render_template("swarm/swarm.html")

@ui_blueprint.route("/swarm/add/")
@login_required
def swarm_add():
    return render_template("swarm/add.html")

@ui_blueprint.route("/swarm/init/")
@login_required
def swarm_init():
    return render_template("swarm/init.html")

'''service route'''
@ui_blueprint.route("/service/")
@login_required
def service():
    return render_template("service/service.html")

@ui_blueprint.route("/service/delete/")
@login_required
def service_delete():
    return render_template("service/delete.html")

@ui_blueprint.route("/service/update/")
@login_required
def service_update():
    return render_template("service/update.html")

@ui_blueprint.route("/service/create/")
@login_required
def service_create():
    return render_template("service/create.html")

@ui_blueprint.route("/service/detail/")
@login_required
def service_detail():
    return render_template("service/detail.html")

@ui_blueprint.route("/service/nginx/")
@login_required
def service_nginx():
    return render_template("service/nginx.html")

'''node route'''
@ui_blueprint.route("/node/")
@login_required
def node():
    return render_template("node/node.html")

@ui_blueprint.route("/node/add/")
@login_required
def node_add():
    return render_template("node/add.html")

@ui_blueprint.route("/node/update/")
@login_required
def node_update():
    return render_template("node/update.html")

@ui_blueprint.route("/node/delete/")
@login_required
def node_delete():
    return render_template("node/delete.html")

'''misc route'''
@ui_blueprint.route("/misc/")
@login_required
def misc():
    return render_template("misc.html")

@ui_blueprint.route("/storage/")
@login_required
def storage():
    return render_template("misc/storage.html")

'''network route'''
@ui_blueprint.route("/network/")
@login_required
def network():
    return render_template("network/network.html")

'''registry route'''
@ui_blueprint.route("/registry/")
@login_required
def registry():
    return render_template("registry/registry.html")

@ui_blueprint.route("/registry/<namespace>/<repository_name>/")
@login_required
def registryImageName(namespace, repository_name):
    return render_template("registry/imageName.html", imageName="{}/{}".format(namespace, repository_name).replace("_/", ""))

@ui_blueprint.route("/registry/<imageId>/")
@login_required
def registryImageId(imageId):
    return render_template("registry/imageId.html", imageId=imageId)
