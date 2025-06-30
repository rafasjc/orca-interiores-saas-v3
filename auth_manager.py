"""
Sistema de Autenticação Profissional
Orça Interiores SaaS - Nível Empresarial
"""

import streamlit as st
import hashlib
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging
from config import Config

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthManager:
    """Gerenciador de autenticação e usuários"""
    
    def __init__(self):
        self.db_path = "usuarios.db"
        self.secret_key = Config.get_secrets()['secret_key']
        self.init_database()
        self.create_demo_users()
    
    def init_database(self):
        """Inicializa o banco de dados com todas as tabelas necessárias"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    senha_hash TEXT NOT NULL,
                    plano TEXT DEFAULT 'free',
                    projetos_mes INTEGER DEFAULT 0,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login TIMESTAMP,
                    ativo BOOLEAN DEFAULT 1,
                    empresa TEXT,
                    telefone TEXT
                )
            ''')
            
            # Tabela de projetos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS projetos (
                    id TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL,
                    nome_projeto TEXT NOT NULL,
                    cliente TEXT,
                    ambiente TEXT,
                    material TEXT,
                    area_total REAL,
                    valor_total REAL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    arquivo_nome TEXT,
                    status TEXT DEFAULT 'concluido',
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabela de sessões
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessoes (
                    id TEXT PRIMARY KEY,
                    usuario_id TEXT NOT NULL,
                    token TEXT UNIQUE NOT NULL,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    data_expiracao TIMESTAMP NOT NULL,
                    ativo BOOLEAN DEFAULT 1,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Banco de dados inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def create_demo_users(self):
        """Cria usuários de demonstração"""
        demo_users = [
            {
                'email': 'demo@orcainteriores.com',
                'nome': 'Usuário Demo',
                'senha': 'demo123',
                'plano': 'pro',
                'empresa': 'Empresa Demo'
            },
            {
                'email': 'arquiteto@teste.com',
                'nome': 'João Arquiteto',
                'senha': 'arq123',
                'plano': 'basic',
                'empresa': 'Arquitetura & Design'
            },
            {
                'email': 'marceneiro@teste.com',
                'nome': 'Carlos Marceneiro',
                'senha': 'marc123',
                'plano': 'enterprise',
                'empresa': 'Marcenaria Premium'
            }
        ]
        
        for user_data in demo_users:
            try:
                self.criar_usuario(
                    email=user_data['email'],
                    nome=user_data['nome'],
                    senha=user_data['senha'],
                    plano=user_data['plano'],
                    empresa=user_data.get('empresa', '')
                )
            except:
                pass  # Usuário já existe
    
    def hash_senha(self, senha: str) -> str:
        """Gera hash seguro da senha"""
        return hashlib.pbkdf2_hex(
            senha.encode('utf-8'),
            self.secret_key.encode('utf-8'),
            100000  # 100k iterações para segurança
        )
    
    def gerar_token(self) -> str:
        """Gera token único para sessão"""
        return hashlib.sha256(
            f"{uuid.uuid4()}{datetime.now()}{self.secret_key}".encode()
        ).hexdigest()
    
    def criar_usuario(self, email: str, nome: str, senha: str, 
                     plano: str = 'free', empresa: str = '', 
                     telefone: str = '') -> bool:
        """Cria novo usuário no sistema"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se email já existe
            cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
            if cursor.fetchone():
                return False
            
            # Criar usuário
            usuario_id = str(uuid.uuid4())
            senha_hash = self.hash_senha(senha)
            
            cursor.execute('''
                INSERT INTO usuarios (id, email, nome, senha_hash, plano, empresa, telefone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (usuario_id, email, nome, senha_hash, plano, empresa, telefone))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Usuário criado: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return False
    
    def autenticar_usuario(self, email: str, senha: str) -> Optional[Dict]:
        """Autentica usuário e retorna dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            senha_hash = self.hash_senha(senha)
            cursor.execute('''
                SELECT id, email, nome, plano, projetos_mes, empresa, telefone, ativo
                FROM usuarios 
                WHERE email = ? AND senha_hash = ? AND ativo = 1
            ''', (email, senha_hash))
            
            resultado = cursor.fetchone()
            
            if resultado:
                # Atualizar último login
                cursor.execute('''
                    UPDATE usuarios 
                    SET ultimo_login = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (resultado[0],))
                conn.commit()
                
                usuario = {
                    'id': resultado[0],
                    'email': resultado[1],
                    'nome': resultado[2],
                    'plano': resultado[3],
                    'projetos_mes': resultado[4],
                    'empresa': resultado[5] or '',
                    'telefone': resultado[6] or ''
                }
                
                logger.info(f"Login realizado: {email}")
                conn.close()
                return usuario
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            return None
    
    def incrementar_projetos(self, usuario_id: str) -> bool:
        """Incrementa contador de projetos do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE usuarios 
                SET projetos_mes = projetos_mes + 1 
                WHERE id = ?
            ''', (usuario_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Erro ao incrementar projetos: {e}")
            return False
    
    def verificar_limite_projetos(self, usuario: Dict) -> bool:
        """Verifica se usuário pode criar mais projetos"""
        plano_info = Config.PLANOS.get(usuario['plano'], Config.PLANOS['free'])
        limite = plano_info['projetos_mes']
        
        if limite == 999999:  # Ilimitado
            return True
        
        return usuario['projetos_mes'] < limite
    
    def salvar_projeto(self, usuario_id: str, dados_projeto: Dict) -> str:
        """Salva projeto no banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            projeto_id = str(uuid.uuid4())
            
            cursor.execute('''
                INSERT INTO projetos (
                    id, usuario_id, nome_projeto, cliente, ambiente, 
                    material, area_total, valor_total, arquivo_nome
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                projeto_id,
                usuario_id,
                dados_projeto.get('nome_projeto', 'Projeto sem nome'),
                dados_projeto.get('cliente', ''),
                dados_projeto.get('ambiente', ''),
                dados_projeto.get('material', ''),
                dados_projeto.get('area_total', 0),
                dados_projeto.get('valor_total', 0),
                dados_projeto.get('arquivo_nome', '')
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Projeto salvo: {projeto_id}")
            return projeto_id
            
        except Exception as e:
            logger.error(f"Erro ao salvar projeto: {e}")
            return ""
    
    def obter_projetos_usuario(self, usuario_id: str) -> List[Dict]:
        """Obtém todos os projetos do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, nome_projeto, cliente, ambiente, material, 
                       area_total, valor_total, data_criacao, arquivo_nome
                FROM projetos 
                WHERE usuario_id = ? 
                ORDER BY data_criacao DESC
            ''', (usuario_id,))
            
            projetos = []
            for row in cursor.fetchall():
                projetos.append({
                    'id': row[0],
                    'nome_projeto': row[1],
                    'cliente': row[2],
                    'ambiente': row[3],
                    'material': row[4],
                    'area_total': row[5],
                    'valor_total': row[6],
                    'data_criacao': row[7],
                    'arquivo_nome': row[8]
                })
            
            conn.close()
            return projetos
            
        except Exception as e:
            logger.error(f"Erro ao obter projetos: {e}")
            return []
    
    def obter_estatisticas_usuario(self, usuario_id: str) -> Dict:
        """Obtém estatísticas do usuário"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de projetos
            cursor.execute(
                'SELECT COUNT(*) FROM projetos WHERE usuario_id = ?', 
                (usuario_id,)
            )
            total_projetos = cursor.fetchone()[0]
            
            # Valor total dos projetos
            cursor.execute(
                'SELECT SUM(valor_total) FROM projetos WHERE usuario_id = ?', 
                (usuario_id,)
            )
            valor_total = cursor.fetchone()[0] or 0
            
            # Projetos este mês
            cursor.execute('''
                SELECT COUNT(*) FROM projetos 
                WHERE usuario_id = ? AND date(data_criacao) >= date('now', 'start of month')
            ''', (usuario_id,))
            projetos_mes = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_projetos': total_projetos,
                'valor_total': valor_total,
                'projetos_mes': projetos_mes
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {
                'total_projetos': 0,
                'valor_total': 0,
                'projetos_mes': 0
            }
    
    def resetar_contador_mensal(self):
        """Reseta contador mensal de projetos (executar mensalmente)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('UPDATE usuarios SET projetos_mes = 0')
            conn.commit()
            conn.close()
            
            logger.info("Contador mensal resetado")
            
        except Exception as e:
            logger.error(f"Erro ao resetar contador: {e}")
    
    def criar_dashboard_usuario(self, usuario: Dict):
        """Cria dashboard do usuário na sidebar"""
        st.markdown("### 👤 Minha Conta")
        
        # Informações básicas
        st.markdown(f"**Nome:** {usuario['nome']}")
        st.markdown(f"**Email:** {usuario['email']}")
        if usuario.get('empresa'):
            st.markdown(f"**Empresa:** {usuario['empresa']}")
        
        # Plano atual
        plano_info = Config.PLANOS[usuario['plano']]
        st.markdown(f"**Plano:** {plano_info['nome']}")
        
        # Progresso de projetos
        projetos_usados = usuario['projetos_mes']
        projetos_limite = plano_info['projetos_mes']
        
        if projetos_limite == 999999:
            st.markdown(f"**Projetos:** {projetos_usados} (Ilimitado)")
        else:
            progresso = min(projetos_usados / projetos_limite, 1.0)
            st.markdown(f"**Projetos:** {projetos_usados}/{projetos_limite}")
            st.progress(progresso)
            
            if progresso >= 0.8:
                st.warning("⚠️ Limite quase atingido!")
        
        # Estatísticas
        stats = self.obter_estatisticas_usuario(usuario['id'])
        
        st.markdown("---")
        st.markdown("### 📊 Estatísticas")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Projetos", stats['total_projetos'])
        with col2:
            st.metric("Valor Total", f"R$ {stats['valor_total']:,.2f}")
        
        # Recursos do plano
        st.markdown("---")
        st.markdown("### 🎯 Recursos do Plano")
        for recurso in plano_info['recursos']:
            st.markdown(f"✅ {recurso}")
        
        # Upgrade de plano
        if usuario['plano'] != 'enterprise':
            st.markdown("---")
            if st.button("⬆️ Fazer Upgrade", type="secondary"):
                st.info("🚀 Em breve: Sistema de pagamento integrado!")
        
        return stats

