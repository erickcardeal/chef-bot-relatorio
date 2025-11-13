# 📋 Guia: Processar CSV de Ingredientes

## 🎯 Objetivo

Processar CSV de ingredientes e adicionar colunas necessárias:
- **Sinônimos**: Lista de sinônimos separados por vírgula
- **Tempero Sensível**: Sim/Não
- **Aviso**: Mensagem personalizada para temperos sensíveis
- **Unidade Padrão**: g (gramas) ou ml (mililitros)

---

## 🚀 Como Usar

### 1. Preparar o CSV

Certifique-se de que o CSV tenha pelo menos uma coluna com o nome dos ingredientes:
- `Nome` ou `Nome Oficial` ou `nome`
- `Categoria` (opcional, mas recomendado)

### 2. Executar o Script

```bash
# Ativar ambiente virtual (se necessário)
source venv/bin/activate

# Processar CSV
python processar_csv_ingredientes.py ingredientes.csv ingredientes_processado.csv
```

**Parâmetros:**
- `ingredientes.csv`: Arquivo CSV de entrada
- `ingredientes_processado.csv`: Arquivo CSV de saída (opcional, padrão: `ingredientes_processado.csv`)

### 3. Revisar o CSV Processado

O script irá:
- ✅ Adicionar colunas necessárias
- ✅ Gerar sinônimos básicos automaticamente
- ✅ Identificar temperos sensíveis automaticamente
- ✅ Determinar unidades baseado em categoria/nome
- ✅ Criar avisos para temperos sensíveis

### 4. Ajustar Manualmente (se necessário)

Após processar, você pode:
- Ajustar sinônimos manualmente (adicionar mais variações)
- Verificar se todos os temperos sensíveis foram identificados
- Ajustar unidades se necessário
- Personalizar avisos

### 5. Importar para Google Sheets

1. Abrir Google Sheets
2. Arquivo → Importar
3. Selecionar o CSV processado
4. Configurar colunas conforme necessário

---

## 📊 Estrutura do CSV

### Colunas de Entrada (mínimas)

| Nome | Categoria |
|------|-----------|
| Arroz branco | Grãos |
| Pimenta do reino | Temperos |
| Leite integral | Laticínios |

### Colunas de Saída

| Nome Oficial | Sinônimos | Categoria | Unidade Padrão | Tempero Sensível | Aviso |
|-------------|-----------|-----------|----------------|------------------|-------|
| Arroz branco | arroz branco, arroz | Grãos | g | Não | - |
| Pimenta do reino | pimenta do reino, pimenta, pimenta preta | Temperos | g | Sim | ⚠️ ATENÇÃO: Verifique se a quantidade está correta! |
| Leite integral | leite integral, leite | Laticínios | ml | Não | - |

---

## 🔧 Funcionalidades do Script

### 1. Geração Automática de Sinônimos

O script gera sinônimos básicos automaticamente:
- Nome em minúsculas
- Variações com/sem artigo
- Plural/singular

**Exemplo:**
- Entrada: "Arroz branco"
- Sinônimos gerados: "arroz branco, arroz"

### 2. Identificação Automática de Temperos Sensíveis

O script identifica automaticamente temperos sensíveis baseado em uma lista:
- Pimenta (do reino, preta, calabresa, etc.)
- Curcuma/Açafrão
- Canela
- Noz-moscada
- Páprica
- Cominho
- etc.

**Exemplo:**
- Entrada: "Pimenta do reino"
- Tempero Sensível: "Sim"
- Aviso: "⚠️ ATENÇÃO: Verifique se a quantidade está correta!"

### 3. Determinação Automática de Unidades

O script determina unidades baseado em:
- **Categoria**: Laticínios → ml
- **Nome**: Leite, Azeite, Óleo → ml
- **Padrão**: Sólidos → g

**Exemplo:**
- Entrada: "Leite integral" (Categoria: Laticínios)
- Unidade: "ml"

---

## ⚙️ Personalização

### Adicionar Mais Temperos Sensíveis

Edite o arquivo `processar_csv_ingredientes.py` e adicione à lista `TEMPEROS_SENSIVEIS`:

```python
TEMPEROS_SENSIVEIS = [
    'pimenta',
    'curcuma',
    'açafrão',
    # Adicione mais aqui
    'seu tempero aqui',
]
```

### Ajustar Geração de Sinônimos

Edite a função `gerar_sinonimos()` para personalizar a geração de sinônimos:

