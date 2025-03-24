from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken

class JwtService:
    @staticmethod
    def token_blacklist(user):
        try:
            tokens = OutstandingToken.objects.filter(user=user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)
        except Exception as e:
            return {'detail': str(e)}
