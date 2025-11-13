# 🚀 Execute Estes Comandos no Terminal

## 📋 Copie e Cole no Terminal

```bash
cd /Users/erickcardealdossantos/Desktop/Bot
git push -u origin main
```

---

## 🔐 Quando Solicitar Credenciais

### **Usuário:**
```
erickcardeal
```

### **Senha:**
**⚠️ NÃO use sua senha do GitHub!**

Use um **Personal Access Token**:

### Como Criar o Token:

1. **Acesse**: https://github.com/settings/tokens
2. **Clique em**: "Generate new token" → "Generate new token (classic)"
3. **Nome**: `chef-bot-deploy`
4. **Expiração**: Escolha (recomendo 90 dias ou sem expiração)
5. **Permissões**: Marque `repo` (acesso completo a repositórios)
6. **Clique em**: "Generate token" (no final da página)
7. **COPIE O TOKEN** (aparece apenas uma vez! Salve em local seguro)
8. **Use o token como senha** quando o Terminal solicitar

---

## ✅ O Que Vai Acontecer

Após executar o comando e fornecer as credenciais:

```
Enumerating objects: 65, done.
Counting objects: 100% (65/65), done.
Delta compression using up to X threads
Compressing objects: 100% (XX/XX), done.
Writing objects: 100% (XX/XX), done.
To https://github.com/erickcardeal/chef-bot-relatorio.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

---

## 🎯 Passo a Passo Visual

1. **Abra o Terminal** (Cmd + Espaço → "Terminal")
2. **Cole o comando**: `cd /Users/erickcardealdossantos/Desktop/Bot`
3. **Pressione Enter**
4. **Cole o comando**: `git push -u origin main`
5. **Pressione Enter**
6. **Quando solicitar usuário**: Digite `erickcardeal` e pressione Enter
7. **Quando solicitar senha**: Cole o Personal Access Token e pressione Enter
8. **Aguarde** o push completar

---

## 📝 Comandos Completos (Copie Tudo)

```bash
cd /Users/erickcardealdossantos/Desktop/Bot
git push -u origin main
```

Depois:
- **Usuário**: `erickcardeal`
- **Senha**: Seu Personal Access Token

---

## 🔗 Links Úteis

- **Criar Token**: https://github.com/settings/tokens
- **Repositório**: https://github.com/erickcardeal/chef-bot-relatorio
- **Railway**: https://railway.app/

---

## 🆘 Problemas?

### Erro: "Authentication failed"
- Verifique se o token está correto
- Verifique se o token tem permissão `repo`
- Crie um novo token se necessário

### Erro: "Permission denied"
- Verifique se tem acesso ao repositório
- Verifique se o repositório existe

### Erro: "Repository not found"
- Verifique se o nome do repositório está correto
- Verifique se o repositório é público ou você tem acesso

---

**Última atualização**: 2025-11-13

