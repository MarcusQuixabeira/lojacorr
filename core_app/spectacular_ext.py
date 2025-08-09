from drf_spectacular.extensions import OpenApiAuthenticationExtension

class InsuredJWTScheme(OpenApiAuthenticationExtension):
    target_class = 'core_app.auth.InsuredJWTAuthentication'
    name = 'insuredJWT' 

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT Bearer token. Use: Authorization: Bearer <access_token>',
        }
