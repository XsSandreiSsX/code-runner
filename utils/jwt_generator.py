from datetime import datetime, timedelta, timezone

import jwt


def generate_internal_jwt(iss: str, jwt_secret: str, ttl: int = 30) -> str:
    """
    Generates a short-lived JWT token for internal service-to-service requests.

    This function is intended to be copied into any service that communicates
    with Code-runner. Each service uses its own secret key issued by Code-runner
    during registration. The token is used only inside a trusted infrastructure
    and should not be exposed publicly.

    How to use:
        - Copy this function into your service's utils.
        - Store jwt_secret in environment variables or a secure secret storage.
        Before sending a request to Codrunner, call the function and pass the
        token in the Authorization header:
        Authorization: Bearer <generated_token>

    Important:
        - Do not use this token for public endpoints or external clients.
        - Do not store or commit the secret in code or repositories.
        - If the secret is leaked, rotate the secret in Code-runner and update it
          in the service configuration.

    Args:
        iss (str): The service name as registered in Codrunner (e.g. "course-service").
        jwt_secret (str): The secret key issued to this service.
        ttl (int): Token lifetime in seconds. Default is 30.

    Returns:
        str: A signed JWT token.
    """

    now = datetime.now(timezone.utc)

    payload = {"iss": iss, "iat": now, "exp": now + timedelta(seconds=ttl)}

    return jwt.encode(payload, jwt_secret, algorithm="HS256")
