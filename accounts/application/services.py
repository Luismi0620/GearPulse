from django.core.exceptions import ValidationError as DjangoValidationError

from accounts.models import User
from common.exceptions import ConflictError


class UserService:
    """Orchestrates user registration. Keeps validation/business rules out of views."""

    def register_user(self, email: str, role: str) -> User:
        email = (email or "").strip().lower()
        role = (role or User.Role.ATHLETE).strip().lower()

        if role not in User.Role.values:
            raise ValueError(f"invalid role: use one of {User.Role.values}")
        if User.objects.filter(email=email).exists():
            raise ConflictError(f"user with email '{email}' already exists")

        # Model-level business validation (User.clean()) is actually invoked here,
        # not just declared: full_clean() runs field validators + clean() before
        # anything is persisted.
        user = User(email=email, role=role)
        try:
            user.full_clean()
        except DjangoValidationError as exc:
            raise ValueError("; ".join(exc.messages)) from exc

        user.save()
        return user
