from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from jwt import decode as jwt_decode, ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from asgiref.sync import sync_to_async
from apps.custom_auth.identity_principal import IdentityPrincipal
from apps.jobs.domain.entities.company import Company

class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()

        if not query_string:
            scope['user'] = AnonymousUser()
            return await super().__call__(scope, receive, send)

        try:            # Parsear el query_string
            params = dict(item.split('=', 1) for item in query_string.split('&') if '=' in item)
            token = params.get('token', None)

            if token:
                # Validar el token con SimpleJWT
                UntypedToken(token)

                # Decodificar el token y obtener el usuario
                payload = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                
                # Determinar si es un usuario o una empresa
                user_id = payload.get('user_id') or payload.get('sub')
                if user_id:
                    scope['user'] = IdentityPrincipal(
                        id=str(user_id),
                        username=str(payload.get('email') or payload.get('username') or ''),
                    )
                elif 'company_id' in payload:
                    company = await sync_to_async(Company.objects.get)(id=payload['company_id'])
                    scope['user'] = company
                else:
                    scope['user'] = AnonymousUser()
            else:
                scope['user'] = AnonymousUser()

        except ExpiredSignatureError:
            print("Token expirado.")
            scope['user'] = AnonymousUser()
        except InvalidTokenError:
            print("Token inválido.")
            scope['user'] = AnonymousUser()
        except Exception as e:
            print(f"Error al procesar el token: {e}")
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)
