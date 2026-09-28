import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Header, HTTPException, status

from conecta_banco import consultar_usuario

# A chave vem de uma variável de ambiente. Se não estiver definida, uma chave
# aleatória é criada a cada execução (os tokens deixam de valer ao reiniciar).
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
ALGORITMO = "HS256"
EXPIRA_EM_MINUTOS = 60


def gerar_token(user, senha):
    usuario_no_banco = consultar_usuario(user, senha)
    if usuario_no_banco is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="USUÁRIO OU SENHA INVÁLIDOS.",
        )
    dados = {
        "user": usuario_no_banco,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRA_EM_MINUTOS),
    }
    return jwt.encode(dados, SECRET_KEY, algorithm=ALGORITMO)


def verificar_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITMO])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TOKEN EXPIRADO.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TOKEN INVÁLIDO.",
        )


def usuario_autenticado(token: str = Header()):
    """Dependência do FastAPI: exige o header 'token' e devolve o usuário."""
    return verificar_token(token)["user"]
