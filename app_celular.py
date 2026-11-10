import streamlit as st

# Configuração da página para celular
st.set_page_config(page_title="Precificador Mestre", page_icon="📊", layout="centered")

st.title("📊 Precificador Mestre")
st.write("PS & Acrílico — Balcão e Internet")

# 1. VALORES OPERACIONAIS PADRÃO (Memória)
if 'valores' not in st.session_state:
    st.session_state.valores = {
        "chapa_ps1mm": 43.00, "chapa_ps2mm": 93.00,
        "chapa_acrilico1mm": 140.00, "chapa_acrilico2mm": 210.00, "chapa_acrilico3mm": 310.00,
        "uv_m2": 12.00, "laser_min": 0.50, "dobra_unidade": 0.30,
        "setup_ps": 5.00, "setup_acrilico": 10.00
    }

# TAXAS FIXAS
ML_COMISSAO = 0.14
ML_TAXA_FIXA = 7.00
SH_COMISSAO = 0.20
SH_TAXA_FIXA = 4.00

# Painel de Edição de Custos Oculto (Estilo sanfona)
with st.expander("⚙️ Ajustar Custos de Materiais"):
    st.session_state.valores["chapa_ps1mm"] = st.number_input("Chapa PS 1mm (R$)", value=st.session_state.valores["chapa_ps1mm"])
    st.session_state.valores["chapa_ps2mm"] = st.number_input("Chapa PS 2mm (R$)", value=st.session_state.valores["chapa_ps2mm"])
    st.session_state.valores["chapa_acrilico1mm"] = st.number_input("Acrílico 1mm (R$)", value=st.session_state.valores["chapa_acrilico1mm"])
    st.session_state.valores["chapa_acrilico2mm"] = st.number_input("Acrílico 2mm (R$)", value=st.session_state.valores["chapa_acrilico2mm"])
    st.session_state.valores["chapa_acrilico3mm"] = st.number_input("Acrílico 3mm (R$)", value=st.session_state.valores["chapa_acrilico3mm"])
    st.session_state.valores["uv_m2"] = st.number_input("Impressão UV por m² (R$)", value=st.session_state.valores["uv_m2"])
    st.session_state.valores["laser_min"] = st.number_input("Minuto da Laser (R$)", value=st.session_state.valores["laser_min"])
    st.session_state.valores["dobra_unidade"] = st.number_input("Custo por Dobra (R$)", value=st.session_state.valores["dobra_unidade"])
    st.session_state.valores["setup_ps"] = st.number_input("Setup Mínimo PS (R$)", value=st.session_state.valores["setup_ps"])
    st.session_state.valores["setup_acrilico"] = st.number_input("Setup Mínimo Acrílico (R$)", value=st.session_state.valores["setup_acrilico"])

st.markdown("---")

# 2. ENTRADA DE DADOS DO PRODUTO
mat = st.radio("Selecione o Material:", ["PS", "Acrílico (Com Dobra)"], horizontal=True)

col1, col2 = st.columns(2)
with col1:
    largura_cm = st.number_input("Largura (cm):", value=30.0, step=1.0)
with col2:
    altura_cm = st.number_input("Altura (cm):", value=10.0, step=1.0)

if mat == "PS":
    esp = st.selectbox("Espessura:", [1, 2], format_func=lambda x: f"{x}mm")
    dobras = 0
else:
    esp = st.selectbox("Espessura:", [1, 2, 3], format_func=lambda x: f"{x}mm")
    dobras = st.number_input("Nº de Dobras (vincos):", value=0, step=1)

impressao = st.selectbox("Terá Impressão UV?", ["SIM", "NÃO"])
margem_p = st.number_input("Margem de Lucro Desejada (%):", value=40.0, step=5.0) / 100.0

# 3. CÁLCULO DA ENGENHARIA DE CUSTOS
area_peca = (largura_cm / 100.0) * (altura_cm / 100.0)
perimetro_peca = ((largura_cm / 100.0) * 2) + ((altura_cm / 100.0) * 2)

if mat == "PS":
    fita_custo = 0.40 if esp == 1 else 0.70
    if area_peca > 0.1: fita_custo *= 1.5
    custo_chapa = st.session_state.valores["chapa_ps1mm"] if esp == 1 else st.session_state.valores["chapa_ps2mm"]
    velocidade_laser = 3.0 if esp == 1 else 2.1
    custo_adicional = fita_custo
    setup_local = st.session_state.valores["setup_ps"]
else:
    if esp == 1: custo_chapa, velocidade_laser = st.session_state.valores["chapa_acrilico1mm"], 4.0
    elif esp == 2: custo_chapa, velocidade_laser = st.session_state.valores["chapa_acrilico2mm"], 1.8
    else: custo_chapa, velocidade_laser = st.session_state.valores["chapa_acrilico3mm"], 1.2
    custo_adicional = dobras * st.session_state.valores["dobra_unidade"]
    setup_local = st.session_state.valores["setup_acrilico"]

custo_material_final = area_peca * (custo_chapa / 2.0)
custo_laser_final = (perimetro_peca / velocidade_laser) * st.session_state.valores["laser_min"]
custo_impressao_final = area_peca * st.session_state.valores["uv_m2"] if impressao == "SIM" else 0.0

custo_total_fabricacao = custo_material_final + custo_laser_final + custo_impressao_final + custo_adicional

st.metric(label="💰 Custo Real de Fabricação", value=f"R$ {custo_total_fabricacao:.2f}")

# 4. PROCESSAMENTO DAS MARGENS PARA A TABELA
margens = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]
if margem_p not in margens:
    margens.append(margem_p)
margens.sort()

dados_tabela = []
for m in margens:
    p_balcao = (custo_total_fabricacao + setup_local) / (1 - m)
    l_balcao = p_balcao * m
    
    p_sh = (custo_total_fabricacao + SH_TAXA_FIXA) / (1 - SH_COMISSAO - m) if (1 - SH_COMISSAO - m) > 0 else 0
    l_sh = p_sh * m
    
    p_ml = (custo_total_fabricacao + ML_TAXA_FIXA) / (1 - ML_COMISSAO - m) if (1 - ML_COMISSAO - m) > 0 else 0
    l_ml = p_ml * m
    
    prefixo = "⭐ " if m == margem_p else ""
    
    dados_tabela.append({
        "Margem": f"{prefixo}{int(m*100)}%",
        "Venda Balcão": f"R$ {p_balcao:.2f}",
        "Lucro Balcão": f"R$ {l_balcao:.2f}",
        "Venda Shopee": f"R$ {p_sh:.2f}" if p_sh > 0 else "Inviável",
        "Lucro Shopee": f"R$ {l_sh:.2f}" if p_sh > 0 else "-",
        "Venda ML": f"R$ {p_ml:.2f}" if p_ml > 0 else "Inviável",
        "Lucro ML": f"R$ {l_ml:.2f}" if p_ml > 0 else "-"
    })

st.write("### 📋 Tabela Comparativa de Preços")
st.dataframe(dados_tabela, use_container_width=True)
st.caption("As linhas marcadas com ⭐ representam a sua margem personalizada.")