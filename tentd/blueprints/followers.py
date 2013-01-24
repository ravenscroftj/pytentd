"""Follower endpoints"""

from datetime import datetime

import requests

from flask import json, jsonify, request, g
from flask.views import MethodView
from mongoengine import ValidationError

from tentd.control import follow
from tentd.flask import EntityBlueprint
from tentd.utils.auth import require_authorization
from tentd.utils.exceptions import APIBadRequest
from tentd.documents import Notification

followers = EntityBlueprint('followers', __name__, url_prefix='/followers')

@followers.route_class('')
class FollowersView(MethodView):
    """View for followers-based routes."""

    def post(self):
        """Starts following a user, defined by the post data"""
        follower = follow.start_following(g.entity, request.json)
        return jsonify(follower.to_json())

@followers.route_class('/<string:follower_id>')
class FollowerView(MethodView):
    """View for follower-based routes."""

    decorators = [require_authorization]

    def get(self, follower_id):
        """Returns the json representation of a follower"""
        follower = g.entity.followers.get_or_404(id=follower_id)
        return jsonify(follower.to_json())
    
    def put(self, follower_id):
        """Updates a following relationship."""
        follower = follow.update_follower(g.entity, follower_id, request.json)
        return jsonify(follower.to_json())
    
    def delete(self, follower_id):
        """Deletes a following relationship."""
        try:
            follow.stop_following(g.entity, follower_id)
            return '', 200
        except ValidationError:
            raise APIBadRequest("The given follower id was invalid")