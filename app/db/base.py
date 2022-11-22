# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.fb_comment import FbComment  # noqa
from app.models.fb_post import FbPost  # noqa
from app.models.news import News  # noqa
from app.models.user import User  # noqa
