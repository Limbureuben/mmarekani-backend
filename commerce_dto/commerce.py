import graphene

# class RegistrationInputObject(graphene.InputObjectType):
#     username = graphene.String()
#     email = graphene.String(required=False)
#     password = graphene.String()
#     passwordConfirm = graphene.String()
    
    
class RegistrationObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    

class RegisterObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    


class UserLoginInputObject(graphene.InputObjectType):
    username = graphene.String()
    password = graphene.String()

class UserLoginObject(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    token = graphene.String()
    isStaff = graphene.Boolean()




class RegistrationInputObject(graphene.InputObjectType):
    username = graphene.String(required=True)
    phone = graphene.String(required=True)
    national_id = graphene.String(required=True)

class RegistrationResponse(graphene.ObjectType):
    id = graphene.ID()
    full_name = graphene.String()
    phone_number = graphene.String()
    national_id = graphene.String()