```python
def gerar_sinonimos(nome: str, categoria: str = "") -> str:
    # Sua lógica personalizada aqui
    ...
```

### Ajustar Determinação de Unidades

Edite a função `determinar_unidade()` para personalizar a determinação de unidades:

```python
def determinar_unidade(categoria: str, nome: str) -> str:
    # Sua lógica personalizada aqui
    ...
```

---

## 📝 Exemplos de Uso

### Exemplo 1: Processar CSV Básico

```bash
python processar_csv_ingredientes.py ingredientes.csv
```

**Saída:**
- Arquivo: `ingredientes_processado.csv`
- Colunas adicionadas: Sinônimos, Tempero Sensível, Aviso, Unidade Padrão

### Exemplo 2: Processar CSV com Nome Personalizado

```bash
python processar_csv_ingredientes.py ingredientes.csv ingredientes_final.csv
```

**Saída:**
- Arquivo: `ingredientes_final.csv`
- Mesmas colunas adicionadas

### Exemplo 3: Processar CSV com Colunas Existentes

Se o CSV já tiver algumas colunas (ex: `Sinônimos`, `Tempero Sensível`), o script:
- ✅ Usa as colunas existentes
- ✅ Completa colunas faltantes
- ✅ Mantém dados existentes

---

## ✅ Checklist de Validação

Após processar o CSV, verifique:

- [ ] Todas as colunas foram adicionadas
- [ ] Sinônimos foram gerados corretamente
- [ ] Temperos sensíveis foram identificados
- [ ] Unidades foram determinadas corretamente
- [ ] Avisos foram criados para temperos sensíveis
- [ ] Dados existentes foram preservados

---

## 🐛 Troubleshooting

### Erro: "Arquivo não encontrado"

**Solução:**
- Verifique se o arquivo existe no diretório atual
- Verifique o caminho do arquivo
- Use caminho absoluto se necessário

### Erro: "Nome não encontrado"

**Solução:**
- Verifique se o CSV tem uma coluna com nomes
- Colunas aceitas: `Nome`, `Nome Oficial`, `nome`
- Ajuste o script se necessário

### Erro: "Encoding"

**Solução:**
- Certifique-se de que o CSV está em UTF-8
- Use um editor de texto para converter para UTF-8
- Verifique se há caracteres especiais

---

## 💡 Dicas

### 1. Fazer Backup

Antes de processar, faça backup do CSV original:

```bash
cp ingredientes.csv ingredientes_backup.csv
```

### 2. Revisar Sinônimos

Após processar, revise os sinônimos gerados:
- Adicione mais variações se necessário
- Remova sinônimos incorretos
- Adicione nomes populares/regionais

### 3. Verificar Temperos Sensíveis

Verifique se todos os temperos sensíveis foram identificados:
- Adicione mais à lista se necessário
- Ajuste a lógica de identificação se necessário

### 4. Testar com Amostra

Teste primeiro com uma amostra pequena do CSV:

```bash
# Criar amostra (primeiras 10 linhas)
head -11 ingredientes.csv > ingredientes_amostra.csv

# Processar amostra
python processar_csv_ingredientes.py ingredientes_amostra.csv
```

---

## 🎯 Próximos Passos

1. ✅ Processar CSV
2. ✅ Revisar CSV processado
3. ✅ Ajustar sinônimos manualmente (se necessário)
4. ✅ Verificar temperos sensíveis
5. ✅ Importar para Google Sheets
6. ✅ Configurar n8n para ler Google Sheets
7. ✅ Testar fluxo completo

---

## 📞 Suporte

Se tiver dúvidas ou problemas:
1. Verifique o arquivo de log (se houver)
2. Revise a estrutura do CSV
3. Verifique se todas as dependências estão instaladas
4. Entre em contato com o time de tecnologia

---

## ✅ Conclusão

O script `processar_csv_ingredientes.py` automatiza o processamento do CSV de ingredientes, adicionando todas as colunas necessárias para o fluxo de inventário.

**Vantagens:**
- ✅ Automatiza processo manual
- ✅ Gera sinônimos básicos automaticamente
- ✅ Identifica temperos sensíveis automaticamente
- ✅ Determina unidades automaticamente
- ✅ Cria avisos para temperos sensíveis
- ✅ Preserva dados existentes

**Próximo passo:**
- Processar seu CSV
- Revisar resultado
- Ajustar manualmente se necessário
- Importar para Google Sheets

Quer que eu processe seu CSV diretamente? Envie o arquivo e eu faço as alterações!

