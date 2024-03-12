from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailInsteadOfUsernameBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None or password is None:
            return

        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
            return None
        else:
            if user.check_password(password):
                return user
        return None
