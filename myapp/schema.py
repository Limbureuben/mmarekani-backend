import graphene
from .views import *

class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello world!"

# class Mutation(graphene.ObjectType):
#     register_user = RegistrationMutation.Field()
#     login_user = LoginUser.Field()
#     login_custmer = OTPLoginMutation.Field()

# schema = graphene.Schema(query=Query, mutation=Mutation)
