from fastapi import Depends, HTTPException, status
from typing import List
from ..models.model_user import User
from ..utils.dependencies import get_current_user

def require_user_type(allowed_types: List[str]):
    def permission_dependency(current_user: User = Depends(require_user_type(["", ""]))):
        if current_user.usr_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada para o tipo de usuário '{current_user.usr_type}'."
            )
        return current_user
    return permission_dependency
