# -*- coding:utf-8 -*-


from utils.public import logger
from flask import Blueprint, request, g
from flask_restful import Api, Resource


class Label(Resource):

    @classmethod
    def get(self):

        #Initialize Request Query Parameters
        if g.auth:
            return g.swarm_node.LabelQuery(
                start      = request.args.get("start", 0),
                length     = request.args.get("length", 10),
                search     = request.args.get("search[value]", request.args.get("search", '')),
                orderindex = request.args.get("order[0][column]", 0),
                ordertype  = request.args.get("order[0][dir]", 'asc')
            )
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403

class NodeForLabel(Resource):

    @classmethod
    def get(self):

        #Initialize Request Query Parameters
        if g.auth:
            return g.swarm_node.Node_for_Label(
                start      = request.args.get("start", 0),
                length     = request.args.get("length", 10),
                search     = request.args.get("search[value]", request.args.get("search", '')),
                orderindex = request.args.get("order[0][column]", 0),
                ordertype  = request.args.get("order[0][dir]", "asc")
            )
        else:
            res = {"msg": "Authentication failed, permission denied.", "code": 403}
            logger.warn(res)
            return res, 403


misc_blueprint = Blueprint(__name__, __name__)
api = Api(misc_blueprint)
api.add_resource(Label, '/label', '/label/', endpoint='label')
api.add_resource(NodeForLabel, '/node_for_label', '/node_for_label/', endpoint='node_for_label')