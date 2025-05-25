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

VALID_SIZE_TYPES = [
    "PP",
    "P",
    "M",
    "G",
    "GG",
]

class SizeType(str, Enum):
    tam_pp = "PP"
    tam_P = "P"
    tam_M = "M"
    tam_G = "G"
    tam_GG = "GG"

VALID_COLOR_TYPES = [
    "amarelo",
    "azul",
    "bege",
    "branco",
    "bronze",
    "ciano",
    "cinza",
    "laranja",
    "lilás",
    "marrom",
    "preto",
    "rosa",
    "roxo",
    "verde",
    "vermelho",
]

    
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

VALID_CATEGORY_TYPES = [
    "Masculino",
    "Feminino",
    "Menina",
    "Menino",
]
    
class CategoryType(str, Enum):
    masc = "Masculino"
    fem = "Feminino"
    k_fem = "Menina"
    k_masc = "Menino"

VALID_SECTION_TYPES = [
    "Blusas",
    "Calças",
    "Vestidos",
    "Blusas",
    "Shorts",
    "Blusas"
]
    
class SectionType(str, Enum):
    Blusas = "Blusas"
    Calças = "Calças"
    Vestidos = "Vestidos"
    Calçados = "Blusas"
    Shorts = "Shorts"
    Acessórios = "Blusas"

VALID_STATUS_TYPES = [
    "Em andamento",
    "Pagamento confirmado",
    "Preparando para a entrega",
    "Enviado para a entrega",
    "Entregue",
    "A caminho",
    "Cancelado",
    "Solicitado reembolso",
]

class StatusType(str, Enum):
    andamento = "Em andamento"
    pagamentook = "Pagamento confirmado"
    preparando = "Preparando para a entrega"
    enviado = "Enviado para a entrega"
    entregue = "Entregue"
    acaminho = "A caminho"
    cancelado = "Cancelado"
    reembolso = "Solicitado reembolso"

VALID_PAYMENT_TYPES = [
    "Crédito",
    "Débito",
    "Pix",
    "Boleto",
]
    
class PaymentType(str, Enum):
    credito = "Crédito"
    debito = "Débito"
    pix = "Pix"
    boleto = "Boleto"