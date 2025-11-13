# 🔧 Solução Pendente: Processamento de Álbuns

## 📊 Problema Atual

O bot não está processando corretamente múltiplas fotos enviadas em um álbum. Quando o usuário envia 3 fotos em um álbum:
- Foto 1: Processada e muda estado para FOTO_SAIDA
- Foto 2: Processada como "foto de saída" (ERRADO)
- Foto 3: Processada como "foto de saída" (ERRADO)

## 🔍 Causa Raiz

O `ConversationHandler` processa mensagens **sequencialmente**. Quando a primeira foto inicia `await asyncio.sleep(4)`, ela bloqueia o handler. A segunda foto fica na fila esperando. Quando a primeira foto termina o sleep e muda o estado para `FOTO_SAIDA`, a segunda foto é processada no novo estado.

## ✅ Solução Correta (Pendente)

### Abordagem:
1. **Interceptar todas as fotos ANTES do ConversationHandler** (usar handler global `group=-1`)
2. **Agrupar fotos do mesmo `media_group_id`** em uma lista temporária
3. **Aguardar todas as fotos chegarem** (usar timeout de 3-5 segundos)
4. **Processar todas as fotos de uma vez** quando todas foram coletadas
5. **Passar apenas a primeira foto para o ConversationHandler** (as outras são ignoradas)
6. **O ConversationHandler processa apenas uma vez**, mas com todas as fotos já coletadas

### Implementação:
```python
# Handler global (group=-1) para interceptar fotos ANTES do ConversationHandler
async def group_album_photos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Agrupar fotos de álbuns antes de processar no ConversationHandler"""
    if not update.message or not update.message.photo:
        return  # Não é uma foto, deixar passar
    
    media_group_id = update.message.media_group_id
    if not media_group_id:
        return  # Não é um álbum, deixar passar
    
    user_id = update.effective_user.id
    
    # Agrupar fotos do mesmo media_group_id
    # ... (lógica de agrupamento)
    
    # Aguardar todas as fotos chegarem (usar timeout)
    # ... (lógica de espera)
    
    # Processar todas as fotos quando todas foram coletadas
    # ... (lógica de processamento)
    
    # Passar apenas a primeira foto para o ConversationHandler
    # ... (outras fotos são ignoradas)
```

## 🚧 Status Atual

- ✅ Código atual coleta fotos do álbum
- ❌ Não aguarda todas as fotos chegarem
- ❌ Processa apenas a primeira foto
- ❌ Muda estado prematuramente

## 📝 Próximos Passos

1. Implementar handler global (`group=-1`) para interceptar fotos
2. Agrupar fotos do mesmo `media_group_id`
3. Aguardar todas as fotos chegarem (usar timeout)
4. Processar todas as fotos quando todas foram coletadas
5. Passar apenas a primeira foto para o ConversationHandler
6. Testar com múltiplas fotos

## ⚠️ Nota Importante

Esta solução requer refatoração significativa do código atual. O handler global precisa:
- Interceptar todas as fotos ANTES do ConversationHandler
- Agrupar fotos do mesmo `media_group_id`
- Aguardar todas as fotos chegarem
- Processar todas as fotos quando todas foram coletadas
- Passar apenas a primeira foto para o ConversationHandler

## 🔗 Referências

- [python-telegram-bot: Handling Media Groups](https://github.com/python-telegram-bot/python-telegram-bot/discussions/3143)
- [Stack Overflow: Telegram bot can't receive multiple pics](https://stackoverflow.com/questions/64719959/telegram-bot-cant-receive-multiple-pics-at-one-message)


