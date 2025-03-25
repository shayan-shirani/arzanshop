from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken, RefreshToken

class JwtService:
    @staticmethod
    def token_blacklist(user):
        try:
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)
        except Exception as e:
            return {'detail': str(e)}

    @staticmethod
    def logout(refresh_token):
        token = RefreshToken(refresh_token)
        token.blacklist()

    @staticmethod
    def generate_token(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }