from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.core.config import settings
from backend.database.database import get_db
from backend.database.models import User
from backend.services.auth_service import hash_password, verify_password, create_access_token, get_user
from backend.services.audit_service import AuditService

router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
audit = AuditService()
SESSION_COOKIE = "jroc_session"

@router.post("/bootstrap-chairman")
def bootstrap_chairman(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        raise HTTPException(403, "Chairman bootstrap already completed")
    user = User(username=username, password_hash=hash_password(password), role="CHAIRMAN")
    db.add(user)
    db.commit()
    db.refresh(user)
    audit.record(db, "CHAIRMAN_CREATED", user.id, "user:" + str(user.id), "CREATE")
    return {"id": user.id, "username": user.username, "role": user.role}

@router.post("/login")
def login(response: Response, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user(db, form.username)
    if not user or not verify_password(form.password, user.password_hash):
        audit.record(db, "LOGIN_FAILED", None, "user:" + form.username, "LOGIN", False)
        raise HTTPException(401, "Invalid credentials")
    token = create_access_token(user)
    audit.record(db, "LOGIN_SUCCESS", user.id, "user:" + str(user.id), "LOGIN")
    response.set_cookie(
        key=SESSION_COOKIE,
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/",
        max_age=settings.access_token_minutes * 60,
    )
    return {"access_token": token, "token_type": "bearer", "role": user.role, "username": user.username}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}

@router.get("/me")
def me(request: Request, token: str | None = Depends(oauth2), db: Session = Depends(get_db)):
    user = current_user(request=request, token=token, db=db)
    return {"id": user.id, "username": user.username, "role": user.role}

def current_user(request: Request, token: str | None = Depends(oauth2), db: Session = Depends(get_db)):
    request_token = token or request.cookies.get(SESSION_COOKIE)
    if not request_token:
        raise HTTPException(401, "Authentication required")
    try:
        payload = jwt.decode(request_token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid or expired token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(401, "User not found")
    return user
