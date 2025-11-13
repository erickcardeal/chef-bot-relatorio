# 🔄 Como Reiniciar o Bot

## 📋 Passo a Passo

### **1. Parar o Bot Atual**

#### **Opção A: Usar o script (recomendado)**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
./REINICIAR_BOT.sh
```

#### **Opção B: Comando manual**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
pkill -f "python.*main.py"
```

#### **Opção C: Encontrar e matar processo**
```bash
# Encontrar o processo
ps aux | grep "python.*main.py" | grep -v grep

# Matar o processo (substitua PID pelo número do processo)
kill -9 PID
```

---

### **2. Verificar se o Bot Foi Parado**

```bash
ps aux | grep "python.*main.py" | grep -v grep
```

**Resultado esperado:** Nenhum processo encontrado (ou nenhuma saída)

---

### **3. Reiniciar o Bot**

#### **Opção A: Usar o script (recomendado)**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
./INICIAR_BOT.sh
```

#### **Opção B: Comando manual**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot

# Se usar venv (ambiente virtual)
source venv/bin/activate

# Iniciar o bot
python3 main.py
```

#### **Opção C: Rodar em background**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
source venv/bin/activate  # Se usar venv
nohup python3 main.py > bot.log 2>&1 &
```

---

### **4. Verificar se o Bot Está Rodando**

```bash
ps aux | grep "python.*main.py" | grep -v grep
```

**Resultado esperado:** Processo do bot rodando

---

## 🔍 Verificar Logs

### **Ver logs em tempo real:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -f bot.log
```

### **Ver últimas linhas do log:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
tail -50 bot.log
```

---

## ⚠️ Troubleshooting

### **Problema: Bot não para**
```bash
# Forçar parada
pkill -9 -f "python.*main.py"
```

### **Problema: Bot não inicia**
```bash
# Verificar se há erros
python3 main.py

# Verificar se as dependências estão instaladas
pip3 install -r requirements.txt
```

### **Problema: Porta em uso**
```bash
# Verificar se há processo usando a porta
lsof -i :PORT
```

---

## 📝 Notas

- ✅ **O bot precisa ser reiniciado sempre que o código for alterado**
- ✅ **O bot carrega o código em memória quando inicia**
- ✅ **Mudanças no código só são aplicadas após reiniciar**
- ✅ **Logs são salvos em `bot.log`**

---

## 🚀 Comandos Rápidos

### **Reiniciar rapidamente:**
```bash
cd /Users/erickcardealdossantos/Desktop/Bot
pkill -f "python.*main.py" && sleep 2 && source venv/bin/activate && python3 main.py
```

### **Verificar status:**
```bash
ps aux | grep "python.*main.py" | grep -v grep
```

### **Ver logs:**
```bash
tail -f bot.log
```


