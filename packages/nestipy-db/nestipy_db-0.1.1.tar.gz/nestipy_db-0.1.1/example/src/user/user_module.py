from nestipy.common import Module
from nestipy_db import DbModule

from .auth_model import Auth
from .user_controller import UserController
from .user_model import Profile, User
from .user_service import UserService


@Module(
    imports=[
        DbModule.for_feature(User, Profile),
        DbModule.for_feature(Auth)
    ],
    providers=[UserService],
    controllers=[UserController],
)
class UserModule:
    ...
