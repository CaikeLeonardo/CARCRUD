from pydantic import BaseModel, Field


class Carro(BaseModel):
    placa: str
    marca: str
    modelo: str
    ano: int
    status: str
    valor_compra: float = Field(gt=0)


class Despesa(BaseModel):
    id_veiculo: int
    titulo: str
    valor_gasto: float = Field(gt=0)
    descricao: str


class Venda(BaseModel):
    id_veiculo: int
    valor_vendido: float = Field(gt=0)
    nome_comprador: str


class Usuario(BaseModel):
    user: str
    senha: str
