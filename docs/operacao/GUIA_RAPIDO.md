# 🚀 GUIA RÁPIDO - Bot Telegram Chef

## ⚡ Instalação em 5 Minutos

### 1️⃣ Preparar Ambiente

```bash
cd ~/Desktop/Bot

# Criar ambiente virtual (se não tiver)
python3.12 -m venv venv
source venv/bin/activate
```

### 2️⃣ Substituir Arquivos

**Substituir estes arquivos pelos novos (corrigidos):**
- ✅ `config.py`
- ✅ `notion_api.py`
- ✅ `requirements.txt`

**Adicionar novos arquivos:**
- 🆕 `env.example.txt` → renomear para `.env.example`
- 🆕 `check_config.py`
- 🆕 `README.md` (atualizado)
- 🆕 `CORRECOES.md`

**Manter como está:**
- 📌 `main.py` (não mudou)

### 3️⃣ Configurar Credenciais

```bash
# Copiar template
cp .env.example .env

# Editar com suas credenciais
nano .env
```

**Preencher:**
- `TELEGRAM_BOT_TOKEN` → do @BotFather
- `N8N_WEBHOOK_URL` → do seu n8n
- `NOTION_TOKEN` → da integração Notion
- `NOTION_CHEFS_DB` → ID do database de Chefs
- `NOTION_CLIENTES_DB` → ID do database de Clientes
- `NOTION_CALENDARIO_DB` → ID do database do Calendário

### 4️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

### 5️⃣ Verificar Configuração

```bash
python check_config.py
```

**Esperado:** ✅ TODAS AS CONFIGURAÇÕES ESTÃO OK!

### 6️⃣ Rodar Bot

```bash
python main.py
```

**Esperado:** 🤖 Bot iniciado!

---

## 🎯 Teste Rápido

1. Telegram → @PaulBotuse
2. Enviar: `/start`
3. **Deve aparecer:** "👨‍🍳 Olá! Você é [nome]?"

✅ **Funcionou?** Pronto para usar!

❌ **Erro?** Veja o `CORRECOES.md` ou o `README.md` completo

---

## 📋 Checklist de Verificação

- [ ] Ambiente virtual ativado
- [ ] Arquivos corrigidos substituídos
- [ ] `.env` criado e preenchido
- [ ] `check_config.py` rodou com sucesso
- [ ] Bot iniciou sem erros
- [ ] Teste no Telegram funcionou

---

## 🔧 O Que Foi Corrigido?

**Resumo:**
- ✅ Variáveis de ambiente alinhadas entre arquivos
- ✅ Classe NotionAPI criada
- ✅ Dependências faltantes adicionadas
- ✅ Scripts de verificação criados

**Detalhes completos:** Ver `CORRECOES.md`

---

## 📞 Ajuda Rápida

**Erro comum:** "ModuleNotFoundError"
- **Solução:** `pip install -r requirements.txt`

**Erro comum:** "Token não configurado"
- **Solução:** Verificar arquivo `.env`

**Erro comum:** "Chef não encontrado"
- **Solução:** Campo "Telegram Username" no Notion

**Outros erros:**
- Rodar: `python check_config.py`
- Ver logs de erro
- Consultar `README.md` completo

---

**Documentação completa:**
https://www.notion.so/Bot-Telegram-Relat-rio-de-Visita-2a8b71fbd8f98021a3ecc09eed2d28ff
