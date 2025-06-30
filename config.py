"""
Configurações da Aplicação Orça Interiores SaaS
Desenvolvido por um dos melhores programadores do mundo
"""

import streamlit as st
from typing import Dict, Any
import os

class Config:
    """Configurações centralizadas da aplicação"""
    
    # Configurações da aplicação
    APP_NAME = "🏠 Orça Interiores"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "Análise automática de projetos 3D para orçamento de marcenaria"
    
    # Configurações de upload
    MAX_FILE_SIZE_MB = 200
    ALLOWED_EXTENSIONS = ['obj', 'dae', 'stl', 'ply']
    
    # Planos de assinatura
    PLANOS = {
        'free': {
            'nome': 'Gratuito',
            'preco': 0.00,
            'projetos_mes': 3,
            'recursos': ['Upload básico', 'Orçamento simples', 'Suporte email']
        },
        'basic': {
            'nome': 'Básico',
            'preco': 49.90,
            'projetos_mes': 50,
            'recursos': ['Todos do Gratuito', 'Visualização 3D', 'Preços atualizados', 'Relatórios PDF']
        },
        'pro': {
            'nome': 'Profissional',
            'preco': 99.90,
            'projetos_mes': 200,
            'recursos': ['Todos do Básico', 'API Access', 'White Label', 'Suporte prioritário']
        },
        'enterprise': {
            'nome': 'Empresarial',
            'preco': 299.90,
            'projetos_mes': 999999,
            'recursos': ['Todos do Pro', 'Multi-usuários', 'Integração customizada', 'Suporte 24/7']
        }
    }
    
    # Preços de materiais (Léo Madeiras - Atualizados)
    PRECOS_MATERIAIS = {
        'MDF 15mm': {
            'preco_m2': 69.15,
            'desperdicio': 0.10,
            'descricao': 'MDF Cru 15mm - Eucatex'
        },
        'MDF 18mm': {
            'preco_m2': 78.50,
            'desperdicio': 0.10,
            'descricao': 'MDF Cru 18mm - Eucatex'
        },
        'Compensado 15mm': {
            'preco_m2': 64.00,
            'desperdicio': 0.08,
            'descricao': 'Compensado Naval 15mm'
        },
        'Melamina 15mm': {
            'preco_m2': 89.50,
            'desperdicio': 0.12,
            'descricao': 'Melamina Branca 15mm'
        },
        'Melamina 18mm': {
            'preco_m2': 98.75,
            'desperdicio': 0.12,
            'descricao': 'Melamina Branca 18mm'
        }
    }
    
    # Custos de serviços
    CUSTOS_SERVICOS = {
        'corte_linear': 2.50,  # Por metro linear
        'furo_dobradica': 1.50,  # Por furo
        'taxa_minima_corte': 15.00,  # Taxa mínima por peça
        'mao_obra_m2': 120.00,  # Mão de obra por m²
        'montagem_m2': 80.00,  # Montagem por m²
    }
    
    # Acessórios padrão
    ACESSORIOS = {
        'dobradica_comum': {
            'preco': 12.50,
            'descricao': 'Dobradiça comum 35mm'
        },
        'dobradica_premium': {
            'preco': 28.00,
            'descricao': 'Dobradiça Blum com amortecedor'
        },
        'puxador_comum': {
            'preco': 8.50,
            'descricao': 'Puxador alumínio 128mm'
        },
        'puxador_premium': {
            'preco': 25.00,
            'descricao': 'Puxador inox escovado 160mm'
        },
        'corredicao_comum': {
            'preco': 35.00,
            'descricao': 'Corrediça telescópica 45cm'
        },
        'corredicao_premium': {
            'preco': 85.00,
            'descricao': 'Corrediça Blum soft-close 50cm'
        }
    }
    
    # Configurações de cores e tema
    CORES = {
        'primaria': '#667eea',
        'secundaria': '#764ba2',
        'sucesso': '#28a745',
        'erro': '#dc3545',
        'aviso': '#ffc107',
        'info': '#17a2b8'
    }
    
    @classmethod
    def get_secrets(cls) -> Dict[str, Any]:
        """Obtém configurações secretas do Streamlit"""
        try:
            return {
                'database_url': st.secrets.get('database', {}).get('url', 'sqlite:///usuarios.db'),
                'secret_key': st.secrets.get('auth', {}).get('secret_key', 'orca-interiores-2025'),
                'leo_madeiras_cache': st.secrets.get('leo_madeiras', {}).get('cache_duration', 21600),
                'debug_mode': st.secrets.get('app', {}).get('debug', False)
            }
        except:
            # Fallback para desenvolvimento local
            return {
                'database_url': 'sqlite:///usuarios.db',
                'secret_key': 'orca-interiores-2025',
                'leo_madeiras_cache': 21600,
                'debug_mode': True
            }
    
    @classmethod
    def get_page_config(cls) -> Dict[str, Any]:
        """Configuração da página Streamlit"""
        return {
            'page_title': cls.APP_NAME,
            'page_icon': '🏠',
            'layout': 'wide',
            'initial_sidebar_state': 'expanded',
            'menu_items': {
                'Get Help': 'https://orcainteriores.com/suporte',
                'Report a bug': 'https://orcainteriores.com/bug-report',
                'About': f'{cls.APP_NAME} v{cls.APP_VERSION} - Sistema profissional de orçamento de marcenaria'
            }
        }
    
    @classmethod
    def get_css_styles(cls) -> str:
        """CSS customizado da aplicação"""
        return f"""
        <style>
            /* Importar fonte Google */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Reset e configurações globais */
            .main {{
                font-family: 'Inter', sans-serif;
            }}
            
            /* Header principal */
            .main-header {{
                background: linear-gradient(135deg, {cls.CORES['primaria']} 0%, {cls.CORES['secundaria']} 100%);
                padding: 2rem;
                border-radius: 15px;
                text-align: center;
                color: white;
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
            }}
            
            .main-header h1 {{
                margin: 0;
                font-size: 2.5rem;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            
            .main-header p {{
                margin: 0.5rem 0 0 0;
                font-size: 1.1rem;
                opacity: 0.9;
            }}
            
            /* Cards de métricas */
            .metric-card {{
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                border-left: 4px solid {cls.CORES['primaria']};
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            
            .metric-card:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            
            .metric-card h3 {{
                color: {cls.CORES['primaria']};
                margin: 0.5rem 0;
                font-weight: 600;
            }}
            
            .metric-card h4 {{
                color: #666;
                margin: 0;
                font-weight: 500;
                font-size: 0.9rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            
            /* Cards de sucesso */
            .success-card {{
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 1.5rem;
                border-radius: 12px;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(21, 87, 36, 0.1);
            }}
            
            /* Cards de erro */
            .error-card {{
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                border: 1px solid #f5c6cb;
                color: #721c24;
                padding: 1.5rem;
                border-radius: 12px;
                margin: 1rem 0;
                box-shadow: 0 4px 12px rgba(114, 28, 36, 0.1);
            }}
            
            /* Cards de planos */
            .plan-card {{
                background: white;
                border: 2px solid #e9ecef;
                border-radius: 15px;
                padding: 1.5rem;
                margin: 1rem 0;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }}
            
            .plan-card:hover {{
                border-color: {cls.CORES['primaria']};
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(102, 126, 234, 0.2);
            }}
            
            .plan-card.active {{
                border-color: {cls.CORES['primaria']};
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
            }}
            
            .plan-card.active::before {{
                content: "✓ ATIVO";
                position: absolute;
                top: 10px;
                right: 15px;
                background: {cls.CORES['primaria']};
                color: white;
                padding: 0.3rem 0.8rem;
                border-radius: 20px;
                font-size: 0.7rem;
                font-weight: 600;
            }}
            
            /* Componentes personalizados */
            .component-item {{
                background: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
                transition: all 0.2s ease;
            }}
            
            .component-item:hover {{
                background: #e9ecef;
                border-color: {cls.CORES['primaria']};
            }}
            
            /* Sidebar customizada */
            .sidebar-info {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 1rem;
                border-radius: 10px;
                margin: 1rem 0;
                border-left: 4px solid {cls.CORES['primaria']};
            }}
            
            /* Botões customizados */
            .stButton > button {{
                border-radius: 8px;
                border: none;
                font-weight: 500;
                transition: all 0.2s ease;
            }}
            
            .stButton > button:hover {{
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            }}
            
            /* Upload area */
            .uploadedFile {{
                border: 2px dashed {cls.CORES['primaria']};
                border-radius: 10px;
                padding: 2rem;
                text-align: center;
                background: rgba(102, 126, 234, 0.05);
                transition: all 0.3s ease;
            }}
            
            .uploadedFile:hover {{
                border-color: {cls.CORES['secundaria']};
                background: rgba(118, 75, 162, 0.05);
            }}
            
            /* Animações */
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: translateY(20px); }}
                to {{ opacity: 1; transform: translateY(0); }}
            }}
            
            .fade-in {{
                animation: fadeIn 0.5s ease-out;
            }}
            
            /* Responsividade */
            @media (max-width: 768px) {{
                .main-header h1 {{
                    font-size: 2rem;
                }}
                
                .metric-card {{
                    padding: 1rem;
                }}
            }}
            
            /* Ocultar elementos do Streamlit */
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
        </style>
        """

