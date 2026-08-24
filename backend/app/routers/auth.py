"""认证路由：注册 / 登录 / 当前用户。"""
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..utils import auth as auth_utils

router = APIRouter(prefix="/auth", tags=["认证"])


def get_current_user(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
) -> models.User:
    """从 Authorization: Bearer <token> 解析当前用户。"""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    payload = auth_utils.decode_token(authorization.removeprefix("Bearer "))
    if not payload:
        raise HTTPException(status_code=401, detail="登录已失效，请重新登录")
    user = db.get(models.User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user


@router.post("/register", response_model=schemas.AuthResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.strip()
    if not username or len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="用户名不能为空，密码至少 6 位")
    if db.query(models.User).filter(models.User.username == username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = models.User(
        username=username,
        password_hash=auth_utils.hash_password(payload.password),
        nickname=payload.nickname.strip() or username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.AuthResponse(
        token=auth_utils.create_token(user.id, user.username),
        user=schemas.UserOut.model_validate(user),
    )


@router.post("/login", response_model=schemas.AuthResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.username == payload.username.strip())
        .first()
    )
    if not user or not auth_utils.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return schemas.AuthResponse(
        token=auth_utils.create_token(user.id, user.username),
        user=schemas.UserOut.model_validate(user),
    )


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
