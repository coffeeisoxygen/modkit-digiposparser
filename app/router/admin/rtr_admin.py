from app.dependencies.dep_admin import get_admin_service, get_token_service
from app.exceptions.exceptions import AuthenticationFailedError, InvalidTokenError
from app.schemas.sch_token import AdminLoginRequest, Token
from app.service.token.srv_token import TokenService
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/adm", tags=["Admin"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/adm/login")


@router.post("/login", response_model=Token)
async def login_admin(
    form_data: AdminLoginRequest = Body(...),
    admin_service=Depends(get_admin_service),  # noqa: ANN001
) -> dict:
    """Handle admin login and return JWT token.

    Parameters
    ----------
    form_data : AdminLoginRequest
        Login credentials.
    admin_service : AdminService
        Service for admin authentication.

    Returns:
    -------
    dict
        JWT token and token type.

    Raises:
    ------
    HTTPException
        If authentication fails.
    """
    try:
        token = await admin_service.login_admin(form_data.username, form_data.password)
    except AuthenticationFailedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e
    return {"access_token": token, "token_type": "bearer"}


def get_current_admin(
    token: str = Depends(oauth2_scheme),
    token_service: TokenService = Depends(get_token_service),
) -> dict:
    """Validate JWT token and return admin payload.

    Parameters
    ----------
    token : str
        JWT token from request.
    token_service : TokenService
        Service for token decoding.

    Returns:
    -------
    dict
        Decoded token payload.

    Raises:
    ------
    HTTPException
        If token is invalid or user is not admin.
    """
    try:
        payload = token_service.decode_token(token)
        if not payload.get("is_superuser", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required",
            )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        ) from e
    return payload


@router.get("/users/me")
async def read_current_admin(payload: dict = Depends(get_current_admin)) -> dict:
    """Get current admin user info.

    Parameters
    ----------
    payload : dict
        Decoded JWT payload.

    Returns:
    -------
    dict
        Admin user info.
    """
    return {"username": payload["username"], "admin": True}
