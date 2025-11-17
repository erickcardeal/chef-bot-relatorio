import requests
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from config import (
    NOTION_HEADERS,
    NOTION_CHEFS_DB,
    NOTION_CLIENTES_DB,
    NOTION_CALENDARIO_DB
)

# Configurar logger no nível do módulo
logger_notion = logging.getLogger(__name__)


class NotionAPI:
    """Classe para interagir com a API do Notion"""
    
    def __init__(self, api_key: str):
        """Inicializa a API do Notion"""
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    async def buscar_chef_por_telegram(self, telegram_username: str) -> Optional[Dict]:
        """
        Busca chef no Notion por Telegram Username (sem @)
        """
        url = f"https://api.notion.com/v1/databases/{NOTION_CHEFS_DB}/query"
        
        # Remove @ se tiver
        username_limpo = telegram_username.replace('@', '') if telegram_username else ''
        
        # Busca APENAS por Telegram Username
        payload = {
            "filter": {
                "property": "Telegram Username",
                "rich_text": {
                    "equals": username_limpo
                }
            }
        }
        
        try:
            # Executar requisição em thread separada para não bloquear event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, headers=self.headers, json=payload, timeout=10)
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                chef = data['results'][0]
                
                # Extrair informações do chef
                nome_completo = chef['properties'].get('Nome Completo', {})
                if nome_completo.get('title') and len(nome_completo['title']) > 0:
                    nome = nome_completo['title'][0]['text']['content']
                else:
                    nome = "Nome não encontrado"
                
                return {
                    'id': chef['id'],
                    'nome': nome,
                    'encontrado': True
                }
            
            return None
        
        except requests.Timeout:
            print(f"⏱️ TIMEOUT ao buscar chef: A requisição demorou mais de 10 segundos")
            return None
        except Exception as e:
            print(f"❌ ERRO ao buscar chef: {e}")
            return None
    
    async def buscar_atendimentos_chef(self, chef_id: str, dias: int = 7, sem_relatorio: bool = True) -> List[Dict]:
        """
        Busca atendimentos dos últimos N dias do chef no Calendário
        Se sem_relatorio=True, retorna apenas atendimentos sem relatório
        """
        url = f"https://api.notion.com/v1/databases/{NOTION_CALENDARIO_DB}/query"
        
        # Usar data de hoje (sem hora) para evitar problemas de timezone
        # Considerar que estamos buscando dos últimos 7 dias, incluindo hoje
        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        dias_atras = hoje - timedelta(days=dias-1)  # -1 para incluir o dia inicial (ex: 7 dias = hoje + 6 dias anteriores)
        
        # Formatar datas corretamente (apenas data, sem hora)
        # data_inicio: 7 dias atrás (inclusivo)
        # data_fim: amanhã (exclusivo, então inclui até hoje)
        data_inicio = dias_atras.strftime("%Y-%m-%d")
        data_fim = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")  # Amanhã (exclusivo)
        filtro_tipo = "sem relatório" if sem_relatorio else "todos"
        logger_notion.info(f"🔍 Buscando atendimentos do chef {chef_id[:8]}... de {data_inicio} até {data_fim} (exclusivo) - {filtro_tipo}")
        
        # Construir filtros base
        filtros = [
            {
                "property": "Date",
                "date": {
                    "on_or_after": data_inicio,
                    "before": data_fim
                }
            },
            {
                "property": "Chef Alocado",
                "relation": {
                    "contains": chef_id
                }
            }
        ]
        
        # Adicionar filtro de relatório se solicitado
        if sem_relatorio:
            filtros.append({
                "property": "Relatório",
                "relation": {
                    "is_empty": True
                }
            })
            logger_notion.info(f"✅ Filtro aplicado: apenas atendimentos sem relatório")
        
        payload = {
            "filter": {
                "and": filtros
            },
            "sorts": [
                {
                    "property": "Date",
                    "direction": "descending"
                }
            ],
            "page_size": 100  # Limite máximo do Notion
        }
        
        try:
            atendimentos = []
            has_more = True
            next_cursor = None
            
            # Loop para buscar todas as páginas
            while has_more:
                if next_cursor:
                    payload['start_cursor'] = next_cursor
                
                response = requests.post(url, headers=self.headers, json=payload, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Processar resultados da página atual
                resultados_pagina = data.get('results', [])
                logger_notion.info(f"📄 Página atual: {len(resultados_pagina)} resultados")
                
                # Contadores para debug
                total_resultados = len(resultados_pagina)
                chef_nao_encontrado = 0
                cliente_nao_encontrado = 0
                data_fora_periodo = 0
                atendimentos_validos = 0
                
                for item in resultados_pagina:
                    props = item['properties']
                    
                    # Verificar se o chef está realmente na relação
                    chef_alocado = props.get('Chef Alocado', {}).get('relation', [])
                    chef_ids = [r['id'] for r in chef_alocado]
                    
                    if chef_id not in chef_ids:
                        # Se o chef não estiver na lista, pular
                        chef_nao_encontrado += 1
                        continue
                    
                    # Nome do cliente
                    cliente_relation = props.get('Quem é', {}).get('relation', [])
                    if not cliente_relation:
                        cliente_nao_encontrado += 1
                        logger_notion.warning(f"⚠️ Atendimento {item['id'][:8]}... sem cliente")
                        continue
                    
                    cliente_id = cliente_relation[0]['id']
                    
                    # Buscar nome do cliente
                    cliente_nome = await self.buscar_nome_cliente(cliente_id)
                    if not cliente_nome:
                        cliente_nao_encontrado += 1
                        logger_notion.warning(f"⚠️ Cliente {cliente_id[:8]}... não encontrado")
                        continue
                    
                    # Horário
                    date_obj = props.get('Date', {}).get('date', {})
                    data_completa = date_obj.get('start', '')
                    
                    if 'T' in data_completa:
                        data_str = data_completa.split('T')[0]
                        horario = data_completa.split('T')[1][:5]
                    else:
                        data_str = data_completa
                        horario = '??:??'
                    
                    # Buscar propriedade Personal Shopper
                    personal_shopper_prop = props.get('Personal Shopper', {})
                    personal_shopper = None
                    
                    # Log para debug: ver o que está vindo do Notion
                    logger_notion.info(f"🔍 [NOTION] Personal Shopper prop para {cliente_nome}: tipo={personal_shopper_prop.get('type')}, valor_completo={personal_shopper_prop}")
                    
                    # Verificar tipo da propriedade (pode ser select, checkbox, ou text)
                    if personal_shopper_prop.get('type') == 'select':
                        select_value = personal_shopper_prop.get('select')
                        if select_value is None:
                            personal_shopper = ''
                            logger_notion.info(f"⚠️ [NOTION] Personal Shopper select é None para {cliente_nome}")
                        else:
                            personal_shopper = select_value.get('name', '')
                            logger_notion.info(f"✅ [NOTION] Personal Shopper select extraído: '{personal_shopper}' para {cliente_nome} (select_value={select_value})")
                    elif personal_shopper_prop.get('type') == 'checkbox':
                        checkbox_value = personal_shopper_prop.get('checkbox', False)
                        personal_shopper = 'Sim' if checkbox_value else 'Não'
                        logger_notion.info(f"✅ [NOTION] Personal Shopper checkbox: '{personal_shopper}' para {cliente_nome} (checkbox_value={checkbox_value})")
                    elif personal_shopper_prop.get('type') == 'rich_text':
                        rich_text = personal_shopper_prop.get('rich_text', [])
                        if rich_text and len(rich_text) > 0:
                            personal_shopper = rich_text[0].get('text', {}).get('content', '')
                            logger_notion.info(f"✅ [NOTION] Personal Shopper rich_text: '{personal_shopper}' para {cliente_nome}")
                        else:
                            personal_shopper = ''
                            logger_notion.info(f"⚠️ [NOTION] Personal Shopper rich_text vazio para {cliente_nome}")
                    else:
                        logger_notion.warning(f"⚠️ [NOTION] Personal Shopper tipo desconhecido: {personal_shopper_prop.get('type')} para {cliente_nome}")
                    
                    # Se personal_shopper for string vazia ou None, usar 'Não' como padrão
                    # Mas manter o valor original se for 'true', 'Sim', 'Misto', etc.
                    # IMPORTANTE: Se o valor for 'true', 'Sim', 'Misto', etc., deve ser mantido!
                    logger_notion.info(f"🔍 [NOTION] ANTES da conversão - personal_shopper: '{personal_shopper}' (tipo: {type(personal_shopper).__name__}, bool(personal_shopper)={bool(personal_shopper)})")
                    personal_shopper_final = personal_shopper if personal_shopper else 'Não'
                    
                    # Log final do valor que será usado
                    logger_notion.info(f"🔍 [NOTION] Personal Shopper final para {cliente_nome}: '{personal_shopper_final}' (original: '{personal_shopper}')")
                    
                    # Adicionar atendimento (já filtrado pela API do Notion, mas vamos verificar novamente)
                    # A API já filtra, mas vamos garantir
                    if data_str and data_str >= data_inicio and data_str < data_fim:
                        atendimentos.append({
                            'id': item['id'],
                            'cliente_nome': cliente_nome,
                            'cliente_id': cliente_id,
                            'horario': horario,
                            'data': data_completa,
                            'data_formatada': data_str,
                            'personal_shopper': personal_shopper_final
                        })
                        atendimentos_validos += 1
                        logger_notion.info(f"✅ Atendimento válido: {cliente_nome} - {data_str} {horario} - Personal Shopper: {personal_shopper_final}")
                    else:
                        data_fora_periodo += 1
                        logger_notion.debug(f"⚠️ Atendimento fora do período: {data_str} (período: {data_inicio} a {data_fim})")
                
                # Log de resumo da página
                logger_notion.info(f"📊 Resumo da página: {total_resultados} resultados, {atendimentos_validos} válidos, {chef_nao_encontrado} sem chef, {cliente_nao_encontrado} sem cliente, {data_fora_periodo} fora do período")
                
                # Verificar se há mais páginas
                has_more = data.get('has_more', False)
                next_cursor = data.get('next_cursor')
            
            logger_notion.info(f"📊 Total de atendimentos encontrados: {len(atendimentos)}")
            if len(atendimentos) > 0:
                logger_notion.info(f"📋 Atendimentos: {', '.join([f'{a['cliente_nome']} ({a['data_formatada']})' for a in atendimentos[:5]])}")
            return atendimentos
        
        except requests.Timeout:
            print(f"⏱️ TIMEOUT ao buscar atendimentos: A requisição demorou mais de 10 segundos")
            return []
        except Exception as e:
            print(f"❌ ERRO ao buscar atendimentos: {e}")
            return []
    
    async def buscar_nome_cliente(self, cliente_id: str) -> str:
        """
        Busca o nome de um cliente pelo ID
        """
        url = f"https://api.notion.com/v1/pages/{cliente_id}"
        
        try:
            # Executar requisição em thread separada para não bloquear event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, headers=self.headers, timeout=10)
            )
            response.raise_for_status()
            data = response.json()
            
            # Tentar pegar o nome do cliente
            name_prop = data['properties'].get('Name', {})
            if name_prop.get('title') and len(name_prop['title']) > 0:
                nome = name_prop['title'][0]['text']['content']
                return nome
            
            return "Cliente Desconhecido"
        
        except requests.Timeout:
            print(f"⏱️ TIMEOUT ao buscar nome do cliente: A requisição demorou mais de 10 segundos")
            return "Cliente Desconhecido"
        except Exception as e:
            print(f"⚠️ Erro ao buscar nome do cliente: {e}")
            return "Cliente Desconhecido"
    
    async def buscar_cliente_por_nome(self, nome_cliente: str) -> Optional[Dict]:
        """
        Busca cliente no Notion pelo nome exato
        """
        url = f"https://api.notion.com/v1/databases/{NOTION_CLIENTES_DB}/query"
        
        payload = {
            "filter": {
                "property": "Name",
                "title": {
                    "equals": nome_cliente
                }
            }
        }
        
        try:
            # Executar requisição em thread separada para não bloquear event loop
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.post(url, headers=self.headers, json=payload, timeout=10)
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                cliente = data['results'][0]
                return {
                    'id': cliente['id'],
                    'nome': cliente['properties']['Name']['title'][0]['text']['content'],
                    'encontrado': True
                }
            
            return None
        
        except requests.Timeout:
            print(f"⏱️ TIMEOUT ao buscar cliente: A requisição demorou mais de 10 segundos")
            return None
        except Exception as e:
            print(f"❌ Erro ao buscar cliente: {e}")
            return None


