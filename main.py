from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from auth import create_token, get_current_user, verify_password
from database import find_user, initialize_database

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield

app = FastAPI(
    title="API de autenticación JWT - Unidad IV",
    description="Actividad de Lenguajes de Programación: rutas públicas y protegidas.",
    version="1.0.0",
    lifespan=lifespan,
)

@app.post("/login", tags=["Autenticación"])
def login(form: OAuth2PasswordRequestForm = Depends()) -> dict[str, str]:
    user = find_user(form.username)
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_token({"sub": user["email"], "role": user["role"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/publico", tags=["Rutas"])
def public_route() -> dict[str, str]:
    return {"msg": "Cualquiera puede ver esto"}

@app.get("/privado", tags=["Rutas"])
def private_route(user: dict = Depends(get_current_user)) -> dict[str, str]:
    return {"msg": f"Hola {user['sub']}, rol: {user['role']}"}

@app.get("/admin", tags=["Rutas"])
def admin_route(user: dict = Depends(get_current_user)) -> dict[str, str]:
    if user["role"] != "profesor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo para profesores",
        )
    return {"msg": "Panel de administración"}