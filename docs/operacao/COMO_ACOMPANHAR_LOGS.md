# 📋 Como Acompanhar os Logs do Bot no Cursor

## 🎯 Opções para Monitorar o Bot

### **1. Terminal Integrado do Cursor (Recomendado)**

#### **Abrir Terminal:**
- **Atalho:** `` Ctrl + ` `` (backtick) ou `Cmd + J`
- **Menu:** Terminal → New Terminal

#### **Comandos Úteis:**

##### **Ver logs em tempo real:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -f bot.log
```

##### **Ver últimas 50 linhas:**
```bash
tail -50 bot.log
```

##### **Ver logs filtrados (apenas erros/webhooks):**
```bash
tail -f bot.log | grep -i "error\|webhook\|fase\|enviando"
```

##### **Ver logs com cores (se tiver `ccze` instalado):**
```bash
tail -f bot.log | ccze -A
```

---

### **2. Abrir Arquivo de Log no Cursor**

#### **Passos:**
1. **Abrir arquivo:** `bot.log` na pasta do projeto
2. **Atualizar:** O arquivo atualiza automaticamente quando o bot escreve novos logs
3. **Recarregar:** `Cmd + R` ou clique no botão de refresh

#### **Vantagens:**
- ✅ Ver logs formatados
- ✅ Buscar por texto (`Cmd + F`)
- ✅ Ver histórico completo

---

### **3. Terminal Separado (Fora do Cursor)**

#### **Abrir Terminal externo:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -f bot.log
```

---

## 🔍 Comandos Úteis para Debug

### **Ver logs em tempo real:**
```bash
tail -f bot.log
```

### **Ver últimas 100 linhas:**
```bash
tail -100 bot.log
```

### **Ver logs filtrados (apenas webhooks):**
```bash
tail -f bot.log | grep -i "webhook\|fase\|enviando\|resposta"
```

### **Ver logs filtrados (apenas erros):**
```bash
tail -f bot.log | grep -i "error\|exception\|erro"
```

### **Ver logs de uma data específica:**
```bash
grep "2025-11-12" bot.log
```

### **Ver logs de um usuário específico:**
```bash
grep "@eloijulio" bot.log
```

### **Ver logs de webhook (FASE 1):**
```bash
grep -A 5 "Enviando FASE 1" bot.log
```

### **Ver logs de webhook (FASE 2):**
```bash
grep -A 5 "Enviando inventário" bot.log
```

---

## 📊 Monitoramento em Tempo Real

### **Comando Completo:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot && tail -f bot.log | grep --line-buffered -i "webhook\|fase\|enviando\|resposta\|error\|exception"
```

### **Ver tudo em tempo real:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot && tail -f bot.log
```

---

## 🎨 Formatação de Logs

### **Logs Importantes:**
- `🔄 Enviando FASE 1` - Quando envia dados para webhook
- `📥 Resposta do webhook` - Resposta do webhook
- `✅ FASE 1 enviada com sucesso` - Sucesso no envio
- `❌ Erro` - Erros
- `⚠️ Aviso` - Avisos

---

## 🔧 Verificar Status do Bot

### **Ver se o bot está rodando:**
```bash
ps aux | grep "python.*main.py" | grep -v grep
```

### **Ver PID do bot:**
```bash
cat bot.pid
```

### **Ver logs de inicialização:**
```bash
grep "Bot iniciado\|Application started" bot.log
```

---

## 📝 Exemplos de Uso

### **Durante um teste:**
1. Abrir terminal no Cursor (`Ctrl + ` ` ou `Cmd + J`)
2. Executar: `tail -f bot.log`
3. Fazer teste no Telegram
4. Ver logs aparecendo em tempo real

### **Depois de um teste:**
1. Ver últimas linhas: `tail -50 bot.log`
2. Ver logs do webhook: `grep -A 10 "Enviando FASE 1" bot.log`
3. Ver erros: `grep -i "error\|exception" bot.log`

---

## 💡 Dica

### **Criar um alias (opcional):**
Adicione no seu `~/.zshrc` ou `~/.bashrc`:

```bash
alias botlogs='cd /Users/erickcardealdossantos/Desktop/Bot && tail -f bot.log'
alias botlogs-webhook='cd /Users/erickcardealdossantos/Desktop/Bot && tail -f bot.log | grep -i "webhook\|fase\|enviando"'
alias botlogs-error='cd /Users/erickcardealdossantos/Desktop/Bot && tail -f bot.log | grep -i "error\|exception"'
```

Depois execute:
```bash
source ~/.zshrc  # ou source ~/.bashrc
```

Agora você pode usar:
- `botlogs` - Ver todos os logs
- `botlogs-webhook` - Ver apenas webhooks
- `botlogs-error` - Ver apenas erros

---

## 🎯 Resumo Rápido

### **Opção 1: Terminal Integrado (Mais Fácil)**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -f bot.log
```

### **Opção 2: Abrir Arquivo**
- Abrir `bot.log` no Cursor
- Arquivo atualiza automaticamente

### **Opção 3: Comando Rápido**
```bash
tail -f /Users/erickcardealdossantos/Desktop/Bot/bot.log
```


