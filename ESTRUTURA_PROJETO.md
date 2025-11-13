# 📁 Estrutura do Projeto

## 📂 Estrutura de Diretórios

```
Bot/
├── main.py                    # Código principal do bot
├── config.py                  # Configurações e variáveis de ambiente
├── notion_api.py              # API do Notion
├── check_config.py            # Script de verificação de configuração
├── requirements.txt           # Dependências Python
├── Procfile                   # Comando de inicialização (Railway)
├── .gitignore                 # Arquivos ignorados pelo Git
├── .env.example               # Template de variáveis de ambiente
├── README.md                  # Documentação principal
│
├── docs/                      # Documentação
│   ├── README.md             # Índice da documentação
│   ├── deploy/               # Documentação de deploy
│   │   ├── CHECKLIST_DEPLOY_RAILWAY.md
│   │   ├── QUICK_START_RAILWAY.md
│   │   └── RESUMO_DEPLOY.md
│   ├── implementacao/        # Guias de implementação
│   │   ├── GUIA_IMPLEMENTACAO_FASE1.md
│   │   ├── GUIA_IMPLEMENTACAO_FASE2A.md
│   │   ├── GUIA_IMPLEMENTACAO_FASE2B.md
│   │   └── ...
│   ├── analises/             # Análises técnicas
│   │   ├── ANALISE_FASE1_PERGUNTAS.md
│   │   ├── ANALISE_FLUXO_FASE2.md
│   │   ├── ESTRUTURA_INVENTARIO.md
│   │   └── ...
│   ├── n8n/                  # Guias e códigos n8n
│   │   ├── INSTRUCOES_IMPORTAR_N8N.md
│   │   ├── MONTAR_WORKFLOW_FASE2A.md
│   │   ├── CODIGO_BUSCA_FUZZY_N8N.txt
│   │   └── ...
│   ├── operacao/             # Guias operacionais
│   │   ├── COMO_ACOMPANHAR_LOGS.md
│   │   ├── COMO_REINICIAR_BOT.md
│   │   ├── TESTE_BOT.md
│   │   └── ...
│   ├── historico/            # Histórico e soluções
│   │   ├── PROBLEMA_WEBHOOK.md
│   │   ├── SOLUCAO_ALBUM_PENDENTE.md
│   │   └── ...
│   ├── REGRAS_BUSCA_ATENDIMENTO.md
│   ├── RESUMO_FILTRO_RELATORIO.md
│   └── ...
│
├── n8n/                      # Workflows n8n
│   ├── Relatório de Visita - Fase 1 - COM ATENDIMENTO.json
│   ├── Relatório de Visita - Fase 1.json
│   ├── Relatório de Visita - Fase 2A - Processar (COM TESTE).json
│   ├── Relatório de Visita - Fase 2A - Processar.json
│   ├── Relatório de Visita - Fase 2B - Salvar.json
│   ├── Relatório de Visita - Fase 2.json
│   └── ...
│
├── scripts/                  # Scripts auxiliares
│   ├── processar_csv_ingredientes.py
│   ├── ingredientes.csv
│   ├── ingredientes_processado.csv
│   ├── INICIAR_BOT.sh
│   └── REINICIAR_BOT.sh
│
├── venv/                     # Ambiente virtual (não commitado)
└── logs/                     # Logs (criado em runtime, não commitado)
    └── bot.log
```

---

## 📄 Arquivos na Raiz

### Essenciais
- `main.py` - Código principal do bot
- `config.py` - Configurações
- `notion_api.py` - API do Notion
- `requirements.txt` - Dependências
- `Procfile` - Comando Railway
- `.gitignore` - Arquivos ignorados
- `.env.example` - Template de variáveis
- `README.md` - Documentação principal

### Opcionais
- `check_config.py` - Script de verificação
- `ESTRUTURA_PROJETO.md` - Esta documentação

---

## 📁 Diretórios

### `/docs/` - Documentação
- **`deploy/`** - Guias de deploy
- **`implementacao/`** - Guias de implementação
- **`analises/`** - Análises técnicas
- **`n8n/`** - Guias e códigos n8n
- **`operacao/`** - Guias operacionais
- **`historico/`** - Histórico e soluções

### `/n8n/` - Workflows n8n
- Workflows JSON para importar no n8n
- Arquivos de configuração

### `/scripts/` - Scripts Auxiliares
- Scripts Python auxiliares
- Scripts shell (start, restart)
- Arquivos CSV de dados

---

## 🔒 Arquivos Não Commitados

### No `.gitignore`:
- `.env` - Variáveis de ambiente
- `*.log` - Logs
- `venv/` - Ambiente virtual
- `__pycache__/` - Cache Python
- `*.pid` - Arquivos PID
- `*.csv` - Dados sensíveis (opcional)

---

## 🚀 Próximos Passos

1. **Verificar estrutura**: Confirmar que todos os arquivos estão organizados
2. **Criar repositório GitHub**: Fazer push do código
3. **Deploy no Railway**: Configurar e fazer deploy
4. **Testar**: Verificar se tudo funciona

---

## 📝 Notas

- Estrutura organizada por funcionalidade
- Documentação categorizada
- Scripts separados
- Workflows n8n organizados
- Arquivos históricos preservados

---

**Última atualização**: 2025-11-13

