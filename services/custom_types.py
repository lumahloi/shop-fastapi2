from enum import Enum

VALID_USER_TYPES = [
    "Administrador",
    "Gerente",
    "Vendedor",
    "Marketing",
    "Estoquista",
    "Atendente"
]

class UserType(str, Enum):
    administrador = "Administrador"
    gerente = "Gerente"
    vendedor = "Vendedor"
    marketing = "Marketing"
    estoquista = "Estoquista"
    atendente = "Atendente"

class SizeType(str, Enum):
    tam_pp = "PP"
    tam_P = "P"
    tam_M = "M"
    tam_G = "G"
    tam_GG = "GG"
    
class ColorType(str, Enum):
    color_amarelo = "amarelo"
    color_azul = "azul"
    color_bege = "bege"
    color_branco = "branco"
    color_bronze = "bronze"
    color_ciano = "ciano"
    color_cinza = "cinza"
    color_laranja = "laranja"
    color_lilás = "lilás"
    color_marrom = "marrom"
    color_preto = "preto"
    color_rosa = "rosa"
    color_roxo = "roxo"
    color_verde = "verde"
    color_vermelho = "vermelho"
    
class CategoryType(str, Enum):
    masc = "Masculino"
    fem = "Feminino"
    k_fem = "Menina"
    k_masc = "Menino"
    
class SectionType(str, Enum):
    Blusas = "Blusas"
    Calças = "Calças"
    Vestidos = "Vestidos"
    Calçados = "Blusas"
    Shorts = "Shorts"
    Acessórios = "Blusas"

class StatusType(str, Enum):
    andamento = "Em andamento"
    pagamentook = "Pagamento confirmado"
    preparando = "Preparando para a entrega"
    enviado = "Enviado para a entrega"
    entregue = "Entregue"
    acaminho = "A caminho"
    cancelado = "Cancelado"
    reembolso = "Solicitado reembolso"
    
class PaymentType(str, Enum):
    credito = "Crédito"
    debito = "Débito"
    pix = "Pix"
    boleto = "Boleto"