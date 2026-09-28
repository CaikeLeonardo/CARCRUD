from fastapi import Depends, FastAPI, HTTPException, status

from conecta_banco import (
    carro_existe,
    consultar_carro_especifico,
    consultar_carros,
    consultar_gasto_veiculo,
    criar_tabelas,
    gerar_total_gasto_veiculo,
    inserir_usuario,
    salvar_carro,
    salvar_despesa,
    vender_carro,
)
from gerador_token import gerar_token, usuario_autenticado
from models import Carro, Despesa, Usuario, Venda

app = FastAPI(
    title="CARCRUD",
    version="1.1",
    description=(
        "API para cadastrar veículos, despesas e vendas, e consultar o "
        "resumo financeiro de cada veículo. Projeto desenvolvido durante um "
        "curso de Python, revisado para corrigir falhas de segurança e bugs "
        "do código original."
    ),
    contact={
        "name": "Caike Leonardo",
        "url": "https://github.com/CaikeLeonardo",
        "email": "caikeleonardo9@gmail.com",
    },
)


@app.on_event("startup")
def startup():
    criar_tabelas()


# ---------- Autenticação ----------

@app.post(
    "/cadastrar_usuario",
    description="Cria um novo usuário e devolve o token de acesso.",
    summary="Cadastra um novo usuário.",
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_usuario(usuario: Usuario):
    try:
        inserir_usuario(usuario.user, usuario.senha)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="USUÁRIO JÁ EXISTE.",
        )
    return {"token": gerar_token(usuario.user, usuario.senha)}


@app.post(
    "/login",
    description="Autentica um usuário existente e devolve o token de acesso.",
    summary="Login.",
)
def login(usuario: Usuario):
    return {"token": gerar_token(usuario.user, usuario.senha)}


# ---------- Veículos ----------

@app.post(
    "/cadastrar_veiculo",
    description="Cadastra um novo veículo no banco de dados.",
    summary="Cadastra um novo veículo.",
    response_description="Confirmação do cadastro.",
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_veiculo(carro: Carro, usuario: str = Depends(usuario_autenticado)):
    salvo = salvar_carro(
        carro.placa,
        carro.marca,
        carro.ano,
        carro.modelo,
        carro.status,
        carro.valor_compra,
    )
    if not salvo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JÁ EXISTE UM VEÍCULO CADASTRADO COM ESSA PLACA.",
        )
    return {"mensagem": "CARRO CADASTRADO COM SUCESSO."}


@app.get(
    "/visualizar_veiculos",
    description="Mostra todos os veículos cadastrados, ou um veículo "
    "específico ao informar a placa.",
    summary="Mostra todos os veículos.",
    response_description="Veículos",
    status_code=status.HTTP_200_OK,
)
def visualizar_veiculos(placa: str = None):
    if placa is not None:
        return consultar_carro_especifico(placa)
    return consultar_carros()


@app.get(
    "/resumo_veiculo",
    description="Retorna dados do veículo, valor de compra e total gasto em despesas.",
    summary="Resumo financeiro de um veículo.",
    status_code=status.HTTP_200_OK,
)
def resumo_veiculo(id_veiculo: int, usuario: str = Depends(usuario_autenticado)):
    if not carro_existe(id_veiculo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VEÍCULO NÃO ENCONTRADO.",
        )
    return gerar_total_gasto_veiculo(id_veiculo)


# ---------- Despesas ----------

@app.post(
    "/cadastrar_despesa",
    description="Cadastra uma nova despesa no banco de dados.",
    summary="Cadastra uma nova despesa.",
    response_description="Nova despesa.",
    status_code=status.HTTP_201_CREATED,
)
def cadastrar_despesa(despesa: Despesa, usuario: str = Depends(usuario_autenticado)):
    if not carro_existe(despesa.id_veiculo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VEÍCULO NÃO ENCONTRADO.",
        )
    salvar_despesa(
        despesa.id_veiculo, despesa.titulo, despesa.valor_gasto, despesa.descricao
    )
    return {"mensagem": "DESPESA CADASTRADA COM SUCESSO."}


@app.get(
    "/consultar_despesas_veiculo",
    description="Consulta despesas de um veículo específico.",
    summary="Consulta as despesas de um veículo.",
    response_description="Despesas do veículo.",
    status_code=status.HTTP_200_OK,
)
def consultar_despesas_veiculo(id_veiculo: int):
    return consultar_gasto_veiculo(id_veiculo)


# ---------- Vendas ----------

@app.post(
    "/vender_veiculo",
    description="Registra a venda de um veículo e atualiza seu status.",
    summary="Registra uma venda.",
    status_code=status.HTTP_201_CREATED,
)
def vender_veiculo(venda: Venda, usuario: str = Depends(usuario_autenticado)):
    if not carro_existe(venda.id_veiculo):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VEÍCULO NÃO ENCONTRADO.",
        )
    vender_carro(venda.id_veiculo, venda.valor_vendido, venda.nome_comprador)
    return {"mensagem": "VENDA REGISTRADA COM SUCESSO."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
