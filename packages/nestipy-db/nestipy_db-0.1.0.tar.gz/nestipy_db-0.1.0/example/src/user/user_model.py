import edgy

from nestipy_db import BaseModel, Model


@Model()
class User(BaseModel):
    is_active: bool = edgy.BooleanField(default=True)
    first_name: str = edgy.CharField(max_length=50, null=True)
    last_name: str = edgy.CharField(max_length=50, null=True)
    email: str = edgy.EmailField(max_lengh=100)
    password: str = edgy.CharField(max_length=1000, null=True)


@Model()
class Profile(BaseModel):
    user: User = edgy.ForeignKey(User, on_delete=edgy.CASCADE)
