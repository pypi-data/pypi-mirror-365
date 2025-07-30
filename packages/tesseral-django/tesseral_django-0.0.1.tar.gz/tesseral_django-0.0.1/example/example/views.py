from django.http import JsonResponse
from tesseral_django import (
    require_auth,
    access_token_claims,
    credentials_type,
    organization_id,
)


@require_auth
def protected_view(request):
    return JsonResponse(
        {
            "type": credentials_type(request),
            "org_id": organization_id(request),
            "claims": access_token_claims(request).dict(),
        }
    )
