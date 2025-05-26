from enum import Enum

VALID_USER_TYPES = [
    "administrador",
    "gerente",
    "vendedor",
    "marketing",
    "estoquista",
    "atendente"
]

class UserType(str, Enum):
    administrador = "administrador"
    gerente = "gerente"
    vendedor = "vendedor"
    marketing = "marketing"
    estoquista = "estoquista"
    atendente = "atendente"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None




VALID_SIZE_TYPES = [
    "pp",
    "p",
    "m",
    "g",
    "gg",
]

class SizeType(str, Enum):
    tam_pp = "pp"
    tam_p = "p"
    tam_m = "m"
    tam_g = "g"
    tam_gg = "gg"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None



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
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None




VALID_CATEGORY_TYPES = [
    "masculino",
    "feminino",
    "menina",
    "menino",
]

class CategoryType(str, Enum):
    masc = "masculino"
    fem = "feminino"
    k_fem = "menina"
    k_masc = "menino"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None



VALID_SECTION_TYPES = [
    "blusas",
    "calças",
    "vestidos",
    "calçados",
    "shorts",
    "acessórios"
]

class SectionType(str, Enum):
    blusas = "blusas"
    calças = "calças"
    vestidos = "vestidos"
    calçados = "calçados"
    shorts = "shorts"
    acessórios = "acessórios"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None




VALID_STATUS_TYPES = [
    "em andamento",
    "pagamento confirmado",
    "preparando entrega",
    "entregue",
    "a caminho",
    "cancelado",
    "solicitado reembolso",
    "reembolsado"
]

class StatusType(str, Enum):
    andamento = "em andamento"
    pagamentook = "pagamento confirmado"
    preparando = "preparando para a entrega"
    enviado = "enviado para a entrega"
    entregue = "entregue"
    acaminho = "a caminho"
    cancelado = "cancelado"
    reembolso = "solicitado reembolso"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None



VALID_PAYMENT_TYPES = [
    "crédito",
    "débito",
    "pix",
    "boleto",
]

class PaymentType(str, Enum):
    credito = "crédito"
    debito = "débito"
    pix = "pix"
    boleto = "boleto"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            value = value.lower()
            for member in cls:
                if member.value == value:
                    return member
        return None