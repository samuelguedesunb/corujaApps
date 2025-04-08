import sqlite3
import pandas as pd
from cadastro import InfoRegistro
from cadastro_mp import InfoMP

mp = InfoMP(
    nome="Novo Nome",
    data="07-04-2025",
    endereco="Gama",
    situacao="Pendente",
    fotos = "/images/uploads/teste44.jpg"
)
atualizacao_mp = mp.atualizar_mp_bd(2)

# Atualizando um registro específico (ID = 2)
sucesso, msg = mp.atualizar_mp_bd(id_mp=2)

if sucesso:
    print(f"✅ {msg} - ID atualizado: {mp.id_mp}")
else:
    print(f"❌ {msg}")