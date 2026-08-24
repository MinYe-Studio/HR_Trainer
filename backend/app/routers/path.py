"""个性化学习路径路由。

默认顺序（sort_order）：招聘→绩效→薪酬→员工关系→培训→劳动法
用户可通过 PUT 自定义模块学习顺序（保存 6 个模块 code 的排列）。
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(prefix="/learning-path", tags=["学习路径"])


def _default_codes(db: Session) -> list[str]:
    mods = (
        db.query(models.SkillModule)
        .order_by(models.SkillModule.sort_order)
        .all()
    )
    return [m.code for m in mods]


@router.get("")
def get_learning_path(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取用户学习路径（自定义或默认）。"""
    user_path = current_user.learning_path or []
    codes = user_path if user_path else _default_codes(db)
    return {"module_codes": codes, "customized": bool(user_path)}


@router.put("")
def set_learning_path(
    payload: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """保存用户自定义学习路径。"""
    codes = payload.get("module_codes")
    if not isinstance(codes, list) or not codes:
        raise HTTPException(status_code=400, detail="module_codes 不能为空")

    all_codes = {m.code for m in db.query(models.SkillModule).all()}
    if set(codes) != all_codes or len(codes) != len(all_codes):
        raise HTTPException(status_code=400, detail="学习路径必须包含全部 6 个模块且不重复")

    current_user.learning_path = codes
    db.commit()
    return {"module_codes": codes, "customized": True}
