from fastapi import APIRouter, Depends, HTTPException, status
from app.models.user import UserCreate, UserResponse, UserLogin, Token
from app.controllers.user_controller import UserController
from app.db.client import get_supabase_client
from app.core.security import verify_password, create_access_token
from uuid import UUID

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    return await UserController.create_user(user)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    client = get_supabase_client()
    response = client.table("users").select("*").eq("email", credentials.email).execute()
    
    if not response.data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos")
    
    user_data = response.data[0]
    if not user_data.get("hashed_password"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos")
        
    if not verify_password(credentials.password, user_data["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="E-mail ou senha incorretos")
    
    access_token = create_access_token(data={"sub": str(user_data["id"])})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user_data["id"]}

@router.post("/refresh", response_model=Token)
async def refresh_token(token: Token):
    # Here we should verify the old token (even if expired, we could allow refresh if we track refresh tokens)
    # But for simplicity, we'll just require the frontend to pass the user ID or we decode it.
    # A standard approach is to let the user login again, or if they have a valid token, they can refresh.
    # Since the instruction says "Renew the JWT in the frontend on each application startup", 
    # we can decode the token here (ignoring expiration) and issue a new one if it's validly signed.
    
    import jwt
    from app.core.security import SECRET_KEY, ALGORITHM
    try:
        payload = jwt.decode(token.access_token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
            
        client = get_supabase_client()
        response = client.table("users").select("id").eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=401, detail="Usuário não encontrado")
            
        new_access_token = create_access_token(data={"sub": user_id})
        return {"access_token": new_access_token, "token_type": "bearer", "user_id": UUID(user_id)}
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falha ao validar token para renovação")
