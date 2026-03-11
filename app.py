import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="eNPS - Minha Empresa", page_icon="🛍️", layout="centered")

# 2. Configuração do "Banco de Dados" Local (Arquivo CSV)
ARQUIVO_DADOS = "dados_nps.csv"

def carregar_dados():
    # Verifica se o arquivo já existe. Se sim, carrega os dados. Se não, cria a estrutura vazia.
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=[
            "Data", "Nome", "Loja", "NPS_Geral", "Lideranca", 
            "Treinamento", "Autoavaliacao", "Avaliacao_Supervisor", "Feedback"
        ])

def salvar_dados(nova_linha):
    df = carregar_dados()
    # Adiciona a nova resposta na tabela
    df_nova = pd.DataFrame([nova_linha])
    df_final = pd.concat([df, df_nova], ignore_index=True)
    # Salva no arquivo local
    df_final.to_csv(ARQUIVO_DADOS, index=False)

# 3. Menu Lateral (Acesso Privado do Gestor)
st.sidebar.title("🔐 Acesso Restrito")
senha = st.sidebar.text_input("Digite a senha de administrador:", type="password")

# ==========================================
# TELA 1: ÁREA DO GESTOR (Se a senha estiver correta)
# ==========================================
if senha == "admin123": # Você pode alterar esta senha aqui
    st.title("📊 Gestão de eNPS")
    
    df = carregar_dados()
    
    if not df.empty:
        st.subheader("Filtros de Gestão")
        col_filtro1, col_filtro2 = st.columns(2)
        
        with col_filtro1:
            # Filtro por Loja
            lista_lojas = ["Todas as Lojas"] + df["Loja"].unique().tolist()
            loja_selecionada = st.selectbox("Filtrar por Loja:", lista_lojas)
        
        with col_filtro2:
            # Filtro por Nome (Baseado na loja selecionada)
            if loja_selecionada != "Todas as Lojas":
                df_filtrado_loja = df[df["Loja"] == loja_selecionada]
                lista_nomes = ["Todos os Colaboradores"] + df_filtrado_loja["Nome"].unique().tolist()
            else:
                lista_nomes = ["Todos os Colaboradores"] + df["Nome"].unique().tolist()
                
            nome_selecionado = st.selectbox("Filtrar por Colaborador:", lista_nomes)

        # Aplicando os filtros na tabela
        df_display = df.copy()
        if loja_selecionada != "Todas as Lojas":
            df_display = df_display[df_display["Loja"] == loja_selecionada]
        if nome_selecionado != "Todos os Colaboradores":
            df_display = df_display[df_display["Nome"] == nome_selecionado]

        # Calculando os Indicadores
        st.divider()
        st.subheader("Indicadores")
        
        notas = df_display["NPS_Geral"]
        total_respostas = len(notas)
        promotores = len(notas[notas >= 9])
        detratores = len(notas[notas <= 6])
        
        if total_respostas > 0:
            enps_score = ((promotores - detratores) / total_respostas) * 100
            
            # Caixas de destaque com os números
            met1, met2, met3 = st.columns(3)
            met1.metric("Score eNPS", f"{enps_score:.0f}", help="Varia de -100 a +100")
            met2.metric("Total de Respostas", total_respostas)
            met3.metric("Promotores (Nota 9-10)", promotores)
            
            # Gráfico visual das notas
            st.write("Distribuição das Notas (Geral)")
            st.bar_chart(notas.value_counts().sort_index())
            
            # Tabela detalhada
            st.subheader("📋 Detalhamento das Respostas")
            st.dataframe(df_display, use_container_width=True)
            
            # Botão para você baixar os dados em Excel se quiser
            csv_export = df_display.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar dados da tela atual",
                data=csv_export,
                file_name='dados_enps_lojas.csv',
                mime='text/csv',
            )
        else:
            st.warning("Nenhum dado encontrado para os filtros selecionados.")
            
    else:
        st.info("O banco de dados está vazio. Nenhuma resposta foi enviada ainda.")

# ==========================================
# TELA 2: FORMULÁRIO DO COLABORADOR (Padrão)
# ==========================================
else:
    if senha != "":
        st.sidebar.error("Senha incorreta.")
        
    st.title("💡 Pesquisa de Experiência")
    st.write("Queremos ouvir você! Sua opinião ajuda a construir um ambiente de trabalho cada vez melhor.")

    with st.form("form_nps"):
        st.subheader("Sua Identificação")
        nome_colaborador = st.text_input("Qual o seu nome?")
        loja_colaborador = st.selectbox("Qual a sua loja?", ["Loja Yubiso XV", "Loja Yubiso Marisa", "Loja Bazar", "Loja BALI", "Loja LINO", "Loja MYNO", "Loja Variedades SJP", "Loja AMORA", "Loja Jardim do Paraná", "Loja Armarinhos do Sul", "Loja AUBY"])

        
        st.subheader("Avaliação Geral")
        nps_score = st.slider("Em uma escala de 0 a 10, o quanto você recomendaria trabalhar nesta loja?", 0, 10, 10)
        
        st.subheader("Liderança e Suporte")
        nota_lideranca = st.slider("Como está sendo sua experiência com a liderança?", 0, 10, 10)
        nota_treinamento = st.slider("Como você avalia seu treinamento e suporte?", 0, 10, 10)
        
        st.subheader("Autoavaliação")
        nota_autoaval = st.slider("Como você avaliaria seu trabalho hoje?", 0, 10, 10)
        nota_supaval = st.slider("Como você acha que seu supervisor avaliaria seu trabalho?", 0, 10, 10)
        
        st.subheader("Comentários")
        feedback_texto = st.text_area("O que te motiva no dia a dia? Ou o que você mudaria se pudesse?")
        
        botao_enviar = st.form_submit_button("Enviar Minha Avaliação")

    if botao_enviar:
        if nome_colaborador.strip() == "":
            st.error("Por favor, preencha o seu nome antes de enviar.")
        else:
            data_hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            nova_resposta = {
                "Data": data_hora_atual,
                "Nome": nome_colaborador,
                "Loja": loja_colaborador,
                "NPS_Geral": nps_score,
                "Lideranca": nota_lideranca,
                "Treinamento": nota_treinamento,
                "Autoavaliacao": nota_autoaval,
                "Avaliacao_Supervisor": nota_supaval,
                "Feedback": feedback_texto
            }
            
            salvar_dados(nova_resposta)
            st.success(f"Obrigado, {nome_colaborador}! Seu feedback foi salvo com sucesso.")
            st.balloons() # Mostra balões na tela para agradecer o funcionário!