# ===== FUNÇÕES DE COMPATIBILIDADE (versão antiga) =====
# Mantidas para não quebrar código existente

def buscar_chef_por_telegram(telegram_id, telegram_username):
    """
    Versão síncrona - mantida para compatibilidade
    """
    url = f"https://api.notion.com/v1/databases/{NOTION_CHEFS_DB}/query"
    
    username_limpo = telegram_username.replace('@', '') if telegram_username else ''
    
    payload = {
        "filter": {
            "property": "Telegram Username",
            "rich_text": {
                "equals": username_limpo
            }
        }
    }
    
    try:
        response = requests.post(url, headers=NOTION_HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            chef = data['results'][0]
            nome_completo = chef['properties'].get('Nome Completo', {})
            if nome_completo.get('title') and len(nome_completo['title']) > 0:
                nome = nome_completo['title'][0]['text']['content']
            else:
                nome = "Nome não encontrado"
            
            return {
                'id': chef['id'],
                'nome': nome,
                'encontrado': True
            }
        
        return {'encontrado': False}
    
    except Exception as e:
        print(f"❌ ERRO ao buscar chef: {e}")
        return {'encontrado': False, 'erro': str(e)}


def buscar_atendimentos_hoje(chef_id):
    """
    Versão síncrona - mantida para compatibilidade
    """
    url = f"https://api.notion.com/v1/databases/{NOTION_CALENDARIO_DB}/query"
    
    hoje = datetime.now()
    sete_dias_atras = hoje - timedelta(days=7)
    
    data_inicio = sete_dias_atras.strftime("%Y-%m-%d")
    data_fim = (hoje + timedelta(days=1)).strftime("%Y-%m-%d")
    
    payload = {
        "filter": {
            "and": [
                {
                    "property": "Date",
                    "date": {
                        "on_or_after": data_inicio,
                        "before": data_fim
                    }
                },
                {
                    "property": "Chef Alocado",
                    "relation": {
                        "contains": chef_id
                    }
                }
            ]
        },
        "sorts": [
            {
                "property": "Date",
                "direction": "descending"
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=NOTION_HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        
        atendimentos = []
        for item in data.get('results', []):
            props = item['properties']
            cliente_relation = props.get('Quem é', {}).get('relation', [])
            if not cliente_relation:
                continue
            
            cliente_id = cliente_relation[0]['id']
            cliente_nome = buscar_nome_cliente(cliente_id)
            
            date_obj = props.get('Date', {}).get('date', {})
            data_completa = date_obj.get('start', '')
            
            if 'T' in data_completa:
                data_str = data_completa.split('T')[0]
                horario = data_completa.split('T')[1][:5]
            else:
                data_str = data_completa
                horario = '??:??'
            
            atendimentos.append({
                'id': item['id'],
                'cliente_nome': cliente_nome,
                'cliente_id': cliente_id,
                'horario': horario,
                'data': data_completa,
                'data_formatada': data_str
            })
        
        return atendimentos
    
    except Exception as e:
        print(f"❌ ERRO ao buscar atendimentos: {e}")
        return []


def buscar_nome_cliente(cliente_id):
    """
    Versão síncrona - mantida para compatibilidade
    """
    url = f"https://api.notion.com/v1/pages/{cliente_id}"
    
    try:
        response = requests.get(url, headers=NOTION_HEADERS)
        response.raise_for_status()
        data = response.json()
        
        name_prop = data['properties'].get('Name', {})
        if name_prop.get('title') and len(name_prop['title']) > 0:
            nome = name_prop['title'][0]['text']['content']
            return nome
        
        return "Cliente Desconhecido"
    
    except Exception as e:
        print(f"⚠️ Erro ao buscar nome do cliente: {e}")
        return "Cliente Desconhecido"


def buscar_cliente_por_nome(nome_cliente):
    """
    Versão síncrona - mantida para compatibilidade
    """
    url = f"https://api.notion.com/v1/databases/{NOTION_CLIENTES_DB}/query"
    
    payload = {
        "filter": {
            "property": "Name",
            "title": {
                "equals": nome_cliente
            }
        }
    }
    
    try:
        response = requests.post(url, headers=NOTION_HEADERS, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            cliente = data['results'][0]
            return {
                'id': cliente['id'],
                'nome': cliente['properties']['Name']['title'][0]['text']['content'],
                'encontrado': True
            }
        
        return {'encontrado': False}
    
    except Exception as e:
        print(f"❌ Erro ao buscar cliente: {e}")
        return {'encontrado': False, 'erro': str(e)}
