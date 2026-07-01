from fastapi import APIRouter, HTTPException, Depends, Header, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, engine, Base
from sqlalchemy import Column, Integer, String, Text, BigInteger, Boolean, DateTime
from sqlalchemy.sql import func

# ── Player model (same DB as trx-bot, isolated table) ──────────────
class Player(Base):
    __tablename__ = "players"

    id         = Column(Integer, primary_key=True, index=True)
    username   = Column(String(64), unique=True, index=True)
    password   = Column(String(64))
    nickname   = Column(String(64), default="")
    avatar     = Column(String(32), default="🎮")
    coins      = Column(Integer, default=1000)
    gems       = Column(Integer, default=50)
    is_vip     = Column(Boolean, default=False)
    token      = Column(String(64), default="", index=True)
    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return dict(
            id=self.id, username=self.username, nickname=self.nickname,
            avatar=self.avatar, coins=self.coins, gems=self.gems, is_vip=self.is_vip,
        )


def make_token(username: str) -> str:
    import hashlib, secrets
    return hashlib.sha256(f"{username}{secrets.token_hex(16)}".encode()).hexdigest()[:48]


def hash_pwd(pwd: str) -> str:
    import hashlib
    return hashlib.sha256((pwd + "gv_salt_2024").encode()).hexdigest()[:32]


def get_current_player(
    db: Session = Depends(get_db),
    x_player_token: str = Header(None, alias="X-Player-Token"),
    authorization: str = Header(None),
):
    # 支持 X-Player-Token 或 Authorization: Bearer
    token = x_player_token
    if not token and authorization:
        if authorization.startswith("Bearer "):
            token = authorization[7:]
    if not token:
        raise HTTPException(401, "未登录")
    player = db.query(Player).filter(Player.token == token).first()
    if not player:
        raise HTTPException(401, "登录已过期，请重新登录")
    return player


# ── Schemas ─────────────────────────────────────────────────────────
class LoginResp(BaseModel):
    ok: bool = True
    token: str
    player: dict


# ── Router ──────────────────────────────────────────────────────────
router = APIRouter(prefix="/api/auth", tags=["GameVault Auth"])


@router.post("/register", response_model=LoginResp)
def register(
    username: str = Form(...),
    password: str  = Form(...),
    db: Session = Depends(get_db),
):
    import time as _time
    if len(username) < 3 or len(username) > 32:
        raise HTTPException(400, "用户名需3-32个字符")
    if len(password) < 6:
        raise HTTPException(400, "密码至少6位")
    existing = db.query(Player).filter(Player.username == username).first()
    if existing:
        raise HTTPException(400, "用户名已被占用")

    player = Player(
        username=username,
        password=hash_pwd(password),
        nickname=username[:12],
        coins=1000,
        gems=50,
        token=make_token(username),
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return LoginResp(ok=True, token=player.token, player=player.to_dict())


@router.post("/login", response_model=LoginResp)
def login(
    username: str = Form(...),
    password: str  = Form(...),
    db: Session = Depends(get_db),
):
    player = db.query(Player).filter(Player.username == username).first()
    if not player or player.password != hash_pwd(password):
        raise HTTPException(401, "用户名或密码错误")
    player.token = make_token(username)
    db.commit()
    db.refresh(player)
    return LoginResp(ok=True, token=player.token, player=player.to_dict())


@router.get("/me")
def me(player: Player = Depends(get_current_player)):
    return {"player": player.to_dict()}


@router.get("/notifications")
def notifications(player: Player = Depends(get_current_player)):
    import time as _time
    return {
        "notifications": [
            {"id": 1, "type": "system", "title": "欢迎回来！",
             "content": f"你好 {player.nickname}，欢迎进入 GameVault 游戏世界 🎮",
             "time": int(_time.time()), "read": False},
            {"id": 2, "type": "event", "title": "新游戏上线",
             "content": "多人联机大厅已开放，叫上朋友一起来玩！",
             "time": int(_time.time()) - 3600, "read": False},
            {"id": 3, "type": "activity", "title": "充值返利活动",
             "content": "首次充值享双倍金币，限时7天！",
             "time": int(_time.time()) - 7200, "read": True},
        ],
        "count": 2,
    }


# ── Profile router ───────────────────────────────────────────────────
profile_router = APIRouter(prefix="/api", tags=["GameVault Profile"])


@profile_router.get("/profile")
def get_profile(player: Player = Depends(get_current_player)):
    return {"player": player.to_dict()}


@profile_router.post("/profile")
def update_profile(
    nickname: str  = Form(None),
    avatar:   str   = Form(None),
    db: Session = Depends(get_db),
    player: Player = Depends(get_current_player),
):
    if nickname:
        player.nickname = nickname[:12]
    if avatar:
        player.avatar = avatar[:32]
    db.commit()
    return {"ok": True, "player": player.to_dict()} 
