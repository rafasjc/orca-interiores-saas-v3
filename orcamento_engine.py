"""
Engine de Orçamento Profissional
Sistema avançado de cálculo de custos para marcenaria
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from config import Config

logger = logging.getLogger(__name__)

class OrcamentoEngine:
    """Engine profissional de cálculo de orçamentos"""
    
    def __init__(self):
        self.precos_materiais = Config.PRECOS_MATERIAIS
        self.custos_servicos = Config.CUSTOS_SERVICOS
        self.acessorios = Config.ACESSORIOS
        self.data_atualizacao = datetime.now()
    
    def calcular_area_componente(self, largura: float, altura: float, 
                               profundidade: float = 0) -> float:
        """Calcula área de um componente considerando todas as faces"""
        try:
            # Área principal (frente)
            area_principal = largura * altura
            
            # Se tem profundidade, considerar laterais
            if profundidade > 0:
                area_laterais = 2 * (altura * profundidade)
                area_total = area_principal + area_laterais
            else:
                area_total = area_principal
            
            return round(area_total, 4)
            
        except Exception as e:
            logger.error(f"Erro no cálculo de área: {e}")
            return 0.0
    
    def detectar_tipo_componente(self, nome: str, dimensoes: Dict) -> str:
        """Detecta o tipo de componente baseado no nome e dimensões"""
        nome_lower = nome.lower()
        largura = dimensoes.get('largura', 0)
        altura = dimensoes.get('altura', 0)
        profundidade = dimensoes.get('profundidade', 0)
        
        # Regras de detecção
        if any(palavra in nome_lower for palavra in ['porta', 'door']):
            return 'porta'
        elif any(palavra in nome_lower for palavra in ['prateleira', 'shelf']):
            return 'prateleira'
        elif any(palavra in nome_lower for palavra in ['lateral', 'side']):
            return 'lateral'
        elif any(palavra in nome_lower for palavra in ['fundo', 'back']):
            return 'fundo'
        elif any(palavra in nome_lower for palavra in ['tampo', 'top', 'bancada']):
            return 'tampo'
        elif any(palavra in nome_lower for palavra in ['gaveta', 'drawer']):
            return 'gaveta'
        elif altura > largura and altura > profundidade:
            return 'lateral'
        elif largura > altura and profundidade < 0.1:
            return 'prateleira'
        else:
            return 'painel'
    
    def calcular_acessorios_componente(self, tipo: str, dimensoes: Dict, 
                                     qualidade: str = 'comum') -> Dict:
        """Calcula acessórios necessários para um componente"""
        acessorios_necessarios = {}
        
        try:
            if tipo == 'porta':
                # Dobradiças (2-3 por porta dependendo da altura)
                altura = dimensoes.get('altura', 0)
                num_dobradicas = 3 if altura > 1.5 else 2
                
                dobradica_tipo = f'dobradica_{qualidade}'
                acessorios_necessarios[dobradica_tipo] = {
                    'quantidade': num_dobradicas,
                    'preco_unitario': self.acessorios[dobradica_tipo]['preco'],
                    'descricao': self.acessorios[dobradica_tipo]['descricao']
                }
                
                # Puxador
                puxador_tipo = f'puxador_{qualidade}'
                acessorios_necessarios[puxador_tipo] = {
                    'quantidade': 1,
                    'preco_unitario': self.acessorios[puxador_tipo]['preco'],
                    'descricao': self.acessorios[puxador_tipo]['descricao']
                }
            
            elif tipo == 'gaveta':
                # Corrediças
                profundidade = dimensoes.get('profundidade', 0.45)
                corredicao_tipo = f'corredicao_{qualidade}'
                
                acessorios_necessarios[corredicao_tipo] = {
                    'quantidade': 2,  # Par de corrediças
                    'preco_unitario': self.acessorios[corredicao_tipo]['preco'],
                    'descricao': self.acessorios[corredicao_tipo]['descricao']
                }
                
                # Puxador
                puxador_tipo = f'puxador_{qualidade}'
                acessorios_necessarios[puxador_tipo] = {
                    'quantidade': 1,
                    'preco_unitario': self.acessorios[puxador_tipo]['preco'],
                    'descricao': self.acessorios[puxador_tipo]['descricao']
                }
            
            return acessorios_necessarios
            
        except Exception as e:
            logger.error(f"Erro no cálculo de acessórios: {e}")
            return {}
    
    def calcular_custo_corte(self, componentes: List[Dict]) -> Dict:
        """Calcula custos de corte e usinagem"""
        try:
            custo_total = 0
            detalhes = []
            
            for comp in componentes:
                # Corte linear (perímetro)
                largura = comp.get('largura', 0)
                altura = comp.get('altura', 0)
                perimetro = 2 * (largura + altura)
                
                custo_corte_linear = perimetro * self.custos_servicos['corte_linear']
                custo_total += custo_corte_linear
                
                # Furos para dobradiças (se for porta)
                tipo = comp.get('tipo', '')
                if tipo == 'porta':
                    num_furos = 6  # 3 dobradiças x 2 furos cada
                    custo_furos = num_furos * self.custos_servicos['furo_dobradica']
                    custo_total += custo_furos
                    
                    detalhes.append({
                        'componente': comp.get('nome', 'Componente'),
                        'corte_linear': custo_corte_linear,
                        'furos': custo_furos
                    })
                else:
                    detalhes.append({
                        'componente': comp.get('nome', 'Componente'),
                        'corte_linear': custo_corte_linear,
                        'furos': 0
                    })
            
            # Taxa mínima por projeto
            if custo_total < self.custos_servicos['taxa_minima_corte'] * len(componentes):
                custo_total = self.custos_servicos['taxa_minima_corte'] * len(componentes)
            
            return {
                'custo_total': round(custo_total, 2),
                'detalhes': detalhes
            }
            
        except Exception as e:
            logger.error(f"Erro no cálculo de corte: {e}")
            return {'custo_total': 0, 'detalhes': []}
    
    def gerar_orcamento_completo(self, componentes: List[Dict], 
                               configuracoes: Dict) -> Dict:
        """Gera orçamento completo com todos os custos"""
        try:
            # Configurações
            material = configuracoes.get('material', 'MDF 15mm')
            qualidade_acessorios = configuracoes.get('qualidade_acessorios', 'comum')
            margem_lucro = configuracoes.get('margem_lucro', 30) / 100
            incluir_montagem = configuracoes.get('incluir_montagem', True)
            
            # Informações do material
            info_material = self.precos_materiais.get(material, self.precos_materiais['MDF 15mm'])
            preco_m2 = info_material['preco_m2']
            desperdicio = info_material['desperdicio']
            
            # Processar componentes
            componentes_processados = []
            area_total = 0
            custo_material_total = 0
            custo_acessorios_total = 0
            
            for comp in componentes:
                # Calcular área
                area_comp = self.calcular_area_componente(
                    comp.get('largura', 0),
                    comp.get('altura', 0),
                    comp.get('profundidade', 0)
                )
                
                # Detectar tipo
                tipo = self.detectar_tipo_componente(comp.get('nome', ''), comp)
                
                # Custo do material
                custo_material_comp = area_comp * preco_m2 * (1 + desperdicio)
                
                # Acessórios
                acessorios_comp = self.calcular_acessorios_componente(
                    tipo, comp, qualidade_acessorios
                )
                
                custo_acessorios_comp = sum(
                    item['quantidade'] * item['preco_unitario'] 
                    for item in acessorios_comp.values()
                )
                
                # Adicionar aos totais
                area_total += area_comp
                custo_material_total += custo_material_comp
                custo_acessorios_total += custo_acessorios_comp
                
                # Componente processado
                componentes_processados.append({
                    'nome': comp.get('nome', 'Componente'),
                    'tipo': tipo,
                    'dimensoes': {
                        'largura': comp.get('largura', 0),
                        'altura': comp.get('altura', 0),
                        'profundidade': comp.get('profundidade', 0)
                    },
                    'area': area_comp,
                    'custo_material': round(custo_material_comp, 2),
                    'acessorios': acessorios_comp,
                    'custo_acessorios': round(custo_acessorios_comp, 2),
                    'custo_total_componente': round(custo_material_comp + custo_acessorios_comp, 2)
                })
            
            # Custos de serviços
            custos_corte = self.calcular_custo_corte(componentes)
            custo_mao_obra = area_total * self.custos_servicos['mao_obra_m2']
            custo_montagem = area_total * self.custos_servicos['montagem_m2'] if incluir_montagem else 0
            
            # Subtotal
            subtotal = (custo_material_total + custo_acessorios_total + 
                       custos_corte['custo_total'] + custo_mao_obra + custo_montagem)
            
            # Margem de lucro
            valor_margem = subtotal * margem_lucro
            total_final = subtotal + valor_margem
            
            # Resumo financeiro
            resumo = {
                'area_total': round(area_total, 2),
                'material': {
                    'tipo': material,
                    'preco_m2': preco_m2,
                    'desperdicio_percent': desperdicio * 100,
                    'custo_total': round(custo_material_total, 2)
                },
                'acessorios': {
                    'qualidade': qualidade_acessorios,
                    'custo_total': round(custo_acessorios_total, 2)
                },
                'servicos': {
                    'corte_usinagem': round(custos_corte['custo_total'], 2),
                    'mao_obra': round(custo_mao_obra, 2),
                    'montagem': round(custo_montagem, 2) if incluir_montagem else 0
                },
                'financeiro': {
                    'subtotal': round(subtotal, 2),
                    'margem_lucro_percent': margem_lucro * 100,
                    'valor_margem': round(valor_margem, 2),
                    'total_final': round(total_final, 2)
                }
            }
            
            # Orçamento completo
            orcamento = {
                'data_geracao': datetime.now().isoformat(),
                'configuracoes': configuracoes,
                'componentes': componentes_processados,
                'custos_corte_detalhes': custos_corte['detalhes'],
                'resumo': resumo,
                'observacoes': self.gerar_observacoes(resumo),
                'validade_dias': 30
            }
            
            logger.info(f"Orçamento gerado: R$ {total_final:.2f} para {len(componentes)} componentes")
            return orcamento
            
        except Exception as e:
            logger.error(f"Erro na geração do orçamento: {e}")
            raise
    
    def gerar_observacoes(self, resumo: Dict) -> List[str]:
        """Gera observações automáticas baseadas no orçamento"""
        observacoes = []
        
        try:
            # Observações sobre material
            material_info = resumo['material']
            observacoes.append(f"Material: {material_info['tipo']} - R$ {material_info['preco_m2']:.2f}/m²")
            observacoes.append(f"Desperdício considerado: {material_info['desperdicio_percent']:.0f}%")
            
            # Observações sobre área
            area = resumo['area_total']
            if area < 2:
                observacoes.append("⚠️ Projeto pequeno - considere taxa mínima de serviço")
            elif area > 20:
                observacoes.append("📦 Projeto grande - considere desconto por volume")
            
            # Observações sobre custos
            total = resumo['financeiro']['total_final']
            if total > 10000:
                observacoes.append("💰 Projeto de alto valor - considere parcelamento")
            
            # Observações sobre prazo
            observacoes.append("📅 Prazo estimado: 15-20 dias úteis")
            observacoes.append("🔧 Instalação inclusa no valor da mão de obra")
            observacoes.append("📋 Garantia: 12 meses contra defeitos de fabricação")
            
            return observacoes
            
        except Exception as e:
            logger.error(f"Erro na geração de observações: {e}")
            return ["Orçamento gerado automaticamente"]
    
    def criar_dataframe_componentes(self, componentes: List[Dict]) -> pd.DataFrame:
        """Cria DataFrame dos componentes para visualização"""
        try:
            dados = []
            for comp in componentes:
                dados.append({
                    'Componente': comp['nome'],
                    'Tipo': comp['tipo'].title(),
                    'Largura (m)': comp['dimensoes']['largura'],
                    'Altura (m)': comp['dimensoes']['altura'],
                    'Profundidade (m)': comp['dimensoes']['profundidade'],
                    'Área (m²)': comp['area'],
                    'Material (R$)': comp['custo_material'],
                    'Acessórios (R$)': comp['custo_acessorios'],
                    'Total (R$)': comp['custo_total_componente']
                })
            
            return pd.DataFrame(dados)
            
        except Exception as e:
            logger.error(f"Erro na criação do DataFrame: {e}")
            return pd.DataFrame()
    
    def exportar_orcamento_json(self, orcamento: Dict) -> str:
        """Exporta orçamento em formato JSON"""
        try:
            import json
            return json.dumps(orcamento, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erro na exportação JSON: {e}")
            return "{}"

