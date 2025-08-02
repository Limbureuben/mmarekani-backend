import graphene
from .commerce import *

class RegistrationResponse(graphene.ObjectType):
    message = graphene.String()
    success = graphene.Boolean()
    user = graphene.Field(RegisterObject)