# -*- coding: utf-8 -*-
"""
    SwarmOps.views.FrontView
    ~~~~~~~~~~~~~~

    The blueprint for front view.

    :copyright: (c) 2018 by staugur.
    :license: MIT, see LICENSE for more details.
"""

from flask import Blueprint, g, redirect, url_for
from utils.web import login_required
from config import SSO

# 初始化前台蓝图
FrontBlueprint = Blueprint("front", __name__)

@FrontBlueprint.route('/')
def index():
    # 首页
    return redirect(url_for("ui.index"))

@FrontBlueprint.route("/setting/")
@login_required
def userSet():
    # 用户设置
    return redirect("{}/user/setting/".format(SSO["sso_server"].strip("/")))
