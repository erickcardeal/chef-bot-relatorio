#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bot Telegram @PaulBotuse - Chef FoodTech
Sistema de coleta de relatórios pós-visita dos chefs
"""

import os
import logging
from datetime import datetime, timedelta, timezone
import pytz
import asyncio
from typing import Dict, List, Optional, Any
import json
import base64
import re
import aiohttp
import ssl
from io import BytesIO

from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
    ApplicationHandlerStop,
    JobQueue
)

from config import (
    TELEGRAM_TOKEN,
    N8N_WEBHOOK_URL,
    N8N_WEBHOOK_URL_FASE1,
    N8N_WEBHOOK_URL_FASE2,
    N8N_WEBHOOK_URL_FASE2A,
    N8N_WEBHOOK_URL_FASE2B,
    NOTION_API_KEY,
    NOTION_DATABASE_ID,
    NOTION_CALENDAR_DB_ID,
    NOTION_CHEFS_DB_ID
)
from notion_api import NotionAPI

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Estados da conversa
(SELECIONAR_ATENDIMENTO, HORARIO_CHEGADA, HORARIO_SAIDA, COMO_FOI_VISITA,
 COMENTARIO_CLIENTE, DETALHE_COMENTARIO, PROBLEMA_ESPECIFICO, DETALHE_PROBLEMA,
 PORCOES_EXATAS, MOTIVO_PORCOES, INVENTARIO_OPCAO, INVENTARIO_TEXTO,
 INVENTARIO_FOTO, CONFIRMAR_INVENTARIO, CORRIGIR_INVENTARIO, DESCARTE,
 ITENS_DESCARTADOS, PODE_VENCER, ITENS_PODEM_VENCER, FOTO_ENTRADA, FOTO_SAIDA,
 RESUMO_FASE1, CONFIRMACAO_FASE1, CONFIRMACAO_FINAL) = range(24)

# Dicionário global para armazenar fotos de álbuns por media_group_id e user_id
# Estrutura: {user_id: {media_group_id: {'updates': [Update, ...], 'processed': bool, 'task': Task}}}
album_collector: Dict[int, Dict[str, Dict[str, Any]]] = {}

# Dicionário global para rastrear última atividade do usuário e jobs de timeout
# Estrutura: {user_id: {'last_activity': datetime, 'timeout_warning_job': Job, 'timeout_end_job': Job}}
user_activity: Dict[int, Dict[str, Any]] = {}

# Timezone Brasil
BR_TZ = pytz.timezone('America/Sao_Paulo')

def criar_ssl_connector():
    """Criar connector SSL com verificação desabilitada para n8n"""
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return aiohttp.TCPConnector(ssl=ssl_context)

class ChefBot:
    def __init__(self):
        """Inicializar o bot com API do Notion"""
        self.notion = NotionAPI(NOTION_API_KEY)
        self.user_data: Dict[str, Dict] = {}
    
    def atualizar_atividade_usuario(self, user_id: int):
        """Atualizar timestamp da última atividade do usuário e cancelar jobs de timeout"""
        agora = datetime.now(BR_TZ)
        if user_id not in user_activity:
            user_activity[user_id] = {}
        
        user_activity[user_id]['last_activity'] = agora
        
        # Cancelar jobs de timeout existentes
        if 'timeout_warning_job' in user_activity[user_id] and user_activity[user_id]['timeout_warning_job']:
            try:
                user_activity[user_id]['timeout_warning_job'].schedule_removal()
            except:
                pass
        
        if 'timeout_end_job' in user_activity[user_id] and user_activity[user_id]['timeout_end_job']:
            try:
                user_activity[user_id]['timeout_end_job'].schedule_removal()
            except:
                pass
        
        logger.debug(f"⏱️ Atividade atualizada para usuário {user_id}")
    
    async def verificar_timeout_warning(self, context: ContextTypes.DEFAULT_TYPE):
        """Verificar se usuário está inativo há 2 minutos e enviar aviso"""
        user_id = context.job.data.get('user_id')
        chat_id = context.job.data.get('chat_id')
        
        if user_id not in user_activity:
            return
        
        ultima_atividade = user_activity[user_id].get('last_activity')
        if not ultima_atividade:
            return
        
        # Verificar se ainda está inativo (2 minutos)
        agora = datetime.now(BR_TZ)
        tempo_inativo = (agora - ultima_atividade).total_seconds()
        
        if tempo_inativo >= 120:  # 2 minutos
            logger.info(f"⏱️ Usuário {user_id} inativo há {tempo_inativo:.0f}s - enviando aviso")
            
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="👋 Olá! Você ainda está aí?\n\n"
                         "Se você não responder nos próximos 60 segundos, vou encerrar esta conversa."
                )
                
                # Agendar job para encerrar conversa após 60s
                job_queue = context.job_queue
                if job_queue:
                    end_job = job_queue.run_once(
                        self.encerrar_conversa_timeout,
                        when=60,  # 60 segundos
                        data={'user_id': user_id, 'chat_id': chat_id}
                    )
                    user_activity[user_id]['timeout_end_job'] = end_job
            except Exception as e:
                logger.error(f"❌ Erro ao enviar aviso de timeout: {e}")
        else:
            # Ainda não completou 2 minutos, reagendar verificação
            tempo_restante = 120 - tempo_inativo
            if tempo_restante > 0:
                job_queue = context.job_queue
                if job_queue:
                    warning_job = job_queue.run_once(
                        self.verificar_timeout_warning,
                        when=int(tempo_restante),
                        data={'user_id': user_id, 'chat_id': chat_id}
                    )
                    user_activity[user_id]['timeout_warning_job'] = warning_job
    
    async def encerrar_conversa_timeout(self, context: ContextTypes.DEFAULT_TYPE):
        """Encerrar conversa após timeout"""
        user_id = context.job.data.get('user_id')
        chat_id = context.job.data.get('chat_id')
        
        if user_id not in user_activity:
            return
        
        ultima_atividade = user_activity[user_id].get('last_activity')
        if not ultima_atividade:
            return
        
        # Verificar se ainda está inativo (3 minutos total = 2min + 60s)
        agora = datetime.now(BR_TZ)
        tempo_inativo = (agora - ultima_atividade).total_seconds()
        
        if tempo_inativo >= 180:  # 3 minutos total
            logger.info(f"⏱️ Encerrando conversa do usuário {user_id} por timeout ({tempo_inativo:.0f}s inativo)")
            
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="⏱️ Vou encerrar sua conversa, ok? Caso você precise enviar outro relatório, basta iniciar novamente a conversa.",
                    reply_markup=ReplyKeyboardRemove()
                )
                
                # Limpar dados do usuário
                if user_id in user_activity:
                    del user_activity[user_id]
            except Exception as e:
                logger.error(f"❌ Erro ao encerrar conversa por timeout: {e}")
    
    def agendar_verificacao_timeout(self, user_id: int, chat_id: int, job_queue: JobQueue):
        """Agendar verificação de timeout para o usuário"""
        if not job_queue:
            return
        
        # Agendar verificação após 2 minutos (120 segundos)
        warning_job = job_queue.run_once(
            self.verificar_timeout_warning,
            when=120,  # 2 minutos
            data={'user_id': user_id, 'chat_id': chat_id}
        )
        
        if user_id not in user_activity:
            user_activity[user_id] = {}
        
        user_activity[user_id]['timeout_warning_job'] = warning_job
        user_activity[user_id]['last_activity'] = datetime.now(BR_TZ)
        logger.debug(f"⏱️ Verificação de timeout agendada para usuário {user_id} (2 minutos)")
    
    def atualizar_atividade_handler(self, update: Update):
        """Helper para atualizar atividade em handlers"""
        if update and update.effective_user:
            self.atualizar_atividade_usuario(update.effective_user.id)
    
    def reagendar_timeout_apos_mensagem(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Reagendar timeout após bot enviar mensagem esperando resposta"""
        if not update or not update.effective_user:
            return
        
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id if update.effective_chat else None
        
        if not chat_id or not context.job_queue:
            return
        
        # Atualizar atividade e reagendar timeout
        self.atualizar_atividade_usuario(user_id)
        self.agendar_verificacao_timeout(user_id, chat_id, context.job_queue)
    
    def precisa_inventario(self, personal_shopper: str) -> bool:
        """Verificar se precisa de inventário baseado no personal_shopper"""
        if not personal_shopper:
            return True  # Por padrão, precisa de inventário se não especificado
        
        # Normalizar: remover espaços, converter para minúsculas e remover acentos
        valor_normalizado = personal_shopper.strip().lower()
        
        # Remover acentos (caso comum: "não" vs "nao")
        valor_normalizado = valor_normalizado.replace('ã', 'a').replace('õ', 'o')
        
        # Valores que indicam que NÃO precisa de inventário
        valores_sem_inventario = ['não', 'nao', 'no', 'n', 'false', '0', '']
        
        # Se o valor normalizado está na lista, NÃO precisa de inventário
        return valor_normalizado not in valores_sem_inventario
    
    def format_date(self, date_str: str) -> str:
        """Formatar data para exibição"""
        try:
            # Se a data já está no formato YYYY-MM-DD, converter diretamente
            if len(date_str) == 10 and date_str.count('-') == 2:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                return date.strftime('%d/%m/%Y')
            # Se está em formato ISO, converter
            elif 'T' in date_str:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date.strftime('%d/%m/%Y')
            else:
                # Tentar parsear como ISO
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date.strftime('%d/%m/%Y')
        except:
            # Se falhar, retornar como está ou formato básico
            return date_str
    
    def format_time(self, time_str: str) -> str:
        """Formatar horário para formato brasileiro"""
        try:
            # Se já está no formato HH:MM, retorna como está
            if re.match(r'^\d{2}:\d{2}$', time_str):
                return time_str
            # Se está em formato ISO, converte
            time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            return time.strftime('%H:%M')
        except:
            return time_str

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Comando /relatorio - Iniciar conversa e identificar chef"""
        user = update.effective_user
        username = user.username
        user_id = user.id
        chat_id = update.effective_chat.id
        
        # Atualizar atividade e agendar verificação de timeout
        self.atualizar_atividade_usuario(user_id)
        if context.job_queue:
            self.agendar_verificacao_timeout(user_id, chat_id, context.job_queue)
        
        logger.info(f"🔵 Chef iniciou conversa: @{username} (ID: {user_id})")
        
        # Buscar chef no Notion pelo username (sem @)
        logger.info(f"🔄 Buscando chef no Notion para @{username}...")
        try:
            chef_data = await self.notion.buscar_chef_por_telegram(username)
            logger.info(f"✅ Chef encontrado: {chef_data.get('nome', 'N/A') if chef_data else 'None'}")
        except Exception as e:
            logger.error(f"❌ Erro ao buscar chef: {e}", exc_info=True)
            chef_data = None
        
        if not chef_data:
            logger.warning(f"⚠️ Chef não encontrado para @{username}")
            await update.message.reply_text(
                "❌ Chef não encontrado no sistema.\n\n"
                "Por favor, entre em contato com o time de tecnologia para resolver este problema."
            )
            return ConversationHandler.END
        
        # Salvar dados do chef no contexto
        context.user_data['chef'] = chef_data
        context.user_data['chef_id'] = chef_data['id']
        context.user_data['chef_nome'] = chef_data['nome']
        context.user_data['telegram_user'] = username
        
        # Buscar atendimentos dos últimos 7 dias
        chef_id = context.user_data['chef_id']
        logger.info(f"🔄 Buscando atendimentos para chef {chef_id[:8]}... (últimos 7 dias)")
        try:
            atendimentos = await self.notion.buscar_atendimentos_chef(chef_id, dias=7)
            logger.info(f"✅ Atendimentos encontrados: {len(atendimentos) if atendimentos else 0}")
        except Exception as e:
            logger.error(f"❌ Erro ao buscar atendimentos: {e}", exc_info=True)
            atendimentos = []
        
        # Salvar atendimentos no contexto
        context.user_data['atendimentos'] = atendimentos or []
        
        # Verificar se há atendimentos
        if not atendimentos:
            logger.info(f"⚠️ Nenhum atendimento encontrado para @{username}")
            await update.message.reply_text(
                f"Olá, {chef_data['nome']}! Tudo bem? 👋\n\n"
                "📭 Não encontrei atendimentos registrados nos últimos 7 dias.\n"
                "Se isso estiver incorreto, entre em contato com o time de tecnologia."
            )
            return ConversationHandler.END
        
        # Criar teclado com os atendimentos
        keyboard = []
        for atend in atendimentos:
            cliente = atend['cliente_nome']
            horario = atend.get('horario', '')
            
            # Usar data_formatada se existir, senão formatar a data completa
            if atend.get('data_formatada'):
                data_display = self.format_date(atend['data_formatada'])
            else:
                data_display = self.format_date(atend.get('data', ''))
            
            if horario and horario != '??:??':
                keyboard.append([f"{cliente} - {horario}"])
            else:
                keyboard.append([f"{cliente} - {data_display}"])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        # Mensagem inicial
        logger.info(f"📤 Enviando mensagem inicial para @{username}...")
        mensagem_inicial = (
            f"E aí {chef_data['nome']}, tudo bem?\n\n"
            f"Bora fazer o relatório de visita? Vou te ajudar em todo o processo. "
            f"Vamos iniciar com as informações gerais do atendimento e depois disso vamos para o inventário, ok?"
        )
        
        try:
            await update.message.reply_text(
                mensagem_inicial,
                reply_markup=ReplyKeyboardRemove()
            )
            logger.info(f"✅ Mensagem inicial enviada para @{username}")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem inicial: {e}", exc_info=True)
            return ConversationHandler.END
        
        # Mensagem de busca no sistema
        qtd_atendimentos = len(atendimentos)
        logger.info(f"📤 Enviando mensagem de atendimentos para @{username}... ({qtd_atendimentos} atendimentos sem relatório)")
        mensagem = (
            f"Chequei aqui no sistema e você tem {qtd_atendimentos} atendimento{'s' if qtd_atendimentos > 1 else ''} nos últimos 7 dias sem relatório.\n\n"
            "Qual deles você quer enviar o relatório?"
        )
        
        try:
            await update.message.reply_text(
                mensagem,
                reply_markup=reply_markup
            )
            logger.info(f"✅ Mensagem de atendimentos enviada para @{username}")
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem de atendimentos: {e}", exc_info=True)
            return ConversationHandler.END
        
        return SELECIONAR_ATENDIMENTO

    async def selecionar_atendimento(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Selecionar atendimento para relatar"""
        # Atualizar atividade
        self.atualizar_atividade_usuario(update.effective_user.id)
        
        texto = update.message.text
        
        # Extrair nome do cliente (antes do " - ")
        cliente_nome = texto.split(" - ")[0]
        
        # Buscar o atendimento correspondente
        atendimento = None
        for atend in context.user_data.get('atendimentos', []):
            if atend['cliente_nome'] == cliente_nome:
                atendimento = atend
                break
        
        if not atendimento:
            await update.message.reply_text(
                "❌ Erro ao identificar atendimento.\n"
                "Por favor, entre em contato com o time de tecnologia."
            )
            return ConversationHandler.END
        
        # Salvar dados do atendimento (incluindo Personal Shopper)
        context.user_data['cliente_nome'] = atendimento['cliente_nome']
        context.user_data['cliente_id'] = atendimento.get('cliente_id', '')
        context.user_data['atendimento_id'] = atendimento.get('id', '')
        context.user_data['data_atendimento'] = atendimento.get('data', datetime.now(BR_TZ).strftime("%Y-%m-%d"))
        context.user_data['personal_shopper'] = atendimento.get('personal_shopper', 'Não')
        
        # Inicializar estrutura de dados do relatório
        context.user_data['relatorio'] = {
            'chef_id': context.user_data['chef_id'],
            'chef_nome': context.user_data['chef_nome'],
            'cliente_nome': atendimento['cliente_nome'],
            'cliente_id': atendimento.get('cliente_id', ''),
            'atendimento_id': atendimento.get('id', ''),
            'data_atendimento': atendimento.get('data', datetime.now(BR_TZ).strftime("%Y-%m-%d")),
            'timestamp_inicio': datetime.now(BR_TZ).isoformat(),
            'personal_shopper': atendimento.get('personal_shopper', 'Não')
        }
        
        logger.info(f"📋 Atendimento selecionado: {cliente_nome} - Personal Shopper: {atendimento.get('personal_shopper', 'Não')}")
        
        await update.message.reply_text(
            "Qual foi o horário de chegada?",
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Reagendar timeout após enviar mensagem esperando resposta
        self.reagendar_timeout_apos_mensagem(update, context)
        
        return HORARIO_CHEGADA

    async def horario_chegada(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Registrar horário de chegada"""
        self.atualizar_atividade_handler(update)
        horario = update.message.text.strip()
        
        # Salvar horário de chegada (sem validação rigorosa, normalizar no n8n)
        context.user_data['relatorio']['horario_chegada'] = horario.strip()
        
        await update.message.reply_text(
            "Qual foi o horário de saída?"
        )
        
        # Reagendar timeout após enviar mensagem esperando resposta
        self.reagendar_timeout_apos_mensagem(update, context)
        
        return HORARIO_SAIDA

    async def horario_saida(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Registrar horário de saída"""
        self.atualizar_atividade_handler(update)
        horario = update.message.text.strip()
        
        # Salvar horário de saída (sem validação rigorosa, normalizar no n8n)
        context.user_data['relatorio']['horario_saida'] = horario
        
        await update.message.reply_text(
            "De modo geral, como foi a visita?"
        )
        
        # Reagendar timeout após enviar mensagem esperando resposta
        self.reagendar_timeout_apos_mensagem(update, context)
        
        return COMO_FOI_VISITA

    async def como_foi_visita(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber descrição de como foi a visita"""
        self.atualizar_atividade_handler(update)
        context.user_data['relatorio']['como_foi_visita'] = update.message.text
        
        keyboard = [["✅ Sim"], ["❌ Não"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "O cliente fez algum comentário que vai ter impacto nos próximos atendimentos ou nos próximos menus?",
            reply_markup=reply_markup
        )
        
        # Reagendar timeout após enviar mensagem esperando resposta
        self.reagendar_timeout_apos_mensagem(update, context)
        
        return COMENTARIO_CLIENTE

    async def comentario_cliente(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber se há comentário do cliente"""
        resposta = update.message.text
        
        if "Sim" in resposta:
            context.user_data['relatorio']['tem_comentario'] = "Sim"
            await update.message.reply_text(
                "Qual foi o comentário do cliente?",
                reply_markup=ReplyKeyboardRemove()
            )
            # Reagendar timeout após enviar mensagem esperando resposta
            self.reagendar_timeout_apos_mensagem(update, context)
            return DETALHE_COMENTARIO
        else:
            context.user_data['relatorio']['tem_comentario'] = "Não"
            context.user_data['relatorio']['comentario_cliente'] = ""
            
            keyboard = [["✅ Sim"], ["❌ Não"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                "Houve algum problema específico?\n"
                "(Exemplo: equipamento quebrado, falta de utensílio)",
                reply_markup=reply_markup
            )
            return PROBLEMA_ESPECIFICO

    async def detalhe_comentario(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber detalhe do comentário do cliente"""
        context.user_data['relatorio']['comentario_cliente'] = update.message.text
        
        keyboard = [["✅ Sim"], ["❌ Não"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Houve algum problema específico?\n"
            "(Exemplo: equipamento quebrado, falta de utensílio)",
            reply_markup=reply_markup
        )
        return PROBLEMA_ESPECIFICO

    async def problema_especifico(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber se há problema específico"""
        resposta = update.message.text
        
        if "Sim" in resposta:
            context.user_data['relatorio']['tem_problema'] = "Sim"
            await update.message.reply_text(
                "Qual foi o problema específico?",
                reply_markup=ReplyKeyboardRemove()
            )
            return DETALHE_PROBLEMA
        else:
            context.user_data['relatorio']['tem_problema'] = "Não"
            context.user_data['relatorio']['problema_especifico'] = ""
            
            keyboard = [["✅ Sim"], ["❌ Não"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                "⚠️ IMPORTANTE:\n\n"
                "As porções foram produzidas na mesma quantidade da planilha do atendimento?",
                reply_markup=reply_markup
            )
            return PORCOES_EXATAS

    async def detalhe_problema(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber detalhe do problema específico"""
        context.user_data['relatorio']['problema_especifico'] = update.message.text
        
        keyboard = [["✅ Sim"], ["❌ Não"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "⚠️ IMPORTANTE:\n\n"
            "As porções foram produzidas na mesma quantidade da planilha do atendimento?",
            reply_markup=reply_markup
        )
        return PORCOES_EXATAS

    async def porcoes_exatas(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber se porções foram exatas"""
        resposta = update.message.text
        
        if "Sim" in resposta:
            context.user_data['relatorio']['porcoes_exatas'] = "Sim"
            context.user_data['relatorio']['motivo_porcoes'] = ""
        else:
            context.user_data['relatorio']['porcoes_exatas'] = "Não"
            
            await update.message.reply_text(
                "Quais e Por que as porções não foram produzidas de acordo com a quantidade da planilha?",
                reply_markup=ReplyKeyboardRemove()
            )
            
            return MOTIVO_PORCOES
        
        # Após definir porções (exatas ou não), perguntar sobre descarte
        keyboard = [["✅ Sim"], ["❌ Não"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Algum ingrediente foi descartado?",
            reply_markup=reply_markup
        )
        
        return DESCARTE

    async def motivo_porcoes(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber motivo das porções não exatas"""
        context.user_data['relatorio']['motivo_porcoes'] = update.message.text
        
        # Perguntar sobre descarte
        keyboard = [["✅ Sim"], ["❌ Não"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Algum ingrediente foi descartado?",
            reply_markup=reply_markup
        )
        
        return DESCARTE

    async def inventario_opcao(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber inventário (foto ou texto) - FASE 2A (processar imediatamente)"""
        self.atualizar_atividade_handler(update)
        
        # Verifica se é foto
        if update.message.photo:
            # Pegar a foto de maior resolução
            photo_file = await update.message.photo[-1].get_file()
            
            # Baixar foto para BytesIO
            photo_bytes = BytesIO()
            await photo_file.download_to_memory(photo_bytes)
            photo_bytes.seek(0)
            
            # Converter pra base64
            photo_base64 = base64.b64encode(photo_bytes.read()).decode('utf-8')
            
            # Salvar no user_data para processar_inventario usar
            context.user_data['relatorio']['inventario_foto'] = photo_base64
            context.user_data['relatorio']['inventario_texto'] = ""
            context.user_data['inventario_texto'] = ""
            context.user_data['foto_inventario_base64'] = photo_base64
            context.user_data['relatorio']['inventario_atualizado'] = "Sim"
            
            # Processar imediatamente (FASE 2A)
            return await self.processar_inventario(update, context)
        else:
            # É texto - salvar e processar imediatamente
            context.user_data['relatorio']['inventario_texto'] = update.message.text
            context.user_data['relatorio']['inventario_foto'] = None
            context.user_data['inventario_texto'] = update.message.text
            context.user_data['foto_inventario_base64'] = ''
            context.user_data['relatorio']['inventario_atualizado'] = "Sim"
            
            # Processar imediatamente (FASE 2A)
            return await self.processar_inventario(update, context)

    async def processar_inventario(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Processar inventário com n8n FASE 2A (busca fuzzy + Claude se necessário)"""
        self.atualizar_atividade_handler(update)
        
        # Mensagem inicial de processamento
        await update.message.reply_text(
            "🔄 *Processando inventário...*\n"
            "Aguarde enquanto analiso as informações.",
            parse_mode='Markdown'
        )
        
        try:
            # Obter notion_page_id da FASE 1
            notion_page_id = context.user_data['relatorio'].get('notion_page_id')
            if not notion_page_id:
                logger.error("❌ notion_page_id não encontrado no user_data")
                await update.message.reply_text(
                    "❌ *Erro ao processar inventário*\n\n"
                    "Não foi possível encontrar o ID do relatório.\n\n"
                    "Por favor, tente novamente ou entre em contato com o suporte.",
                    parse_mode='Markdown',
                    reply_markup=ReplyKeyboardRemove()
                )
                return INVENTARIO_OPCAO
            
            # Preparar dados para n8n FASE 2A (processar)
            # Buscar inventário do relatorio ou do user_data diretamente
            inventario_texto = context.user_data.get('inventario_texto', '') or context.user_data.get('relatorio', {}).get('inventario_texto', '')
            inventario_foto = context.user_data.get('foto_inventario_base64', '') or context.user_data.get('relatorio', {}).get('inventario_foto', '') or ''
            
            webhook_data = {
                'notion_page_id': notion_page_id,
                'inventario_texto': inventario_texto,
                'foto_inventario_base64': inventario_foto
            }
            
            logger.info(f"📦 Dados para FASE 2A: inventario_texto={len(inventario_texto)} chars, foto={len(inventario_foto) if inventario_foto else 0} chars")
            
            # Webhook FASE 2A (processar) - CORRETO (SEMPRE usar FASE2A, nunca FASE2 ou URL genérica)
            if not N8N_WEBHOOK_URL_FASE2A:
                logger.error("❌ N8N_WEBHOOK_URL_FASE2A não configurado!")
                raise Exception("Webhook FASE 2A não configurado")
            webhook_url_fase2a = N8N_WEBHOOK_URL_FASE2A
            logger.info(f"🔄 Enviando FASE 2A (processar) para webhook: {webhook_url_fase2a}")
            
            # Mensagens de aguarde enquanto processa (similar à FASE 1)
            mensagens_aguarde = [
                "⏳ Analisando ingredientes...",
                "⏳ Normalizando quantidades..."
            ]
            mensagem_aguarde_enviada_1 = False
            mensagem_aguarde_enviada_2 = False
            resposta_recebida = False
            
            async def enviar_mensagem_aguarde(delay: float, mensagem_idx: int):
                """Enviar mensagem de aguarde após delay"""
                nonlocal mensagem_aguarde_enviada_1, mensagem_aguarde_enviada_2, resposta_recebida
                await asyncio.sleep(delay)
                
                # Verificar se ainda não recebeu resposta
                if not resposta_recebida:
                    if mensagem_idx == 1 and not mensagem_aguarde_enviada_1:
                        mensagem_aguarde_enviada_1 = True
                        mensagem = mensagens_aguarde[0]
                        await update.message.reply_text(mensagem)
                        logger.info(f"📤 Mensagem de aguarde 1 enviada após {delay:.1f}s")
                    elif mensagem_idx == 2 and not mensagem_aguarde_enviada_2 and mensagem_aguarde_enviada_1:
                        mensagem_aguarde_enviada_2 = True
                        mensagem = mensagens_aguarde[1]
                        await update.message.reply_text(mensagem)
                        logger.info(f"📤 Mensagem de aguarde 2 enviada após {delay:.1f}s")
            
            # Iniciar tarefas para enviar mensagens de aguarde
            task_mensagem_1 = asyncio.create_task(enviar_mensagem_aguarde(5.0, 1))
            task_mensagem_2 = asyncio.create_task(enviar_mensagem_aguarde(10.0, 2))
            
            # Enviar para n8n FASE 2A processar (busca fuzzy + Claude se necessário)
            connector = criar_ssl_connector()
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    webhook_url_fase2a,
                    json=webhook_data,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    # Marcar que recebeu resposta (evitar enviar mais mensagens de aguarde)
                    resposta_recebida = True
                    
                    # Cancelar tarefas de mensagem de aguarde (já recebeu resposta)
                    task_mensagem_1.cancel()
                    task_mensagem_2.cancel()
                    
                    try:
                        await task_mensagem_1
                    except asyncio.CancelledError:
                        pass
                    try:
                        await task_mensagem_2
                    except asyncio.CancelledError:
                        pass
                    if response.status == 200:
                        resultado = await response.json()
                        
                        # Verificar se houve erro no processamento
                        if not resultado.get('success'):
                            erro_msg = resultado.get('message', 'Erro desconhecido')
                            logger.error(f"❌ Erro no processamento do inventário: {erro_msg}")
                            await update.message.reply_text(
                                "❌ *Erro no processamento do inventário*\n\n"
                                f"Motivo: {erro_msg}\n\n"
                                "Por favor, tente novamente enviando o inventário como TEXTO ou entre em contato com o time de tecnologia.",
                                parse_mode='Markdown',
                                reply_markup=ReplyKeyboardRemove()
                            )
                            
                            # Voltar para solicitar inventário novamente
                            await update.message.reply_text(
                                "Me envie quais foram os ingredientes/insumos que sobraram do último atendimento, seja o mais detalhista possível, pois isso vai impactar no próximo atendimento."
                            )
                            
                            # Reagendar timeout após enviar mensagem esperando resposta
                            self.reagendar_timeout_apos_mensagem(update, context)
                            
                            return INVENTARIO_OPCAO
                        
                        # Processar inventário estruturado (nova estrutura do n8n)
                        inventario_estruturado = resultado.get('inventario_estruturado', [])
                        inventario_visualizacao = resultado.get('inventario_visualizacao', '')
                        temperos_sensiveis = resultado.get('temperos_sensiveis', [])
                        total_ingredientes = resultado.get('total_ingredientes', 0)
                        total_temperos_sensiveis = resultado.get('total_temperos_sensiveis', 0)
                        precisa_revisao_temperos = resultado.get('precisa_revisao_temperos', False)
                        aviso_temperos = resultado.get('aviso_temperos')
                        metodo = resultado.get('metodo', 'parse_simples')
                        precisa_validacao = resultado.get('precisa_validacao', True)
                        
                        # Salvar dados processados (nova estrutura)
                        context.user_data['inventario_processado'] = inventario_estruturado
                        context.user_data['inventario_visualizacao'] = inventario_visualizacao
                        context.user_data['temperos_sensiveis'] = temperos_sensiveis
                        context.user_data['total_ingredientes'] = total_ingredientes
                        context.user_data['total_temperos_sensiveis'] = total_temperos_sensiveis
                        context.user_data['precisa_revisao_temperos'] = precisa_revisao_temperos
                        context.user_data['aviso_temperos'] = aviso_temperos
                        context.user_data['metodo'] = metodo
                        context.user_data['precisa_validacao'] = precisa_validacao
                        
                        logger.info(f"✅ Inventário processado: {total_ingredientes} ingredientes ({total_temperos_sensiveis} temperos sensíveis), método: {metodo}")
                        
                        # Exibir visualização formatada (já vem pronta do n8n com alertas e pergunta de confirmação)
                        # A visualização já inclui tudo: ingredientes, alertas de temperos, e pergunta de confirmação
                        await update.message.reply_text(
                            inventario_visualizacao,
                            parse_mode='Markdown'
                        )
                        
                        # Pedir confirmação com botões (a visualização já pede, mas adicionamos botões para facilitar)
                        keyboard = [
                            ['✅ Está correto'],
                            ['❌ Precisa correção']
                        ]
                        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
                        
                        await update.message.reply_text(
                            "*Confirma que está correto?*",
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                        )
                        
                        return CONFIRMAR_INVENTARIO
                    else:
                        response_text = await response.text()
                        logger.error(f"❌ Erro no webhook FASE 2A: {response.status} - {response_text[:200]}")
                        raise Exception(f"Erro no webhook: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error("⏱️ Timeout ao processar inventário")
            await update.message.reply_text(
                "⏱️ O processamento demorou muito.\n\n"
                "Por favor, tente enviar o inventário como TEXTO ou entre em contato com o time de tecnologia.",
                reply_markup=ReplyKeyboardRemove()
            )
            await update.message.reply_text(
                "Me envie quais foram os ingredientes/insumos que sobraram do último atendimento, seja o mais detalhista possível, pois isso vai impactar no próximo atendimento."
            )
            # Reagendar timeout após enviar mensagem esperando resposta
            self.reagendar_timeout_apos_mensagem(update, context)
            return INVENTARIO_OPCAO
        except Exception as e:
            logger.error(f"❌ Erro ao processar inventário: {e}", exc_info=True)
            await update.message.reply_text(
                "❌ Erro ao processar inventário.\n\n"
                "Por favor, tente enviar o inventário como TEXTO ou entre em contato com o time de tecnologia.",
                reply_markup=ReplyKeyboardRemove()
            )
            await update.message.reply_text(
                "Me envie quais foram os ingredientes/insumos que sobraram do último atendimento, seja o mais detalhista possível, pois isso vai impactar no próximo atendimento."
            )
            # Reagendar timeout após enviar mensagem esperando resposta
            self.reagendar_timeout_apos_mensagem(update, context)
            return INVENTARIO_OPCAO

    async def confirmar_inventario(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Confirmar ou corrigir inventário processado (FASE 2A) e salvar no Notion (FASE 2B)"""
        self.atualizar_atividade_handler(update)
        resposta = update.message.text
        
        if '✅' in resposta:
            # Inventário confirmado, salvar no Notion (FASE 2B)
            try:
                # Obter notion_page_id da FASE 1
                notion_page_id = context.user_data['relatorio'].get('notion_page_id')
                if not notion_page_id:
                    logger.error("❌ notion_page_id não encontrado no user_data")
                    await update.message.reply_text(
                        "❌ *Erro ao salvar inventário*\n\n"
                        "Não foi possível encontrar o ID do relatório.\n\n"
                        "Por favor, tente novamente ou entre em contato com o suporte.",
                        parse_mode='Markdown',
                        reply_markup=ReplyKeyboardRemove()
                    )
                    return CONFIRMAR_INVENTARIO
                
                # Preparar dados para n8n FASE 2B (salvar) - nova estrutura
                webhook_data = {
                    'notion_page_id': notion_page_id,
                    'inventario_estruturado': context.user_data.get('inventario_processado', []),
                    'inventario_visualizacao': context.user_data.get('inventario_visualizacao', ''),
                    'total_ingredientes': context.user_data.get('total_ingredientes', 0),
                    'temperos_sensiveis': context.user_data.get('temperos_sensiveis', []),
                    'total_temperos_sensiveis': context.user_data.get('total_temperos_sensiveis', 0),
                    'precisa_revisao_temperos': context.user_data.get('precisa_revisao_temperos', False),
                    'aviso_temperos': context.user_data.get('aviso_temperos'),
                    'metodo': context.user_data.get('metodo', 'parse_simples'),
                    'status': 'confirmado'
                }
                
                # Webhook FASE 2B (salvar) - CORRETO (SEMPRE usar FASE2B, nunca URL genérica)
                if not N8N_WEBHOOK_URL_FASE2B:
                    logger.error("❌ N8N_WEBHOOK_URL_FASE2B não configurado!")
                    raise Exception("Webhook FASE 2B não configurado")
                webhook_url_fase2b = N8N_WEBHOOK_URL_FASE2B
                logger.info(f"🔄 Enviando FASE 2B (salvar) para webhook: {webhook_url_fase2b}")
                logger.info(f"📦 Dados para FASE 2B: {webhook_data['total_ingredientes']} ingredientes, {webhook_data['total_temperos_sensiveis']} temperos sensíveis")
                
                # Mostrar mensagem de processamento
                await update.message.reply_text(
                    "💾 *Terminando de selar o frango....*\n"
                    "Aguarde um momento.",
                    parse_mode='Markdown'
                )
                
                # Enviar para n8n FASE 2B salvar (atualizar página no Notion)
                connector = criar_ssl_connector()
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.post(
                        webhook_url_fase2b,
                        json=webhook_data,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 200:
                            resultado = await response.json()
                            
                            # Verificar se houve erro no salvamento
                            if not resultado.get('success'):
                                erro_msg = resultado.get('message', 'Erro desconhecido')
                                logger.error(f"❌ Erro ao salvar inventário: {erro_msg}")
                                await update.message.reply_text(
                                    "❌ *Erro ao salvar inventário*\n\n"
                                    f"Motivo: {erro_msg}\n\n"
                                    "Por favor, tente novamente ou entre em contato com o suporte.",
                                    parse_mode='Markdown',
                                    reply_markup=ReplyKeyboardRemove()
                                )
                                return CONFIRMAR_INVENTARIO
                            
                            # Inventário salvo com sucesso
                            notion_url = resultado.get('notion_url', '')
                            logger.info(f"✅ Inventário salvo com sucesso! Notion URL: {notion_url}")
                            
                            # Mensagem de sucesso
                            mensagem_sucesso = "✅ *Relatório finalizado!*\n\n"
                            mensagem_sucesso += "Caso você queira enviar outro relatório de visita, basta iniciar novamente o chat.\n\n"
                            mensagem_sucesso += "Let's cook!"
                            
                            await update.message.reply_text(
                                mensagem_sucesso,
                                parse_mode='Markdown',
                                reply_markup=ReplyKeyboardRemove()
                            )
                            
                            # Limpar dados
                            context.user_data.clear()
                            return ConversationHandler.END
                        else:
                            response_text = await response.text()
                            logger.error(f"❌ Erro no webhook FASE 2B: {response.status} - {response_text[:200]}")
                            raise Exception(f"Erro no webhook: {response.status}")
                            
            except asyncio.TimeoutError:
                logger.error("⏱️ Timeout ao salvar inventário")
                await update.message.reply_text(
                    "⏱️ O salvamento demorou muito.\n\n"
                    "Por favor, tente novamente ou entre em contato com o suporte.",
                    parse_mode='Markdown',
                    reply_markup=ReplyKeyboardRemove()
                )
                return CONFIRMAR_INVENTARIO
            except Exception as e:
                logger.error(f"❌ Erro ao salvar inventário: {e}", exc_info=True)
                await update.message.reply_text(
                    "❌ Erro ao salvar inventário.\n\n"
                    "Por favor, tente novamente ou entre em contato com o suporte.",
                    parse_mode='Markdown',
                    reply_markup=ReplyKeyboardRemove()
                )
                return CONFIRMAR_INVENTARIO
        else:
            # Precisa correção - pedir texto corrigido
            await update.message.reply_text(
                "✏️ *Digite o inventário corrigido:*\n\n"
                "Exemplo: 500g arroz branco, 2 tomates italianos, meio pacote macarrão penne\n\n"
                "Ou digite a lista completa:",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Reagendar timeout após enviar mensagem esperando resposta
            self.reagendar_timeout_apos_mensagem(update, context)
            
            return INVENTARIO_TEXTO


    async def descarte(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber se houve descarte"""
        resposta = update.message.text
        
        if "Sim" in resposta:
            context.user_data['relatorio']['descarte'] = "Sim"
            
            await update.message.reply_text(
                "Quais ingredientes foram descartados e por quê?\n\n"
                "(Exemplo: Frango vencido, Alface murcha)",
                reply_markup=ReplyKeyboardRemove()
            )
            
            return ITENS_DESCARTADOS
        else:
            context.user_data['relatorio']['descarte'] = "Não"
            context.user_data['relatorio']['itens_descartados'] = ""
            
            keyboard = [["✅ Sim"], ["❌ Não"]]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            
            await update.message.reply_text(
                "Algum ingrediente possivelmente NÃO vai durar até o próximo atendimento?",
                reply_markup=reply_markup
            )
            
            return PODE_VENCER

    async def itens_descartados(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber quais itens foram descartados"""
        context.user_data['relatorio']['itens_descartados'] = update.message.text
        
        keyboard = [["✅ Sim"], ["❌ Não"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            "Algum ingrediente possivelmente NÃO vai durar até o próximo atendimento?",
            reply_markup=reply_markup
        )
        
        return PODE_VENCER

    async def pode_vencer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber se tem itens que podem vencer"""
        resposta = update.message.text
        
        if "Sim" in resposta:
            context.user_data['relatorio']['pode_vencer'] = "Sim"
            
            await update.message.reply_text(
                "Quais ingredientes podem vencer?\n\n"
                "(Exemplo: Iogurte vence em 2 dias, Peixe na geladeira)",
                reply_markup=ReplyKeyboardRemove()
            )
            
            return ITENS_PODEM_VENCER
        else:
            context.user_data['relatorio']['pode_vencer'] = "Não"
            context.user_data['relatorio']['itens_podem_vencer'] = ""
            
            # Após coletar todos os dados básicos, pedir fotos
            await update.message.reply_text(
                "📸 *Foto de Entrada*\n\n"
                "Agora você deve enviar a foto do início do seu atendimento: fogão, geladeira, pia e estado geral da cozinha.\n\n"
                "💡 Você pode enviar mais de uma foto.",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove()
            )
            
            # Reagendar timeout após enviar mensagem esperando resposta
            self.reagendar_timeout_apos_mensagem(update, context)
            
            return FOTO_ENTRADA

    async def itens_podem_vencer(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber quais itens podem vencer"""
        context.user_data['relatorio']['itens_podem_vencer'] = update.message.text
        
        # Após coletar todos os dados básicos, pedir fotos
        await update.message.reply_text(
            "📸 *Foto de Entrada*\n\n"
            "Agora você deve enviar a foto do início do seu atendimento: fogão, geladeira, pia e estado geral da cozinha.\n\n"
            "💡 Você pode enviar mais de uma foto.",
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardRemove()
        )
        
        # Reagendar timeout após enviar mensagem esperando resposta
        self.reagendar_timeout_apos_mensagem(update, context)
        
        return FOTO_ENTRADA

    async def foto_entrada(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber foto de entrada - ACEITA AUTOMATICAMENTE"""
        if not update.message.photo:
            await update.message.reply_text(
                "❌ Por favor, envie uma FOTO da entrada."
            )
            return FOTO_ENTRADA
        
        # Verificar se é um álbum (múltiplas fotos)
        is_album = update.message.media_group_id is not None
        media_group_id = update.message.media_group_id
        
        if is_album:
            # Verificar se há fotos coletadas pelo handler global
            user_id = update.effective_user.id
            message_id = update.message.message_id
            
            logger.info(f"🔍 [FOTO ENTRADA] Foto recebida - message_id: {message_id}, media_group_id: {media_group_id}, estado_atual: FOTO_ENTRADA")
            
            # Verificar se o álbum já foi processado pelo handler global
            if user_id in album_collector and media_group_id in album_collector[user_id]:
                album_data = album_collector[user_id][media_group_id]
                
                # Verificar se já foi processado
                if album_data.get('processed', False) and 'fotos_processadas' in album_data:
                    # Álbum já foi processado - usar fotos coletadas
                    fotos_processadas = album_data['fotos_processadas']
                    qtd_fotos = len(fotos_processadas)
                    
                    logger.info(f"✅ Álbum já processado! Usando {qtd_fotos} foto(s) coletada(s) (media_group_id: {media_group_id})")
                    
                    # Atualizar relatório com todas as fotos
                    context.user_data['relatorio']['fotos_entrada'] = fotos_processadas
                    context.user_data['relatorio']['foto_entrada'] = fotos_processadas[0]['base64']
                    
                    # Enviar mensagem de confirmação e pedir foto de saída (apenas uma vez)
                    if not album_data.get('message_sent', False):
                        # Mensagem dinâmica baseada na quantidade de fotos
                        if qtd_fotos == 1:
                            mensagem_confirmacao = "✅ 1 foto de entrada recebida!\n\n"
                        else:
                            mensagem_confirmacao = f"✅ {qtd_fotos} fotos de entrada recebidas!\n\n"
                        
                        await update.message.reply_text(
                            mensagem_confirmacao +
                            "📸 *Foto de SAÍDA*\n\n"
                            "Agora envie uma foto da cozinha/área de trabalho de quando você SAIU e deixou tudo organizado.\n\n"
                            "💡 Você pode enviar uma ou várias fotos.",
                            parse_mode='Markdown'
                        )
                        album_data['message_sent'] = True
                        logger.info(f"✅ Mensagem de confirmação enviada para álbum (media_group_id: {media_group_id}, {qtd_fotos} foto(s))")
                    
                    # Não limpar álbum do coletor aqui - deixar para o handler global bloquear outras fotos
                    # O álbum será limpo automaticamente após um tempo ou quando não houver mais fotos
                    
                    # Mudar para estado FOTO_SAIDA
                    return FOTO_SAIDA
                else:
                    # Álbum ainda está sendo processado - aguardar mais tempo
                    logger.info(f"⏳ Álbum ainda sendo processado... Aguardando fotos coletadas (media_group_id: {media_group_id})")
                    # Aguardar até 5 segundos, verificando a cada 0.5 segundos se foi processado
                    tempo_max_espera = 5.0  # 5 segundos
                    intervalo_verificacao = 0.5  # Verificar a cada 0.5 segundos
                    tempo_espera_total = 0.0
                    
                    while tempo_espera_total < tempo_max_espera:
                        await asyncio.sleep(intervalo_verificacao)
                        tempo_espera_total += intervalo_verificacao
                        
                        # Verificar se foi processado
                        if user_id in album_collector and media_group_id in album_collector[user_id]:
                            album_data = album_collector[user_id][media_group_id]
                            if album_data.get('processed', False) and 'fotos_processadas' in album_data:
                                # Agora foi processado - usar fotos coletadas
                                fotos_processadas = album_data['fotos_processadas']
                                qtd_fotos = len(fotos_processadas)
                                
                                logger.info(f"✅ Álbum processado após espera ({tempo_espera_total:.1f}s)! Usando {qtd_fotos} foto(s) coletada(s)")
                                
                                # Atualizar relatório com todas as fotos
                                context.user_data['relatorio']['fotos_entrada'] = fotos_processadas
                                context.user_data['relatorio']['foto_entrada'] = fotos_processadas[0]['base64']
                                
                                # Enviar mensagem de confirmação (apenas uma vez)
                                if not album_data.get('message_sent', False):
                                    # Mensagem dinâmica baseada na quantidade de fotos
                                    if qtd_fotos == 1:
                                        mensagem_confirmacao = "✅ 1 foto de entrada recebida!\n\n"
                                    else:
                                        mensagem_confirmacao = f"✅ {qtd_fotos} fotos de entrada recebidas!\n\n"
                                    
                                    await update.message.reply_text(
                                        mensagem_confirmacao +
                                        "📸 *Foto de SAÍDA*\n\n"
                                        "Agora envie uma foto da cozinha/área de trabalho de quando você SAIU e deixou tudo organizado.\n\n"
                                        "💡 Você pode enviar uma ou várias fotos.",
                                        parse_mode='Markdown'
                                    )
                                    album_data['message_sent'] = True
                                    logger.info(f"✅ Mensagem de confirmação enviada para álbum (media_group_id: {media_group_id}, {qtd_fotos} foto(s))")
                                
                                return FOTO_SAIDA
                    
                    # Se ainda não foi processado após 5 segundos, processar como foto única (fallback)
                    logger.warning(f"⚠️ Álbum não processado após {tempo_max_espera}s. Processando como foto única (media_group_id: {media_group_id})")
                    # Continuar com processamento normal de foto única
                    is_album = False  # Forçar processamento como foto única
            else:
                # Álbum não encontrado no coletor - pode ser que ainda não tenha sido processado
                # ou que esta seja a primeira foto
                logger.info(f"⚠️ Álbum não encontrado no coletor (media_group_id: {media_group_id}). Aguardando processamento...")
                # Aguardar até 5 segundos, verificando a cada 0.5 segundos se foi processado
                tempo_max_espera = 5.0  # 5 segundos
                intervalo_verificacao = 0.5  # Verificar a cada 0.5 segundos
                tempo_espera_total = 0.0
                
                while tempo_espera_total < tempo_max_espera:
                    await asyncio.sleep(intervalo_verificacao)
                    tempo_espera_total += intervalo_verificacao
                    
                    # Verificar se foi processado
                    if user_id in album_collector and media_group_id in album_collector[user_id]:
                        album_data = album_collector[user_id][media_group_id]
                        if album_data.get('processed', False) and 'fotos_processadas' in album_data:
                            # Agora foi processado - usar fotos coletadas
                            fotos_processadas = album_data['fotos_processadas']
                            qtd_fotos = len(fotos_processadas)
                            
                            logger.info(f"✅ Álbum processado após espera ({tempo_espera_total:.1f}s)! Usando {qtd_fotos} foto(s) coletada(s)")
                            
                            # Atualizar relatório com todas as fotos
                            context.user_data['relatorio']['fotos_entrada'] = fotos_processadas
                            context.user_data['relatorio']['foto_entrada'] = fotos_processadas[0]['base64']
                            
                            # Enviar mensagem de confirmação (apenas uma vez)
                            if not album_data.get('message_sent', False):
                                # Mensagem dinâmica baseada na quantidade de fotos
                                if qtd_fotos == 1:
                                    mensagem_confirmacao = "✅ 1 foto de entrada recebida!\n\n"
                                else:
                                    mensagem_confirmacao = f"✅ {qtd_fotos} fotos de entrada recebidas!\n\n"
                                
                                await update.message.reply_text(
                                    mensagem_confirmacao +
                                    "📸 *Foto de SAÍDA*\n\n"
                                    "Agora envie uma foto da cozinha/área de trabalho de quando você SAIU e deixou tudo organizado.\n\n"
                                    "💡 Você pode enviar uma ou várias fotos.",
                                    parse_mode='Markdown'
                                )
                                album_data['message_sent'] = True
                                logger.info(f"✅ Mensagem de confirmação enviada para álbum (media_group_id: {media_group_id}, {qtd_fotos} foto(s))")
                            
                            return FOTO_SAIDA
                
                # Se ainda não foi processado após 5 segundos, processar como foto única (fallback)
                logger.warning(f"⚠️ Álbum não processado após {tempo_max_espera}s. Processando como foto única (media_group_id: {media_group_id})")
                # Continuar com processamento normal de foto única
                is_album = False  # Forçar processamento como foto única
            
        if not is_album:
            # Foto única - processar normalmente
            logger.info("📸 Foto única de entrada recebida")
            
            # Limpar controle de álbum se existir
            if 'album_entrada' in context.user_data:
                del context.user_data['album_entrada']
            
            # Pegar a foto de maior resolução
            photo_file = await update.message.photo[-1].get_file()
            
            # Baixar a foto para BytesIO
            photo_bytes = BytesIO()
            await photo_file.download_to_memory(photo_bytes)
            photo_bytes.seek(0)
            
            # Converter para base64
            photo_base64 = base64.b64encode(photo_bytes.read()).decode('utf-8')
            context.user_data['relatorio']['foto_entrada'] = photo_base64
            
            # Limpar lista de fotos se existir (foto única substitui álbum)
            if 'fotos_entrada' in context.user_data.get('relatorio', {}):
                del context.user_data['relatorio']['fotos_entrada']
            
            # Enviar mensagem de confirmação e pedir foto de saída
            await update.message.reply_text(
                "✅ 1 foto de entrada recebida!\n\n"
                "📸 *Foto de SAÍDA*\n\n"
                "Agora envie uma foto da cozinha/área de trabalho de quando você SAIU e deixou tudo organizado.\n\n"
                "💡 Você pode enviar uma ou várias fotos.",
                parse_mode='Markdown'
            )
            
            return FOTO_SAIDA

    async def foto_saida(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber foto de saída"""
        if not update.message.photo:
            await update.message.reply_text(
                "❌ Por favor, envie uma FOTO (não texto)"
            )
            return FOTO_SAIDA
        
        # Verificar se é um álbum (múltiplas fotos)
        is_album = update.message.media_group_id is not None
        media_group_id = update.message.media_group_id
        
        if is_album:
            # Verificar se há fotos coletadas pelo handler global
            user_id = update.effective_user.id
            message_id = update.message.message_id
            
            logger.info(f"🔍 [FOTO SAÍDA] Foto recebida - message_id: {message_id}, media_group_id: {media_group_id}, estado_atual: FOTO_SAIDA")
            
            # Verificar se o álbum já foi processado pelo handler global
            if user_id in album_collector and media_group_id in album_collector[user_id]:
                album_data = album_collector[user_id][media_group_id]
                
                # Verificar se já foi processado
                if album_data.get('processed', False) and 'fotos_processadas' in album_data:
                    # Álbum já foi processado - usar fotos coletadas
                    fotos_processadas = album_data['fotos_processadas']
                    qtd_fotos = len(fotos_processadas)
                    
                    logger.info(f"✅ Álbum já processado! Usando {qtd_fotos} foto(s) coletada(s) (media_group_id: {media_group_id})")
                    
                    # Atualizar relatório com todas as fotos
                    context.user_data['relatorio']['fotos_saida'] = fotos_processadas
                    context.user_data['relatorio']['foto_saida'] = fotos_processadas[0]['base64']
                    
                    # Processar e mostrar resumo (apenas uma vez)
                    if not album_data.get('message_sent', False):
                        await self.mostrar_resumo_fase1(update, context)
                        album_data['message_sent'] = True
                        return RESUMO_FASE1
                    else:
                        # Mensagem já foi enviada, apenas retornar estado
                        return RESUMO_FASE1
                else:
                    # Álbum ainda está sendo processado - aguardar mais tempo
                    logger.info(f"⏳ Álbum ainda sendo processado... Aguardando fotos coletadas (media_group_id: {media_group_id})")
                    # Aguardar até 5 segundos, verificando a cada 0.5 segundos se foi processado
                    tempo_max_espera = 5.0  # 5 segundos
                    intervalo_verificacao = 0.5  # Verificar a cada 0.5 segundos
                    tempo_espera_total = 0.0
                    
                    while tempo_espera_total < tempo_max_espera:
                        await asyncio.sleep(intervalo_verificacao)
                        tempo_espera_total += intervalo_verificacao
                        
                        # Verificar se foi processado
                        if user_id in album_collector and media_group_id in album_collector[user_id]:
                            album_data = album_collector[user_id][media_group_id]
                            if album_data.get('processed', False) and 'fotos_processadas' in album_data:
                                # Agora foi processado - usar fotos coletadas
                                fotos_processadas = album_data['fotos_processadas']
                                qtd_fotos = len(fotos_processadas)
                                
                                logger.info(f"✅ Álbum processado após espera ({tempo_espera_total:.1f}s)! Usando {qtd_fotos} foto(s) coletada(s)")
                                
                                # Atualizar relatório com todas as fotos
                                context.user_data['relatorio']['fotos_saida'] = fotos_processadas
                                context.user_data['relatorio']['foto_saida'] = fotos_processadas[0]['base64']
                                
                                # Processar e mostrar resumo (apenas uma vez)
                                if not album_data.get('message_sent', False):
                                    await self.mostrar_resumo_fase1(update, context)
                                    album_data['message_sent'] = True
                                    return RESUMO_FASE1
                                else:
                                    return RESUMO_FASE1
                    
                    # Se ainda não foi processado após 5 segundos, processar como foto única (fallback)
                    logger.warning(f"⚠️ Álbum não processado após {tempo_max_espera}s. Processando como foto única (media_group_id: {media_group_id})")
                    is_album = False  # Forçar processamento como foto única
            else:
                # Álbum não encontrado no coletor - aguardar processamento
                logger.info(f"⚠️ Álbum não encontrado no coletor (media_group_id: {media_group_id}). Aguardando processamento...")
                # Aguardar até 5 segundos, verificando a cada 0.5 segundos se foi processado
                tempo_max_espera = 5.0  # 5 segundos
                intervalo_verificacao = 0.5  # Verificar a cada 0.5 segundos
                tempo_espera_total = 0.0
                
                while tempo_espera_total < tempo_max_espera:
                    await asyncio.sleep(intervalo_verificacao)
                    tempo_espera_total += intervalo_verificacao
                    
                    # Verificar se foi processado
                    if user_id in album_collector and media_group_id in album_collector[user_id]:
                        album_data = album_collector[user_id][media_group_id]
                        if album_data.get('processed', False) and 'fotos_processadas' in album_data:
                            # Agora foi processado - usar fotos coletadas
                            fotos_processadas = album_data['fotos_processadas']
                            qtd_fotos = len(fotos_processadas)
                            
                            logger.info(f"✅ Álbum processado após espera ({tempo_espera_total:.1f}s)! Usando {qtd_fotos} foto(s) coletada(s)")
                            
                            # Atualizar relatório com todas as fotos
                            context.user_data['relatorio']['fotos_saida'] = fotos_processadas
                            context.user_data['relatorio']['foto_saida'] = fotos_processadas[0]['base64']
                            
                            # Processar e mostrar resumo (apenas uma vez)
                            if not album_data.get('message_sent', False):
                                await self.mostrar_resumo_fase1(update, context)
                                album_data['message_sent'] = True
                                return RESUMO_FASE1
                            else:
                                return RESUMO_FASE1
                
                # Se ainda não foi processado após 5 segundos, processar como foto única (fallback)
                logger.warning(f"⚠️ Álbum não processado após {tempo_max_espera}s. Processando como foto única (media_group_id: {media_group_id})")
                is_album = False  # Forçar processamento como foto única
            
        if not is_album:
            # Foto única - processar normalmente
            logger.info("📸 Foto única de saída recebida")
            
            # Limpar controle de álbum se existir
            if 'album_saida' in context.user_data:
                del context.user_data['album_saida']
            
            # Pegar a foto de maior resolução
            photo_file = await update.message.photo[-1].get_file()
            
            # Baixar a foto para BytesIO
            photo_bytes = BytesIO()
            await photo_file.download_to_memory(photo_bytes)
            photo_bytes.seek(0)
            
            # Converter para base64
            photo_base64 = base64.b64encode(photo_bytes.read()).decode('utf-8')
            context.user_data['relatorio']['foto_saida'] = photo_base64
            
            # Limpar lista de fotos se existir (foto única substitui álbum)
            if 'fotos_saida' in context.user_data.get('relatorio', {}):
                del context.user_data['relatorio']['fotos_saida']
            
            # Após as fotos, mostrar resumo e enviar FASE 1
            return await self.mostrar_resumo_fase1(update, context)

    async def mostrar_resumo_fase1(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Mostrar resumo dos dados coletados até agora e destacar envio em 2 partes"""
        relatorio = context.user_data['relatorio']
        
        # Montar resumo
        resumo = (
            "✅ *RESUMO DO RELATÓRIO*\n\n"
            f"👤 *Cliente:* {relatorio['cliente_nome']}\n"
            f"📅 *Data:* {self.format_date(relatorio.get('data_atendimento', 'Hoje'))}\n"
            f"🕐 *Horário:* {relatorio['horario_chegada']} - {relatorio['horario_saida']}\n\n"
        )
        
        # Adicionar informações opcionais
        if relatorio.get('como_foi_visita'):
            resumo += f"📝 *Como foi a visita:*\n{relatorio['como_foi_visita']}\n\n"
        
        if relatorio.get('comentario_cliente'):
            resumo += f"💬 *Comentário do cliente:*\n{relatorio['comentario_cliente']}\n\n"
        
        if relatorio.get('problema_especifico'):
            resumo += f"⚠️ *Problema específico:*\n{relatorio['problema_especifico']}\n\n"
        
        if relatorio.get('porcoes_exatas'):
            resumo += f"🍽️ *Porções exatas:* {relatorio['porcoes_exatas']}\n"
            if relatorio.get('motivo_porcoes'):
                resumo += f"   *Motivo:* {relatorio['motivo_porcoes']}\n"
            resumo += "\n"
        
        if relatorio.get('descarte'):
            resumo += f"🗑️ *Descarte:* {relatorio['descarte']}\n"
            if relatorio.get('itens_descartados'):
                resumo += f"   *Itens:* {relatorio['itens_descartados']}\n"
            resumo += "\n"
        
        if relatorio.get('pode_vencer'):
            resumo += f"⚠️ *Pode vencer:* {relatorio['pode_vencer']}\n"
            if relatorio.get('itens_podem_vencer'):
                resumo += f"   *Itens:* {relatorio['itens_podem_vencer']}\n"
            resumo += "\n"
        
        # Adicionar fotos
        resumo += "📸 *Fotos:*\n"
        resumo += "   • Foto de entrada: ✅\n"
        resumo += "   • Foto de saída: ✅\n\n"
        
        # Confirmar envio
        resumo += "Tudo certo? Vamos enviar a primeira parte do relatório?"
        
        keyboard = [["✅ Sim, enviar"], ["❌ Cancelar"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        
        await update.message.reply_text(
            resumo,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
        return RESUMO_FASE1

    async def confirmacao_fase1(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber confirmação para enviar FASE 1"""
        resposta = update.message.text
        
        if "Cancelar" in resposta:
            await update.message.reply_text(
                "❌ Relatório cancelado.",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        if "Sim" not in resposta and "enviar" not in resposta.lower():
            await update.message.reply_text(
                "Por favor, confirme para continuar.",
                reply_markup=ReplyKeyboardMarkup([["✅ Sim, enviar"], ["❌ Cancelar"]], one_time_keyboard=True, resize_keyboard=True)
            )
            return RESUMO_FASE1
        
        await update.message.reply_text(
            "📤 Enviando primeira parte do relatório...\n\n"
            "⏱️ Aguarde alguns segundos...",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return await self.enviar_fase1(update, context)

    async def enviar_fase1(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enviar FASE 1: dados básicos + fotos para n8n"""
        try:
            # Mensagens temáticas de cozinha para mostrar enquanto processa
            mensagens_aguarde = [
                "⏳ Criando o mise en place... Aguarde mais um momento",
                "⏳ Esquentando o forno... Aguarde mais um momento",
                "⏳ Preparando os ingredientes... Aguarde mais um momento",
                "⏳ Organizando a bancada... Aguarde mais um momento",
                "⏳ Temperando os pratos... Aguarde mais um momento"
            ]
            
            # Preparar payload para FASE 1 (apenas dados básicos + fotos)
            # Estrutura com body envolvendo todos os dados
            payload = {
                "body": {
                    # Chef
                    "chef_id": context.user_data['relatorio'].get('chef_id', ''),
                    "chef_telegram_id": str(update.effective_user.id),
                    "chef_username": f"@{context.user_data['telegram_user']}",
                    "chef_nome": context.user_data['relatorio'].get('chef_nome', ''),
                    
                    # Cliente
                    "cliente_id": context.user_data['relatorio'].get('cliente_id', ''),
                    "cliente_nome": context.user_data['relatorio']['cliente_nome'],
                    
                    # Atendimento
                    "atendimento_id": context.user_data['relatorio'].get('atendimento_id', ''),
                    "data_atendimento": context.user_data['relatorio'].get('data_atendimento', datetime.now(BR_TZ).strftime("%Y-%m-%d")),
                    "horario_chegada": context.user_data['relatorio']['horario_chegada'],
                    "horario_saida": context.user_data['relatorio']['horario_saida'],
                    
                    # Visita
                    "como_foi_visita": context.user_data['relatorio'].get('como_foi_visita', ''),
                    "comentario_cliente": context.user_data['relatorio'].get('comentario_cliente', ''),
                    "problema_especifico": context.user_data['relatorio'].get('problema_especifico', ''),
                    
                    # Porções
                    "porcoes_exatas": context.user_data['relatorio'].get('porcoes_exatas', ''),
                    "motivo_porcoes": context.user_data['relatorio'].get('motivo_porcoes', ''),
                    
                    # Descarte
                    "descarte": context.user_data['relatorio'].get('descarte', ''),
                    "itens_descartados": context.user_data['relatorio'].get('itens_descartados', ''),
                    
                    # Pode vencer
                    "pode_vencer": context.user_data['relatorio'].get('pode_vencer', ''),
                    "itens_podem_vencer": context.user_data['relatorio'].get('itens_podem_vencer', ''),
                    
                    # Fotos (FASE 1)
                    # Foto principal (compatibilidade com n8n atual)
                    "foto_entrada_base64": context.user_data['relatorio'].get('foto_entrada', '') or '',
                    "foto_saida_base64": context.user_data['relatorio'].get('foto_saida', '') or '',
                    # Fotos múltiplas (se houver álbum)
                    "fotos_entrada_base64": [
                        f['base64'] for f in context.user_data['relatorio'].get('fotos_entrada', [])
                    ] if 'fotos_entrada' in context.user_data['relatorio'] else [],
                    "fotos_saida_base64": [
                        f['base64'] for f in context.user_data['relatorio'].get('fotos_saida', [])
                    ] if 'fotos_saida' in context.user_data['relatorio'] else [],
                    # Quantidade de fotos (para informação)
                    "qtd_fotos_entrada": len(context.user_data['relatorio'].get('fotos_entrada', [])) if 'fotos_entrada' in context.user_data['relatorio'] else (1 if context.user_data['relatorio'].get('foto_entrada') else 0),
                    "qtd_fotos_saida": len(context.user_data['relatorio'].get('fotos_saida', [])) if 'fotos_saida' in context.user_data['relatorio'] else (1 if context.user_data['relatorio'].get('foto_saida') else 0),
                    
                    # Inventário (vazio na FASE 1 - será preenchido na FASE 2)
                    "inventario_atualizado": "Não",
                    "inventario_texto": "",
                    "foto_inventario_base64": "",
                    
                    # Personal Shopper (para determinar se precisa de inventário)
                    "personal_shopper": context.user_data.get('personal_shopper', 'Não') or context.user_data['relatorio'].get('personal_shopper', 'Não')
                }
            }
            
            # Enviar para n8n FASE 1 (webhook específico da FASE 1)
            webhook_url_fase1 = N8N_WEBHOOK_URL_FASE1 or N8N_WEBHOOK_URL
            logger.info(f"🔄 Enviando FASE 1 para webhook: {webhook_url_fase1}")
            # Log do payload sem as fotos base64 completas (mostrar apenas tamanho)
            payload_log = {
                "body": {
                    k: (
                        f'{len(v)} chars' if k in ['foto_entrada_base64', 'foto_saida_base64', 'foto_inventario_base64'] and v else 'empty'
                        if k in ['foto_entrada_base64', 'foto_saida_base64', 'foto_inventario_base64'] 
                        else f'{len(v)} fotos' if k in ['fotos_entrada_base64', 'fotos_saida_base64'] and isinstance(v, list) 
                        else v
                    )
                    for k, v in payload['body'].items()
                }
            }
            logger.info(f"📦 Payload: {json.dumps(payload_log, indent=2)}")
            logger.info(f"📸 Fotos: {payload['body'].get('qtd_fotos_entrada', 0)} entrada, {payload['body'].get('qtd_fotos_saida', 0)} saída")
            
            # Variáveis para controle de mensagens de aguarde
            mensagem_aguarde_enviada_1 = False
            mensagem_aguarde_enviada_2 = False
            resposta_recebida = False
            
            async def enviar_mensagem_aguarde(delay: float, mensagem_idx: int):
                """Enviar mensagem de aguarde após delay"""
                nonlocal mensagem_aguarde_enviada_1, mensagem_aguarde_enviada_2, resposta_recebida
                await asyncio.sleep(delay)
                
                # Verificar se ainda não recebeu resposta
                if not resposta_recebida:
                    if mensagem_idx == 1 and not mensagem_aguarde_enviada_1:
                        mensagem_aguarde_enviada_1 = True
                        mensagem = mensagens_aguarde[0]  # "⏳ Criando o mise en place..."
                        await update.message.reply_text(mensagem)
                        logger.info(f"📤 Mensagem de aguarde 1 enviada após {delay:.1f}s")
                    elif mensagem_idx == 2 and not mensagem_aguarde_enviada_2 and mensagem_aguarde_enviada_1:
                        mensagem_aguarde_enviada_2 = True
                        mensagem = mensagens_aguarde[1]  # "⏳ Esquentando o forno..."
                        await update.message.reply_text(mensagem)
                        logger.info(f"📤 Mensagem de aguarde 2 enviada após {delay:.1f}s")
            
            # Iniciar tarefas para enviar mensagens de aguarde
            # Primeira mensagem após 5 segundos
            task_mensagem_1 = asyncio.create_task(enviar_mensagem_aguarde(5.0, 1))
            # Segunda mensagem após 10 segundos (se ainda estiver processando)
            task_mensagem_2 = asyncio.create_task(enviar_mensagem_aguarde(10.0, 2))
            
            # Criar connector SSL com verificação desabilitada (para n8n)
            connector = criar_ssl_connector()
            async with aiohttp.ClientSession(connector=connector) as session:
                try:
                    async with session.post(
                        webhook_url_fase1,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        # Marcar que recebeu resposta (evitar enviar mais mensagens de aguarde)
                        resposta_recebida = True
                        
                        # Cancelar tarefas de mensagem de aguarde (já recebeu resposta)
                        task_mensagem_1.cancel()
                        task_mensagem_2.cancel()
                        
                        try:
                            await task_mensagem_1
                        except asyncio.CancelledError:
                            pass
                        try:
                            await task_mensagem_2
                        except asyncio.CancelledError:
                            pass
                        
                        status_code = response.status
                        logger.info(f"📥 Resposta do webhook FASE 1: Status {status_code}")
                        
                        # Tentar ler resposta
                        try:
                            response_text = await response.text()
                            logger.info(f"📄 Resposta do webhook: {response_text[:500]}")  # Primeiros 500 chars
                            
                            if status_code == 200:
                                try:
                                    resultado = json.loads(response_text)
                                    notion_url = resultado.get('notion_url', '')
                                    notion_page_id = resultado.get('notion_page_id', '')
                                    
                                    # Verificar se recebeu notion_page_id (OBRIGATÓRIO)
                                    if notion_page_id:
                                        logger.info(f"✅ FASE 1 enviada com sucesso! Notion Page ID: {notion_page_id}")
                                        # Salvar notion_page_id para FASE 2
                                        context.user_data['relatorio']['notion_page_id'] = notion_page_id
                                    else:
                                        logger.warning(f"⚠️ FASE 1 enviada, mas workflow não retornou notion_page_id. Resposta: {response_text}")
                                        # Tentar retry (aguardar mais alguns segundos e verificar novamente)
                                        logger.info("🔄 Workflow pode estar processando... Aguardando confirmação...")
                                        await update.message.reply_text(
                                            "⏳ Aguardando confirmação do sistema...",
                                            parse_mode='Markdown'
                                        )
                                        
                                        # Aguardar 3 segundos antes de tentar retry
                                        await asyncio.sleep(3)
                                        
                                        # Fazer segunda tentativa (polling) para verificar se o workflow terminou
                                        try:
                                            async with session.post(
                                                webhook_url_fase1,
                                                json=payload,
                                                timeout=aiohttp.ClientTimeout(total=10)
                                            ) as response_retry:
                                                if response_retry.status == 200:
                                                    response_text_retry = await response_retry.text()
                                                    resultado_retry = json.loads(response_text_retry)
                                                    notion_page_id_retry = resultado_retry.get('notion_page_id', '')
                                                    
                                                    if notion_page_id_retry:
                                                        logger.info(f"✅ FASE 1 confirmada no retry! Notion Page ID: {notion_page_id_retry}")
                                                        context.user_data['relatorio']['notion_page_id'] = notion_page_id_retry
                                                        notion_page_id = notion_page_id_retry
                                                        notion_url = resultado_retry.get('notion_url', notion_url)
                                                    else:
                                                        # NÃO RECEBEU notion_page_id APÓS RETRY - PARAR O PROCESSO
                                                        logger.error(f"❌ ERRO CRÍTICO: Retry também não retornou notion_page_id. Resposta: {response_text_retry}")
                                                        await update.message.reply_text(
                                                            "❌ *ERRO AO CRIAR RELATÓRIO*\n\n"
                                                            "O sistema não conseguiu criar o relatório no Notion.\n\n"
                                                            "🔧 *O que aconteceu:*\n"
                                                            "A primeira parte do relatório foi enviada, mas não recebemos confirmação de que o relatório foi criado corretamente.\n\n"
                                                            "⚠️ *Ação necessária:*\n"
                                                            "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                                                            "Seus dados foram salvos localmente, mas o relatório não foi criado no Notion.\n\n"
                                                            "📞 Entre em contato com o suporte para resolver este problema.",
                                                            parse_mode='Markdown',
                                                            reply_markup=ReplyKeyboardRemove()
                                                        )
                                                        # PARAR O PROCESSO - não continuar para inventário
                                                        context.user_data.clear()
                                                        return ConversationHandler.END
                                        except Exception as e:
                                            logger.error(f"❌ Erro no retry: {e}", exc_info=True)
                                            # Erro no retry - PARAR O PROCESSO
                                            await update.message.reply_text(
                                                "❌ *ERRO AO PROCESSAR RELATÓRIO*\n\n"
                                                "Ocorreu um erro ao tentar confirmar a criação do relatório.\n\n"
                                                "🔧 *O que aconteceu:*\n"
                                                "A primeira parte do relatório foi enviada, mas não conseguimos confirmar se o relatório foi criado corretamente.\n\n"
                                                "⚠️ *Ação necessária:*\n"
                                                "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                                                "Seus dados foram salvos localmente, mas não conseguimos confirmar a criação no Notion.\n\n"
                                                "📞 Entre em contato com o suporte para resolver este problema.",
                                                parse_mode='Markdown',
                                                reply_markup=ReplyKeyboardRemove()
                                            )
                                            # PARAR O PROCESSO - não continuar para inventário
                                            context.user_data.clear()
                                            return ConversationHandler.END
                                        
                                        # Se ainda não tiver notion_page_id após retry, PARAR O PROCESSO
                                        if not notion_page_id:
                                            logger.error("❌ ERRO CRÍTICO: Não foi possível obter notion_page_id após retry. Parando processo.")
                                            await update.message.reply_text(
                                                "❌ *ERRO AO CRIAR RELATÓRIO*\n\n"
                                                "O sistema não conseguiu criar o relatório no Notion.\n\n"
                                                "🔧 *O que aconteceu:*\n"
                                                "A primeira parte do relatório foi enviada, mas não recebemos confirmação de que o relatório foi criado corretamente.\n\n"
                                                "⚠️ *Ação necessária:*\n"
                                                "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                                                "Seus dados foram salvos localmente, mas o relatório não foi criado no Notion.\n\n"
                                                "📞 Entre em contato com o suporte para resolver este problema.",
                                                parse_mode='Markdown',
                                                reply_markup=ReplyKeyboardRemove()
                                            )
                                            # PARAR O PROCESSO - não continuar para inventário
                                            context.user_data.clear()
                                            return ConversationHandler.END
                                    
                                    # Só chega aqui se tiver notion_page_id
                                    # Mensagem 1: Informações gerais do atendimento enviadas com sucesso
                                    mensagem_1 = "✅ Informações gerais do atendimento enviadas com sucesso."
                                    
                                    await update.message.reply_text(
                                        mensagem_1,
                                        parse_mode='Markdown',
                                        reply_markup=ReplyKeyboardRemove()
                                    )
                                    
                                    # Verificar se precisa de inventário (Personal Shopper)
                                    personal_shopper = context.user_data.get('personal_shopper', 'Não') or context.user_data['relatorio'].get('personal_shopper', 'Não')
                                    
                                    # Se Personal Shopper indicar que NÃO precisa de inventário, pular e finalizar
                                    if not self.precisa_inventario(personal_shopper):
                                        logger.info(f"⏭️ Pulando inventário - Personal Shopper = '{personal_shopper}' para cliente {context.user_data['relatorio']['cliente_nome']}")
                                        
                                        # Atualizar relatório no Notion para marcar como completo (sem inventário)
                                        # Isso será feito pelo n8n quando receber a FASE 1, mas vamos garantir aqui
                                        await update.message.reply_text(
                                            "✅ *Relatório finalizado!*\n\n"
                                            "Este atendimento não requer inventário.\n\n"
                                            "Caso você queira enviar outro relatório de visita, basta iniciar novamente a conversa.\n\n"
                                            "Let's cook!",
                                            parse_mode='Markdown',
                                            reply_markup=ReplyKeyboardRemove()
                                        )
                                        
                                        # Limpar dados e finalizar
                                        context.user_data.clear()
                                        if update.effective_user.id in user_activity:
                                            del user_activity[update.effective_user.id]
                                        return ConversationHandler.END
                                    
                                    # Se Personal Shopper não for "Não", continuar com inventário
                                    logger.info(f"📦 Continuando com inventário - Personal Shopper = '{personal_shopper}' para cliente {context.user_data['relatorio']['cliente_nome']}")
                                    
                                    # Mensagem 2: Agora vamos seguir para o inventário
                                    await update.message.reply_text(
                                        "Agora vamos seguir para o inventário."
                                    )
                                    
                                    # Mensagem 3: Pedir inventário com informações sobre temperos sensíveis
                                    await update.message.reply_text(
                                        "Me envie quais foram os ingredientes/insumos que sobraram do último atendimento, seja o mais detalhista possível, pois isso vai impactar no próximo atendimento.\n\n"
                                        "Não se esqueça de pontuar temperos sensíveis como: Pimentas, Açafrão da terra, Canela, etc.."
                                    )
                                    
                                    # Reagendar timeout após enviar mensagem esperando resposta
                                    self.reagendar_timeout_apos_mensagem(update, context)
                                    
                                    # Continuar com inventário (FASE 2)
                                    return INVENTARIO_OPCAO
                                except json.JSONDecodeError as e:
                                    logger.error(f"❌ Erro ao parsear JSON da resposta: {e}")
                                    logger.error(f"Resposta recebida: {response_text}")
                                    # Erro ao parsear JSON - não podemos confirmar se o relatório foi criado
                                    # PARAR O PROCESSO
                                    await update.message.reply_text(
                                        "❌ *ERRO AO PROCESSAR RELATÓRIO*\n\n"
                                        "Ocorreu um erro ao processar a resposta do sistema.\n\n"
                                        "🔧 *O que aconteceu:*\n"
                                        "A primeira parte do relatório foi enviada, mas não conseguimos interpretar a resposta do sistema.\n\n"
                                        "⚠️ *Ação necessária:*\n"
                                        "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                                        "Seus dados foram salvos localmente, mas não conseguimos confirmar a criação no Notion.\n\n"
                                        "📞 Entre em contato com o suporte para resolver este problema.",
                                        parse_mode='Markdown',
                                        reply_markup=ReplyKeyboardRemove()
                                    )
                                    # PARAR O PROCESSO - não continuar para inventário
                                    context.user_data.clear()
                                    return ConversationHandler.END
                            
                            elif status_code == 404:
                                # Webhook não encontrado - PARAR O PROCESSO
                                logger.error(f"❌ Webhook não encontrado (404). Resposta: {response_text[:200]}")
                                await update.message.reply_text(
                                    "❌ *ERRO AO ENVIAR RELATÓRIO*\n\n"
                                    "O sistema de processamento não está configurado ou não está disponível.\n\n"
                                    "🔧 *O que aconteceu:*\n"
                                    "A primeira parte do relatório foi coletada, mas não conseguimos enviar para o sistema de processamento.\n\n"
                                    "⚠️ *Ação necessária:*\n"
                                    "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                                    "Seus dados foram salvos localmente, mas não foram enviados para o sistema.\n\n"
                                    "📞 Entre em contato com o suporte para resolver este problema.",
                                    parse_mode='Markdown',
                                    reply_markup=ReplyKeyboardRemove()
                                )
                                # PARAR O PROCESSO - não continuar para inventário
                                context.user_data.clear()
                                return ConversationHandler.END
                            else:
                                # Erro no webhook (status diferente de 200) - PARAR O PROCESSO
                                logger.error(f"❌ Erro no webhook: Status {status_code}, Resposta: {response_text[:200]}")
                                await update.message.reply_text(
                                    f"❌ *ERRO AO ENVIAR RELATÓRIO*\n\n"
                                    f"Ocorreu um erro ao enviar o relatório para o sistema.\n\n"
                                    f"🔧 *O que aconteceu:*\n"
                                    f"O sistema retornou um erro (Status {status_code}).\n\n"
                                    f"⚠️ *Ação necessária:*\n"
                                    f"Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                                    f"Seus dados foram salvos localmente, mas não foram enviados para o sistema.\n\n"
                                    f"📞 Entre em contato com o suporte para resolver este problema.",
                                    parse_mode='Markdown',
                                    reply_markup=ReplyKeyboardRemove()
                                )
                                # PARAR O PROCESSO - não continuar para inventário
                                context.user_data.clear()
                                return ConversationHandler.END
                                
                        except Exception as e:
                            logger.error(f"❌ Erro ao ler resposta do webhook: {e}", exc_info=True)
                            # Erro ao ler resposta - PARAR O PROCESSO
                            await update.message.reply_text(
                                "❌ *ERRO AO PROCESSAR RELATÓRIO*\n\n"
                                "Ocorreu um erro ao processar a resposta do sistema.\n\n"
                                "🔧 *O que aconteceu:*\n"
                                f"Erro: {str(e)}\n\n"
                                "⚠️ *Ação necessária:*\n"
                                "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                                "Seus dados foram salvos localmente, mas não conseguimos confirmar a criação no Notion.\n\n"
                                "📞 Entre em contato com o suporte para resolver este problema.",
                                parse_mode='Markdown',
                                reply_markup=ReplyKeyboardRemove()
                            )
                            # PARAR O PROCESSO - não continuar para inventário
                            context.user_data.clear()
                            return ConversationHandler.END
                            
                except asyncio.TimeoutError:
                    logger.error(f"⏱️ Timeout ao enviar FASE 1 para webhook: {webhook_url_fase1}")
                    # Timeout - PARAR O PROCESSO
                    await update.message.reply_text(
                        "❌ *ERRO AO ENVIAR RELATÓRIO*\n\n"
                        "O sistema não respondeu a tempo.\n\n"
                        "🔧 *O que aconteceu:*\n"
                        "O sistema de processamento não respondeu dentro do tempo esperado (30 segundos).\n\n"
                        "⚠️ *Ação necessária:*\n"
                        "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                        "Seus dados foram salvos localmente, mas não foram enviados para o sistema.\n\n"
                        "📞 Entre em contato com o suporte para resolver este problema.",
                        parse_mode='Markdown',
                        reply_markup=ReplyKeyboardRemove()
                    )
                    # PARAR O PROCESSO - não continuar para inventário
                    context.user_data.clear()
                    return ConversationHandler.END
                except aiohttp.ClientError as e:
                    logger.error(f"❌ Erro de conexão ao enviar FASE 1: {e}")
                    # Erro de conexão - PARAR O PROCESSO
                    await update.message.reply_text(
                        "❌ *ERRO AO ENVIAR RELATÓRIO*\n\n"
                        "Ocorreu um erro de conexão ao enviar o relatório.\n\n"
                        "🔧 *O que aconteceu:*\n"
                        "Não conseguimos conectar com o sistema de processamento.\n\n"
                        "⚠️ *Ação necessária:*\n"
                        "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                        "Seus dados foram salvos localmente, mas não foram enviados para o sistema.\n\n"
                        "📞 Entre em contato com o suporte para resolver este problema.",
                        parse_mode='Markdown',
                        reply_markup=ReplyKeyboardRemove()
                    )
                    # PARAR O PROCESSO - não continuar para inventário
                    context.user_data.clear()
                    return ConversationHandler.END
                        
        except Exception as e:
            logger.error(f"❌ Erro ao enviar FASE 1: {e}", exc_info=True)
            # Qualquer outro erro - PARAR O PROCESSO
            await update.message.reply_text(
                "❌ *ERRO AO ENVIAR RELATÓRIO*\n\n"
                "Ocorreu um erro inesperado ao enviar o relatório.\n\n"
                "🔧 *O que aconteceu:*\n"
                f"Erro: {str(e)}\n\n"
                "⚠️ *Ação necessária:*\n"
                "Por favor, entre em contato com o suporte técnico e informe este erro.\n"
                "Seus dados foram salvos localmente, mas não foram enviados para o sistema.\n\n"
                "📞 Entre em contato com o suporte para resolver este problema.",
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardRemove()
            )
            # PARAR O PROCESSO - não continuar para inventário
            context.user_data.clear()
            return ConversationHandler.END

    async def confirmacao_final(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Receber confirmação final e processar inventário (FASE 2A)"""
        resposta = update.message.text
        
        if "Cancelar" in resposta:
            await update.message.reply_text(
                "❌ Inventário cancelado.\n"
                "A primeira parte do relatório já foi enviada com sucesso.",
                reply_markup=ReplyKeyboardRemove()
            )
            context.user_data.clear()
            return ConversationHandler.END
        
        if "Sim" not in resposta and "enviar" not in resposta.lower():
            await update.message.reply_text(
                "Por favor, confirme para continuar.",
                reply_markup=ReplyKeyboardMarkup([["✅ Sim, enviar"], ["❌ Cancelar"]], one_time_keyboard=True, resize_keyboard=True)
            )
            return CONFIRMACAO_FINAL
        
        # Preparar dados para processar_inventario
        # Salvar inventário no user_data (processar_inventario espera aqui)
        if 'relatorio' in context.user_data:
            inventario_texto = context.user_data['relatorio'].get('inventario_texto', '')
            inventario_foto = context.user_data['relatorio'].get('inventario_foto', '')
            
            # Salvar no user_data para processar_inventario usar
            context.user_data['inventario_texto'] = inventario_texto
            context.user_data['foto_inventario_base64'] = inventario_foto or ''
        
        # Chamar processar_inventario (FASE 2A) ao invés de enviar_fase2
        return await self.processar_inventario(update, context)

    async def enviar_fase2(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Enviar inventário para n8n atualizar relatório"""
        try:
            # Preparar payload para inventário
            payload = {
                # ID do relatório criado na primeira parte
                "notion_page_id": context.user_data['relatorio'].get('notion_page_id', ''),
                
                # Inventário
                "inventario_atualizado": "Sim" if (
                    context.user_data['relatorio'].get('inventario_texto') or
                    context.user_data['relatorio'].get('inventario_foto')
                ) else "Não",
                "inventario_texto": context.user_data['relatorio'].get('inventario_texto', ''),
                "foto_inventario_base64": context.user_data['relatorio'].get('inventario_foto', '') or ''
            }
            
            # Enviar para n8n (webhook específico da FASE 2)
            webhook_url_fase2 = N8N_WEBHOOK_URL_FASE2 or N8N_WEBHOOK_URL
            payload['fase'] = 2
            logger.info(f"🔄 Enviando inventário para webhook: {webhook_url_fase2}")
            logger.info(f"📦 Payload: {json.dumps({k: v if k != 'foto_inventario_base64' else f'{len(v)} chars' if v else 'empty' for k, v in payload.items()}, indent=2)}")
            
            connector = criar_ssl_connector()
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                    webhook_url_fase2,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        resultado = await response.json()
                        
                        mensagem_final = (
                            "🎉 *Inventário enviado com sucesso!*\n\n"
                            "Seu inventário foi processado e o relatório foi atualizado no Notion.\n\n"
                            "✅ *Relatório completo!*\n\n"
                            "Obrigado pelo seu trabalho! 👨‍🍳"
                        )
                        
                        await update.message.reply_text(
                            mensagem_final,
                            parse_mode='Markdown',
                            reply_markup=ReplyKeyboardRemove()
                        )
                    else:
                        raise Exception(f"Erro no webhook: {response.status}")
                        
        except Exception as e:
            logger.error(f"Erro ao enviar inventário: {e}", exc_info=True)
            await update.message.reply_text(
                "⚠️ Houve um erro ao processar o inventário.\n"
                "A primeira parte do relatório já foi enviada com sucesso.\n"
                "Por favor, entre em contato com o suporte e informe este erro.\n"
                f"Erro: {str(e)}",
                reply_markup=ReplyKeyboardRemove()
            )
        
        # Limpar dados do usuário
        context.user_data.clear()
        return ConversationHandler.END

    async def cancelar(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancelar conversa"""
        await update.message.reply_text(
            "❌ Relatório cancelado.\n"
            "Use /relatorio para começar novamente.",
            reply_markup=ReplyKeyboardRemove()
        )
        context.user_data.clear()
        return ConversationHandler.END


def main():
    """Função principal"""
    # Verificar token
    if not TELEGRAM_TOKEN:
        logger.error("Token do Telegram não configurado!")
        return
    
    # Criar aplicação
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Criar instância do bot
    bot = ChefBot()
    
    # Handler global para agrupar fotos de álbuns ANTES do ConversationHandler
    async def group_album_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Agrupar fotos de álbuns antes de processar no ConversationHandler"""
        if not update.message or not update.message.photo:
            return  # Não é uma foto, deixar passar
        
        # Verificar se é um álbum
        media_group_id = update.message.media_group_id
        if not media_group_id:
            return  # Não é um álbum, deixar passar
        
        user_id = update.effective_user.id
        message_id = update.message.message_id
        
        logger.info(f"🔍 [ALBUM HANDLER] Foto recebida - user_id: {user_id}, message_id: {message_id}, media_group_id: {media_group_id}")
        
        # Inicializar estrutura para o usuário se não existir
        if user_id not in album_collector:
            album_collector[user_id] = {}
        
        # Inicializar estrutura para o álbum se não existir
        if media_group_id not in album_collector[user_id]:
            album_collector[user_id][media_group_id] = {
                'updates': [],
                'processed': False,
                'task': None,
                'last_update_time': asyncio.get_event_loop().time()
            }
            logger.info(f"🆕 Novo álbum detectado - user_id: {user_id}, media_group_id: {media_group_id}")
        
        # Obter dados do álbum
        album_data = album_collector[user_id][media_group_id]
        
        # Verificar se já foi processado - se sim, bloquear para não passar para o ConversationHandler
        # Mas permitir que a primeira foto do álbum processado seja passada para o ConversationHandler
        # para usar as fotos coletadas
        if album_data['processed']:
            # Se o álbum já foi processado e já enviamos mensagem, bloquear fotos adicionais
            if album_data.get('message_sent', False):
                logger.info(f"📸 Álbum já foi processado e mensagem enviada. Bloqueando foto (message_id: {message_id})")
                raise ApplicationHandlerStop
            # Se o álbum foi processado mas ainda não enviamos mensagem, permitir que a primeira foto seja processada
            logger.info(f"📸 Álbum já foi processado. Permitindo primeira foto para usar fotos coletadas (message_id: {message_id})")
            # Não bloquear - deixar passar para o ConversationHandler processar
        
        # Adicionar update à lista (evitar duplicatas)
        if message_id not in [u.message.message_id for u in album_data['updates'] if u.message]:
            album_data['updates'].append(update)
            album_data['last_update_time'] = asyncio.get_event_loop().time()
            logger.info(f"✅ Foto adicionada ao álbum pendente (total: {len(album_data['updates'])}, media_group_id: {media_group_id})")
        else:
            logger.info(f"⚠️ Foto duplicada ignorada (message_id: {message_id})")
            # Se já está na lista e o álbum não foi processado, deixar passar para o handler processar
            # Se já está na lista e o álbum foi processado, bloquear se já enviamos mensagem
            if album_data.get('processed', False) and album_data.get('message_sent', False):
                raise ApplicationHandlerStop
        
        # Cancelar task anterior se existir (reset timer)
        if album_data['task'] and not album_data['task'].done():
            album_data['task'].cancel()
            logger.info(f"🔄 Cancelando task anterior (reset timer)")
        
        # Criar task para processar álbum após aguardar todas as fotos
        async def process_album_after_wait():
            """Processar álbum após aguardar todas as fotos"""
            await asyncio.sleep(3)  # Aguardar 3 segundos
            
            # Verificar se ainda temos o álbum
            if user_id not in album_collector or media_group_id not in album_collector[user_id]:
                logger.warning(f"⚠️ Álbum {media_group_id} não encontrado durante processamento")
                return
            
            album_data = album_collector[user_id][media_group_id]
            
            # Verificar se já foi processado
            if album_data['processed']:
                logger.info(f"📸 Álbum já foi processado (media_group_id: {media_group_id})")
                return
            
            # Verificar se ainda não recebemos mais fotos recentemente
            tempo_decorrido = asyncio.get_event_loop().time() - album_data['last_update_time']
            if tempo_decorrido < 2.0:  # Se recebemos foto recentemente (menos de 2s), não processar ainda
                logger.info(f"⏳ Recebemos foto recentemente ({tempo_decorrido:.1f}s atrás), aguardando mais...")
                return
            
            # Processar todas as fotos do álbum
            updates_album = album_data['updates']
            qtd_fotos = len(updates_album)
            logger.info(f"📸 Processando álbum completo: {qtd_fotos} foto(s) coletada(s) (media_group_id: {media_group_id})")
            
            # Marcar como processado
            album_data['processed'] = True
            
            # Processar todas as fotos (baixar e converter para base64)
            fotos_processadas = []
            for update_photo in updates_album:
                if update_photo.message and update_photo.message.photo:
                    try:
                        # Baixar foto (maior resolução)
                        # O update já tem acesso ao bot através do photo file
                        photo_file = await update_photo.message.photo[-1].get_file()
                        photo_bytes = BytesIO()
                        await photo_file.download_to_memory(photo_bytes)
                        photo_bytes.seek(0)
                        photo_base64 = base64.b64encode(photo_bytes.read()).decode('utf-8')
                        
                        fotos_processadas.append({
                            'file_unique_id': update_photo.message.photo[-1].file_unique_id,
                            'base64': photo_base64,
                            'message_id': update_photo.message.message_id
                        })
                    except Exception as e:
                        logger.error(f"❌ Erro ao processar foto (message_id: {update_photo.message.message_id}): {e}")
            
            logger.info(f"✅ {len(fotos_processadas)} foto(s) processada(s) do álbum (media_group_id: {media_group_id})")
            
            # Armazenar fotos processadas no album_collector para acesso pelo ConversationHandler
            album_data['fotos_processadas'] = fotos_processadas
            album_data['qtd_fotos'] = len(fotos_processadas)
            album_data['message_sent'] = False  # Inicializar flag de mensagem enviada
            
            # NÃO enviar mensagem aqui - deixar o ConversationHandler enviar quando processar
            # Isso garante que a mensagem seja enviada no contexto correto (entrada ou saída)
            
            logger.info(f"✅ Álbum processado e pronto para uso (media_group_id: {media_group_id}, {len(fotos_processadas)} foto(s))")
        
        # Criar task para processar após aguardar
        task = asyncio.create_task(process_album_after_wait())
        album_data['task'] = task
        
        # IMPORTANTE: Não bloquear a mensagem - deixar passar para o ConversationHandler
        # O ConversationHandler vai verificar se há fotos coletadas para este media_group_id
        # Se houver, vai usar as fotos coletadas em vez de processar a foto individual
    
    # Handler para logar todas as mensagens recebidas (debug)
    async def log_all_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Logar todas as atualizações recebidas"""
        if update.message:
            logger.info(f"📨 Mensagem recebida: de @{update.effective_user.username} (ID: {update.effective_user.id}), texto: {update.message.text}")
        elif update.callback_query:
            logger.info(f"🔘 Callback recebido: de @{update.effective_user.username} (ID: {update.effective_user.id})")
    
    # Adicionar handler de agrupamento de álbuns (group=-1, ANTES do ConversationHandler)
    application.add_handler(MessageHandler(filters.PHOTO, group_album_photos), group=-1)
    
    # Adicionar handler de log (com prioridade baixa para não interferir)
    application.add_handler(MessageHandler(filters.ALL, log_all_updates), group=-1)
    
    # Definir handlers da conversa
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("relatorio", bot.start)],
        states={
            SELECIONAR_ATENDIMENTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.selecionar_atendimento)],
            HORARIO_CHEGADA: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.horario_chegada)],
            HORARIO_SAIDA: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.horario_saida)],
            COMO_FOI_VISITA: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.como_foi_visita)],
            COMENTARIO_CLIENTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.comentario_cliente)],
            DETALHE_COMENTARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.detalhe_comentario)],
            PROBLEMA_ESPECIFICO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.problema_especifico)],
            DETALHE_PROBLEMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.detalhe_problema)],
            PORCOES_EXATAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.porcoes_exatas)],
            MOTIVO_PORCOES: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.motivo_porcoes)],
            FOTO_ENTRADA: [MessageHandler(filters.PHOTO, bot.foto_entrada)],
            FOTO_SAIDA: [MessageHandler(filters.PHOTO, bot.foto_saida)],
            RESUMO_FASE1: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.confirmacao_fase1)],
            DESCARTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.descarte)],
            ITENS_DESCARTADOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.itens_descartados)],
            PODE_VENCER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.pode_vencer)],
            ITENS_PODEM_VENCER: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.itens_podem_vencer)],
            INVENTARIO_OPCAO: [MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, bot.inventario_opcao)],
            INVENTARIO_TEXTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.inventario_opcao)],
            CONFIRMAR_INVENTARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.confirmar_inventario)],
        },
        fallbacks=[CommandHandler("cancelar", bot.cancelar)]
    )
    
    # Adicionar handler
    application.add_handler(conv_handler)
    
    # Adicionar error handler
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handler de erros"""
        logger.error(f"❌ Erro no bot: {context.error}", exc_info=context.error)
        if update and isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ Ocorreu um erro ao processar sua mensagem. Por favor, tente novamente ou entre em contato com o suporte."
                )
            except:
                pass
    
    application.add_error_handler(error_handler)
    
    # Iniciar bot
    logger.info("Bot iniciado! 🤖")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
