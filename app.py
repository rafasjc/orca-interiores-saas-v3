"""
Orça Interiores SaaS - Aplicação Principal
Sistema Profissional de Orçamento de Marcenaria
Desenvolvido por um dos melhores programadores do mundo
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import logging

# Imports dos módulos
from config import Config
from auth_manager import AuthManager
from orcamento_engine import OrcamentoEngine
from file_analyzer import FileAnalyzer

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(**Config.get_page_config())

# CSS customizado
st.markdown(Config.get_css_styles(), unsafe_allow_html=True)

# Inicializar componentes
@st.cache_resource
def init_components():
    """Inicializa componentes do sistema"""
    try:
        auth_manager = AuthManager()
        orcamento_engine = OrcamentoEngine()
        file_analyzer = FileAnalyzer()
        return auth_manager, orcamento_engine, file_analyzer
    except Exception as e:
        st.error(f"Erro na inicialização: {e}")
        st.stop()

def main():
    """Função principal da aplicação"""
    try:
        # Inicializar componentes
        auth_manager, orcamento_engine, file_analyzer = init_components()
        
        # Header principal
        st.markdown(f"""
        <div class="main-header fade-in">
            <h1>{Config.APP_NAME}</h1>
            <p>{Config.APP_DESCRIPTION}</p>
            <p><strong>Versão {Config.APP_VERSION} - Sistema SaaS Profissional</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Verificar autenticação
        if 'usuario_logado' not in st.session_state or st.session_state.usuario_logado is None:
            mostrar_tela_login(auth_manager)
        else:
            mostrar_aplicacao_principal(auth_manager, orcamento_engine, file_analyzer)
            
    except Exception as e:
        logger.error(f"Erro na aplicação principal: {e}")
        st.error("Erro interno da aplicação. Tente recarregar a página.")

