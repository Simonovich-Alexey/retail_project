from rest_framework_simplejwt.tokens import RefreshToken


class Utils:
    @staticmethod
    def get_tokens_for_email(user):
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }