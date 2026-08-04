"""
用户认证 API 路由
"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    require_admin,
)
from database import get_db
from models import User, UserRole

router = APIRouter(prefix="/api/auth", tags=["认证"])


# ====== 请求/响应模型 ======

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    display_name: str = Field(default="", max_length=64)
    phone: str = Field(default="", max_length=20)
    invite_code: str = Field(default="")  # 邀请码


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    phone: str
    role: str
    created_at: str | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ====== 接口 ======

@router.post("/register", summary="用户注册")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    # 简单邀请码机制（可在 config 中配置复杂逻辑）
    valid_codes = ["scenic2024", "invest888", ""]
    # 第一个注册的用户自动成为管理员
    user_count = db.query(User).count()
    role = UserRole.ADMIN if user_count == 0 else UserRole.VIEWER

    user = User(
        username=req.username,
        password_hash=hash_password(req.password),
        display_name=req.display_name or req.username,
        phone=req.phone,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "注册成功", "user_id": user.id}


@router.post("/login", summary="用户登录")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()

    # 生成 token
    token = create_access_token({"sub": str(user.id), "role": user.role.value})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "phone": user.phone,
            "role": user.role.value,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    }


@router.get("/me", summary="获取当前用户信息")
def get_me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "phone": user.phone,
        "role": user.role.value,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
    }


@router.get("/users", summary="用户列表（管理员）")
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return {
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "display_name": u.display_name,
                "role": u.role.value,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in users
        ],
        "total": len(users),
    }


@router.put("/users/{user_id}/role", summary="修改用户角色（管理员）")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if role not in [r.value for r in UserRole]:
        raise HTTPException(status_code=400, detail="无效的角色")
    user.role = UserRole(role)
    db.commit()
    return {"message": "角色更新成功"}
