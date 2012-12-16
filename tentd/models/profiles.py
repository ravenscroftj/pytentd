"""Entity profile types"""

from flask import url_for
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import backref

from tentd import __tent_version__ as tent_version
from tentd.models import db
from tentd.utils.types import JSONDict

class Profile (db.Model):
    """A profile information type belonging to an entity

    The Profile class is an abstract type, defining the relationship between
    an entity and it's profiles, and holding the schema url for the type.

    An entity cannot have multiple profiles with the same schema.

    See: https://tent.io/docs/info-types
    """
    
    id = Column(Integer, primary_key=True)
    
    #: The entity the profile belongs to
    entity = db.relationship('Entity', back_populates='profiles')
    entity_id = Column(Integer, ForeignKey('entity.id'), nullable=False)

    #: The info type schema
    schema = Column(String(256), nullable=False)

    __table_args__ = (
        UniqueConstraint("entity_id", "schema"),
    )

    #: The discriminator for the object type
    type = Column(String(50))
    
    __mapper_args__ = {
        'polymorphic_on': type,
    }

    def __init__ (self, **kwargs):
        if self.__class__ == Profile:
            raise NotImplementedError(
                "Don't create instances of Profile! "
                "Use profiles.Generic instead")
        
        super(Profile, self).__init__(**kwargs)
        
        # Set the schema if the class has one defined
        if hasattr(self.__class__, '__schema__'):
            self.schema = self.__class__.__schema__

class CoreProfile (Profile):
    """This model provides the Core profile info type.

    Documentation on this profile type can be found here:
    https://tent.io/docs/info-types#core

    TODO: Add licence and server relationships
    """
    __schema__ = 'https://tent.io/types/info/core/v0.1.0'
    __mapper_args__ = {'polymorphic_identity': 'core'}

    id = Column(Integer, ForeignKey('profile.id'), primary_key=True)

    #: The canonical entity identifier (an url)
    identifier = Column(String, unique=True)

    def to_json(self):
        # The entity's API root
        link = url_for('base.link', entity=self.entity, _external=True)

        return {
            'entity': self.identifier or link,
            'licences': [],
            'servers': [link],
            'tent_version': tent_version
        }

class BasicProfile(Profile):
    """The Basic profile info type.

    The Basic profile helps humanize users. All fields are optional but help
    provide a context in which to place a user's details.
        
    See: https://tent.io/docs/info-types#basic
    """

    __schema__ = 'https://tent.io/types/info/basic/v0.1.0'
    __mapper_args__ = {'polymorphic_identity': 'profile'}

    id = Column(Integer, ForeignKey('profile.id'), primary_key=True)

    avatar_url = Column(String)

    name       = Column(String)
    location   = Column(String)
    gender     = Column(String)

    birthdate  = Column(String)
    bio        = Column(Text)

    def to_json(self):
        return {name: getattr(self, name) for name in [
            'avatar_url',
            'name',
            'location',
            'gender',
            'birthdate',
            'bio'
        ]}

class GenericProfile(Profile):
    __mapper_args__ = {'polymorphic_identity': 'generic'}

    content = Column(JSONDict)

    def to_json(self):
        return self.content