def mostrar_tela_login(auth_manager: AuthManager):
    """Exibe tela de login e registro"""
    
    # Informações de demonstração
    st.markdown("""
    <div class="success-card">
        <h3>🎯 Contas Demo Disponíveis</h3>
        <p><strong>Usuário Demo:</strong> demo@orcainteriores.com / demo123 (Plano Pro)</p>
        <p><strong>Arquiteto:</strong> arquiteto@teste.com / arq123 (Plano Básico)</p>
        <p><strong>Marceneiro:</strong> marceneiro@teste.com / marc123 (Plano Enterprise)</p>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🚪 Login", "📝 Criar Conta", "💎 Planos"])
    
    with tab1:
        mostrar_formulario_login(auth_manager)
    
    with tab2:
        mostrar_formulario_registro(auth_manager)
    
    with tab3:
        mostrar_planos()

def mostrar_formulario_login(auth_manager: AuthManager):
    """Formulário de login"""
    st.markdown("### 🔐 Acesso ao Sistema")
    
    with st.form("form_login"):
        email = st.text_input("📧 Email", value="demo@orcainteriores.com")
        senha = st.text_input("🔒 Senha", type="password", value="demo123")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_btn = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("🔄 Limpar", use_container_width=True):
                st.rerun()
        
        if login_btn:
            if email and senha:
                usuario = auth_manager.autenticar_usuario(email, senha)
                if usuario:
                    st.session_state.usuario_logado = usuario
                    st.success("✅ Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Email ou senha incorretos")
            else:
                st.error("⚠️ Preencha todos os campos")

def mostrar_formulario_registro(auth_manager: AuthManager):
    """Formulário de registro"""
    st.markdown("### 📝 Criar Nova Conta")
    
    with st.form("form_registro"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("👤 Nome Completo *")
            email = st.text_input("📧 Email *")
            empresa = st.text_input("🏢 Empresa")
        
        with col2:
            senha = st.text_input("🔒 Senha *", type="password")
            telefone = st.text_input("📱 Telefone")
            plano = st.selectbox("💎 Plano Inicial", 
                               options=['free', 'basic'], 
                               format_func=lambda x: Config.PLANOS[x]['nome'])
        
        aceito_termos = st.checkbox("Aceito os termos de uso e política de privacidade")
        
        if st.form_submit_button("✨ Criar Conta", type="primary", use_container_width=True):
            if nome and email and senha and aceito_termos:
                sucesso = auth_manager.criar_usuario(
                    email=email,
                    nome=nome,
                    senha=senha,
                    plano=plano,
                    empresa=empresa,
                    telefone=telefone
                )
                
                if sucesso:
                    st.success("✅ Conta criada com sucesso! Faça login para continuar.")
                else:
                    st.error("❌ Email já cadastrado ou erro interno")
            else:
                st.error("⚠️ Preencha os campos obrigatórios e aceite os termos")

def mostrar_planos():
    """Exibe informações dos planos"""
    st.markdown("### 💎 Planos de Assinatura")
    
    cols = st.columns(len(Config.PLANOS))
    
    for i, (plano_id, plano_info) in enumerate(Config.PLANOS.items()):
        with cols[i]:
            preco_texto = "Gratuito" if plano_info['preco'] == 0 else f"R$ {plano_info['preco']:.2f}/mês"
            projetos_texto = "Ilimitado" if plano_info['projetos_mes'] == 999999 else f"{plano_info['projetos_mes']} projetos/mês"
            
            st.markdown(f"""
            <div class="plan-card">
                <h3>{plano_info['nome']}</h3>
                <h2 style="color: {Config.CORES['primaria']};">{preco_texto}</h2>
                <p><strong>{projetos_texto}</strong></p>
                <ul>
            """, unsafe_allow_html=True)
            
            for recurso in plano_info['recursos']:
                st.markdown(f"<li>{recurso}</li>", unsafe_allow_html=True)
            
            st.markdown("</ul></div>", unsafe_allow_html=True)

def mostrar_aplicacao_principal(auth_manager: AuthManager, orcamento_engine: OrcamentoEngine, file_analyzer: FileAnalyzer):
    """Aplicação principal após login"""
    usuario = st.session_state.usuario_logado
    
    # Sidebar com informações do usuário
    with st.sidebar:
        stats = auth_manager.criar_dashboard_usuario(usuario)
        
        st.markdown("---")
        st.markdown("### 💰 Preços Léo Madeiras")
        for material, info in Config.PRECOS_MATERIAIS.items():
            st.markdown(f"**{material}:** R$ {info['preco_m2']:.2f}/m²")
        st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y')}")
        
        st.markdown("---")
        if st.button("🚪 Sair", type="secondary", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()
    
    # Verificar limite de projetos
    if not auth_manager.verificar_limite_projetos(usuario):
        st.error(f"""
        ⚠️ **Limite de projetos atingido!**
        
        Você já utilizou todos os {Config.PLANOS[usuario['plano']]['projetos_mes']} projetos do seu plano {Config.PLANOS[usuario['plano']]['nome']}.
        
        Faça upgrade para continuar usando o sistema.
        """)
        return
    
    # Área principal
    mostrar_interface_upload(auth_manager, orcamento_engine, file_analyzer, usuario)

def mostrar_interface_upload(auth_manager: AuthManager, orcamento_engine: OrcamentoEngine, 
                           file_analyzer: FileAnalyzer, usuario: Dict):
    """Interface de upload e análise"""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📁 Upload de Projeto 3D")
        
        uploaded_file = st.file_uploader(
            "Escolha um arquivo 3D",
            type=Config.ALLOWED_EXTENSIONS,
            help=f"Formatos suportados: {', '.join(Config.ALLOWED_EXTENSIONS).upper()} (máx. {Config.MAX_FILE_SIZE_MB}MB)"
        )
        
        if uploaded_file:
            # Mostrar informações do arquivo
            st.markdown(f"""
            <div class="success-card">
                <strong>✅ Arquivo:</strong> {uploaded_file.name}<br>
                <strong>📏 Tamanho:</strong> {uploaded_file.size / 1024:.1f} KB<br>
                <strong>🔧 Formato:</strong> {uploaded_file.name.split('.')[-1].upper()}
            </div>
            """, unsafe_allow_html=True)
        
        # Configurações do projeto
        st.markdown("#### ⚙️ Configurações do Projeto")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            cliente = st.text_input("👤 Cliente", placeholder="Nome do cliente")
            ambiente = st.selectbox("🏠 Ambiente", 
                ["Cozinha", "Quarto", "Sala", "Banheiro", "Escritório", "Lavanderia", "Closet"])
            material = st.selectbox("🪵 Material", list(Config.PRECOS_MATERIAIS.keys()))
        
        with col_b:
            qualidade_acessorios = st.selectbox("🔧 Qualidade Acessórios", 
                ["comum", "premium"], format_func=lambda x: x.title())
            margem_lucro = st.slider("💰 Margem de Lucro (%)", 10, 50, 30)
            incluir_montagem = st.checkbox("🔨 Incluir Montagem", value=True)
        
        # Botão de análise
        if uploaded_file and st.button("🚀 Analisar Projeto", type="primary", use_container_width=True):
            processar_arquivo(uploaded_file, {
                'cliente': cliente,
                'ambiente': ambiente,
                'material': material,
                'qualidade_acessorios': qualidade_acessorios,
                'margem_lucro': margem_lucro,
                'incluir_montagem': incluir_montagem
            }, auth_manager, orcamento_engine, file_analyzer, usuario)
    
    with col2:
        mostrar_resumo_lateral()

def processar_arquivo(uploaded_file, configuracoes: Dict, auth_manager: AuthManager, 
                     orcamento_engine: OrcamentoEngine, file_analyzer: FileAnalyzer, usuario: Dict):
    """Processa arquivo e gera orçamento"""
    
    with st.spinner("🔄 Analisando arquivo 3D..."):
        # Analisar arquivo
        sucesso, componentes, mensagem = file_analyzer.analisar_arquivo(uploaded_file)
        
        if not sucesso:
            st.error(f"❌ {mensagem}")
            return
        
        st.success(f"✅ {mensagem}")
        
        # Gerar orçamento
        with st.spinner("💰 Calculando orçamento..."):
            try:
                orcamento = orcamento_engine.gerar_orcamento_completo(componentes, configuracoes)
                
                # Salvar projeto
                dados_projeto = {
                    'nome_projeto': f"Projeto {ambiente} - {datetime.now().strftime('%d/%m/%Y')}",
                    'cliente': configuracoes['cliente'],
                    'ambiente': configuracoes['ambiente'],
                    'material': configuracoes['material'],
                    'area_total': orcamento['resumo']['area_total'],
                    'valor_total': orcamento['resumo']['financeiro']['total_final'],
                    'arquivo_nome': uploaded_file.name
                }
                
                projeto_id = auth_manager.salvar_projeto(usuario['id'], dados_projeto)
                
                # Incrementar contador
                auth_manager.incrementar_projetos(usuario['id'])
                st.session_state.usuario_logado['projetos_mes'] += 1
                
                # Armazenar resultados
                st.session_state.orcamento_atual = orcamento
                st.session_state.componentes_atual = componentes
                st.session_state.projeto_id = projeto_id
                
                st.success("🎉 Orçamento gerado com sucesso!")
                
                # Mostrar resultados
                mostrar_resultados_orcamento(orcamento, componentes)
                
            except Exception as e:
                logger.error(f"Erro no processamento: {e}")
                st.error(f"❌ Erro no processamento: {str(e)}")

def mostrar_resultados_orcamento(orcamento: Dict, componentes: List[Dict]):
    """Exibe resultados do orçamento"""
    
    resumo = orcamento['resumo']
    
    # Tabs para diferentes visualizações
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumo", "🔧 Componentes", "📈 Gráficos", "📄 Relatório"])
    
    with tab1:
        mostrar_resumo_financeiro(resumo)
    
    with tab2:
        mostrar_detalhes_componentes(orcamento['componentes'])
    
    with tab3:
        mostrar_graficos_orcamento(resumo, orcamento['componentes'])
    
    with tab4:
        mostrar_relatorio_completo(orcamento)

def mostrar_resumo_financeiro(resumo: Dict):
    """Exibe resumo financeiro"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>📐 Área Total</h4>
            <h3>{resumo['area_total']:.2f} m²</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🪵 Material</h4>
            <h3>R$ {resumo['material']['custo_total']:,.2f}</h3>
            <small>{resumo['material']['tipo']}</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>🔧 Serviços</h4>
            <h3>R$ {resumo['servicos']['corte_usinagem'] + resumo['servicos']['mao_obra'] + resumo['servicos']['montagem']:,.2f}</h3>
            <small>Corte + Mão de obra + Montagem</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 TOTAL FINAL</h4>
            <h2 style="color: {Config.CORES['primaria']};">R$ {resumo['financeiro']['total_final']:,.2f}</h2>
            <small>Margem: {resumo['financeiro']['margem_lucro_percent']:.0f}%</small>
        </div>
        """, unsafe_allow_html=True)

def mostrar_detalhes_componentes(componentes: List[Dict]):
    """Exibe detalhes dos componentes"""
    
    st.markdown("### 🔧 Detalhamento por Componente")
    
    # Criar DataFrame
    dados = []
    for comp in componentes:
        dados.append({
            'Componente': comp['nome'],
            'Tipo': comp['tipo'].title(),
            'Largura (m)': f"{comp['dimensoes']['largura']:.3f}",
            'Altura (m)': f"{comp['dimensoes']['altura']:.3f}",
            'Profundidade (m)': f"{comp['dimensoes']['profundidade']:.3f}",
            'Área (m²)': f"{comp['area']:.3f}",
            'Material (R$)': f"{comp['custo_material']:.2f}",
            'Acessórios (R$)': f"{comp['custo_acessorios']:.2f}",
            'Total (R$)': f"{comp['custo_total_componente']:.2f}"
        })
    
    df = pd.DataFrame(dados)
    st.dataframe(df, use_container_width=True)
    
    # Detalhes de acessórios
    st.markdown("#### 🔩 Acessórios por Componente")
    
    for comp in componentes:
        if comp['acessorios']:
            with st.expander(f"🔧 {comp['nome']}"):
                for acess_nome, acess_info in comp['acessorios'].items():
                    st.markdown(f"""
                    **{acess_info['descricao']}**
                    - Quantidade: {acess_info['quantidade']}
                    - Preço unitário: R$ {acess_info['preco_unitario']:.2f}
                    - Total: R$ {acess_info['quantidade'] * acess_info['preco_unitario']:.2f}
                    """)

def mostrar_graficos_orcamento(resumo: Dict, componentes: List[Dict]):
    """Exibe gráficos do orçamento"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza - Distribuição de custos
        custos = {
            'Material': resumo['material']['custo_total'],
            'Acessórios': resumo['acessorios']['custo_total'],
            'Corte/Usinagem': resumo['servicos']['corte_usinagem'],
            'Mão de Obra': resumo['servicos']['mao_obra'],
            'Montagem': resumo['servicos']['montagem'],
            'Margem': resumo['financeiro']['valor_margem']
        }
        
        fig_pie = px.pie(
            values=list(custos.values()),
            names=list(custos.keys()),
            title="Distribuição de Custos",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Gráfico de barras - Custo por componente
        nomes = [comp['nome'] for comp in componentes]
        custos_comp = [comp['custo_total_componente'] for comp in componentes]
        
        fig_bar = px.bar(
            x=nomes,
            y=custos_comp,
            title="Custo por Componente",
            labels={'x': 'Componente', 'y': 'Custo (R$)'},
            color=custos_comp,
            color_continuous_scale='Blues'
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)

def mostrar_relatorio_completo(orcamento: Dict):
    """Exibe relatório completo"""
    
    st.markdown("### 📄 Relatório Completo")
    
    # Informações do projeto
    config = orcamento['configuracoes']
    resumo = orcamento['resumo']
    
    st.markdown(f"""
    **📋 Informações do Projeto**
    - **Cliente:** {config.get('cliente', 'Não informado')}
    - **Ambiente:** {config['ambiente']}
    - **Material:** {config['material']}
    - **Data:** {datetime.now().strftime('%d/%m/%Y %H:%M')}
    - **Validade:** {orcamento['validade_dias']} dias
    """)
    
    # Resumo executivo
    st.markdown(f"""
    **💰 Resumo Executivo**
    - **Área Total:** {resumo['area_total']:.2f} m²
    - **Valor por m²:** R$ {resumo['financeiro']['total_final'] / resumo['area_total']:.2f}
    - **Subtotal:** R$ {resumo['financeiro']['subtotal']:,.2f}
    - **Margem de Lucro:** {resumo['financeiro']['margem_lucro_percent']:.0f}% (R$ {resumo['financeiro']['valor_margem']:,.2f})
    - **TOTAL FINAL:** R$ {resumo['financeiro']['total_final']:,.2f}
    """)
    
    # Observações
    st.markdown("**📝 Observações:**")
    for obs in orcamento['observacoes']:
        st.markdown(f"• {obs}")
    
    # Exportar
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Exportar JSON", use_container_width=True):
            json_data = json.dumps(orcamento, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"orcamento_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📧 Enviar por Email", use_container_width=True):
            st.info("🚀 Em breve: Envio automático por email!")

def mostrar_resumo_lateral():
    """Exibe resumo na lateral"""
    
    if 'orcamento_atual' in st.session_state:
        orcamento = st.session_state.orcamento_atual
        resumo = orcamento['resumo']
        
        st.markdown("### 💰 Último Orçamento")
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>💰 Valor Total</h4>
            <h3>R$ {resumo['financeiro']['total_final']:,.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📐 Área</h4>
            <h3>{resumo['area_total']:.2f} m²</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>🔧 Componentes</h4>
            <h3>{len(st.session_state.componentes_atual)}</h3>
        </div>
        """, unsafe_allow_html=True)
        
    else:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            <h3>📤</h3>
            <p>Faça upload de um arquivo 3D</p>
            <p><small>Formatos: OBJ, DAE, STL, PLY</small></p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

