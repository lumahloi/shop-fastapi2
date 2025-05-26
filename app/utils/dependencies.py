from fastapi import Depends, Header, HTTPException
from sqlmodel import Session, select
from ..utils.auth import decode_token
from ..models.model_user import User
from ..utils.session import get_session

def get_current_user(
    authorization: str = Header(...), 
    session: Session = Depends(get_session)
) -> User:
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token ausente ou mal formatado.")

    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    user_email = payload.get("sub")
    user = session.exec(select(User).where(User.usr_email == user_email)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado.")

    return user
