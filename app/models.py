import datetime

from tortoise import Model, fields

from fastapi_admin.models import AbstractAdminLog, AbstractPermission, AbstractRole, AbstractUser

from app.enums import Status


class UserSocial(AbstractUser):
    last_login = fields.DatetimeField(description="Last Login", default=datetime.datetime.now)
    avatar = fields.CharField(max_length=200, default="")
    intro = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}#{self.username}"

    def rowVariant(self) -> str:
        if not self.is_active:
            return "warning"
        return ""

    def cellVariants(self) -> dict:
        if self.is_active:
            return {
                "intro": "info",
            }
        return {}

    class PydanticMeta:
        computed = ("rowVariant", "cellVariants")
    class Meta:
        table = "user_admin"


class Permission(AbstractPermission):
    """
    must inheritance AbstractPermission
    """


class Role(AbstractRole):
    """
    must inheritance AbstractRole
    """


class AdminLog(AbstractAdminLog):
    """
    must inheritance AbstractAdminLog
    """


class FbComment(Model):
    """Sqlalchemy model"""

    __tablename__ = "fb_comment"
    comment_id = fields.CharField(max_length=300, pk=True)
    source = fields.CharField(max_length=300)
    reply_to = fields.CharField(max_length=300)
    text = fields.TextField()
    last_update = fields.DatetimeField()
    reactions = fields.IntField
    post_id = fields.CharField(max_length=300)
    source_url = fields.CharField(max_length=300)
    url = fields.CharField(max_length=300)
    create_date = fields.DatetimeField(auto_now_add=True)
    sentiment = fields.CharField(max_length=300)
    class Meta:
        table= "fb_comment"

# class Category(Model):
#     slug = fields.CharField(max_length=200)
#     name = fields.CharField(max_length=200)
#     created_at = fields.DatetimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.pk}#{self.name}"


# class Product(Model):
#     categories = fields.ManyToManyField("models.Category")
#     name = fields.CharField(max_length=50)
#     view_num = fields.IntField(description="View Num")
#     sort = fields.IntField()
#     is_reviewed = fields.BooleanField(description="Is Reviewed")
#     type = fields.IntEnumField(ProductType, description="Product Type")
#     image = fields.CharField(max_length=200)
#     body = fields.TextField()
#     created_at = fields.DatetimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.pk}#{self.name}"


class Config(Model):
    label = fields.CharField(max_length=200)
    key = fields.CharField(max_length=20)
    value = fields.JSONField()
    status: Status = fields.IntEnumField(Status, default=Status.on)

    def __str__(self):
        return f"{self.pk}#{self.label}"