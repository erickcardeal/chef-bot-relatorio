#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para processar CSV de ingredientes e adicionar colunas necessárias:
- Sinônimos
- Tempero Sensível
- Aviso
- Unidade Padrão (se não existir)
"""

import csv
import sys
import os
from typing import Dict, List, Optional
import unicodedata

# Lista de temperos sensíveis conhecidos
TEMPEROS_SENSIVEIS = [
    'pimenta',
    'curcuma',
    'açafrão',
    'açafrão da terra',
    'açafrão em pó',
    'cúrcuma',
    'canela',
    'noz-moscada',
    'páprica',
    'cominho',
    'pimenta do reino',
    'pimenta preta',
    'pimenta calabresa',
    'pimenta caiena',
    'pimenta verde',
    'pimenta tabasco',
    'pimenta de cheiro',
    'pimenta dedo de moça',
    'pimentão',  # Nota: pimentão geralmente não é sensível, mas vamos marcar para revisão
    'curry',
    'zatar',
]

def normalizar_texto(texto: str) -> str:
    """Normalizar texto (remover acentos, minúsculas)"""
    if not texto:
        return ""
    # Remover acentos
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
    # Converter para minúsculas
    texto = texto.lower().strip()
    return texto

def identificar_tempero_sensivel(nome: str) -> bool:
    """Identificar se ingrediente é tempero sensível"""
    nome_normalizado = normalizar_texto(nome)
    for tempero in TEMPEROS_SENSIVEIS:
        if normalizar_texto(tempero) in nome_normalizado:
            return True
    return False

def gerar_sinonimos(nome: str, categoria: str = "") -> str:
    """Gerar sinônimos básicos para um ingrediente"""
    nome_lower = nome.lower().strip()
    sinonimos = [nome_lower]
    
    # Remover prefixos comuns
    prefixos = ['carne bovina -', 'carne suína -', 'carne cordeiro -', 'carne do futuro -', 
                'frango -', 'peixe -', 'queijo -', 'massa -', 'arroz -', 'feijão -',
                'cogumelo -', 'cogumelos -', 'embutidos -', 'vinagre -', 'vinho branco -',
                'vinho tinto -', 'molho de peixe -']
    
    nome_sem_prefixo = nome_lower
    for prefixo in prefixos:
        if nome_lower.startswith(prefixo):
            nome_sem_prefixo = nome_lower[len(prefixo):].strip()
            sinonimos.append(nome_sem_prefixo)
            break
    
    # Adicionar variações sem hífen (ex: "arroz - branco" -> "arroz branco")
    if ' - ' in nome_lower:
        partes = nome_lower.split(' - ')
        if len(partes) == 2:
            sinonimos.append(partes[1].strip())  # Só a parte depois do hífen
            sinonimos.append(' '.join(partes).strip())  # Tudo junto sem hífen
    
    # Adicionar variações sem barra (ex: "abóbora cabotiá/japonesa" -> "abóbora cabotiá", "abóbora japonesa")
    if '/' in nome_lower:
        partes = nome_lower.split('/')
        for parte in partes:
            parte_limpa = parte.strip()
            if parte_limpa:
                sinonimos.append(parte_limpa)
    
    # Adicionar nome sem artigo (ex: "o arroz" -> "arroz")
    if nome_lower.startswith(('o ', 'a ', 'os ', 'as ')):
        sinonimos.append(nome_lower[2:].strip())
    
    # Remover duplicatas e ordenar
    sinonimos = sorted(list(set([s for s in sinonimos if s])))
    
    return ', '.join(sinonimos)

def determinar_unidade(categoria: str, nome: str, unidade_medida: str = '') -> str:
    """Determinar unidade padrão baseado em categoria e nome"""
    nome_lower = nome.lower()
    categoria_lower = categoria.lower() if categoria else ''
    
    # Líquidos (baseado em categoria e nome)
    if 'laticínios' in categoria_lower or 'leite' in nome_lower or 'azeite' in nome_lower or 'óleo' in nome_lower or 'vinagre' in nome_lower or 'vinho' in nome_lower or 'saquê' in nome_lower:
        # Se já está em ml, manter
        if unidade_medida.lower() == 'ml':
            return 'ml'
        # Se está em g mas é líquido, converter para ml
        return 'ml'
    
    # Óleos e gorduras
    if 'óleos e gorduras' in categoria_lower or 'óleo' in nome_lower or 'azeite' in nome_lower:
        return 'ml'
    
    # Bebidas alcoólicas
    if 'alcóolicos' in categoria_lower or 'alcoolicos' in categoria_lower:
        return 'ml'
    
    # Sólidos (padrão) - sempre em gramas
    return 'g'

def criar_aviso(tempero_sensivel: bool) -> str:
    """Criar aviso para temperos sensíveis"""
    if tempero_sensivel:
        return '⚠️ ATENÇÃO: Verifique se a quantidade está correta!'
    return '-'

def processar_csv(arquivo_entrada: str, arquivo_saida: str):
    """Processar CSV e adicionar colunas necessárias"""
    
    # Ler CSV
    linhas = []
    colunas_existentes = []
    
    try:
        with open(arquivo_entrada, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            colunas_existentes = reader.fieldnames or []
            
            for linha in reader:
                linhas.append(linha)
    except FileNotFoundError:
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        sys.exit(1)
    
    # Verificar colunas existentes
    print(f"📊 Colunas existentes: {', '.join(colunas_existentes)}")
    
    # Definir colunas necessárias
    colunas_necessarias = [
        'Ingrediente',
        'Sinônimos',
        'Categoria',
        'Unidade Padrão',
        'Tempero Sensível',
        'Aviso'
    ]
    
    # Mapear colunas existentes (case-insensitive)
    mapa_colunas = {}
    colunas_mapeamento = {
        'Ingrediente': ['ingrediente', 'nome', 'nome oficial'],
        'Sinônimos': ['sinônimos', 'sinonimos', 'sinonimo'],
        'Categoria': ['categoria', 'categoria'],
        'Unidade Padrão': ['unidade padrão', 'unidade padrao', 'unidade_padrao'],
        'Tempero Sensível': ['tempero sensível', 'tempero sensivel', 'tempero_sensivel'],
        'Aviso': ['aviso', 'warning'],
    }
    
    for col_necessaria, variações in colunas_mapeamento.items():
        for col_existente in colunas_existentes:
            if col_existente.lower() in variações:
                mapa_colunas[col_necessaria] = col_existente
                break
    
    print(f"📋 Colunas mapeadas: {mapa_colunas}")
    
    # Processar linhas
    linhas_processadas = []
    
    for i, linha in enumerate(linhas, 1):
        linha_processada = {}
        
        # Ingrediente (Nome Oficial)
        nome_oficial = linha.get(mapa_colunas.get('Ingrediente', 'Ingrediente')) or linha.get('ingrediente') or linha.get('Ingrediente') or ''
        if not nome_oficial:
            print(f"⚠️ Linha {i}: Nome não encontrado, pulando...")
            continue
        
        linha_processada['Ingrediente'] = nome_oficial
        
        # Categoria
        categoria = linha.get(mapa_colunas.get('Categoria', 'Categoria')) or linha.get('categoria') or linha.get('Categoria') or 'Outros'
        linha_processada['Categoria'] = categoria
        
        # Unidade de Medida (manter coluna original)
        unidade_medida = linha.get('Unidade de Medida') or linha.get('unidade de medida') or ''
        
        # Sinônimos (gerar se não existir ou se estiver vazio)
        sinonimos_existentes = linha.get(mapa_colunas.get('Sinônimos', 'Sinônimos')) or linha.get('sinônimos') or linha.get('sinonimos') or ''
        if sinonimos_existentes and sinonimos_existentes.strip():
            linha_processada['Sinônimos'] = sinonimos_existentes
        else:
            # Gerar sinônimos básicos
            sinonimos = gerar_sinonimos(nome_oficial, categoria)
            linha_processada['Sinônimos'] = sinonimos
            if i <= 10:  # Mostrar apenas primeiros 10 para não poluir
                print(f"✅ Linha {i}: Gerados sinônimos para '{nome_oficial}': {sinonimos[:50]}...")
        
        # Unidade Padrão (sempre g para sólidos, ml para líquidos)
        unidade_padrao_existente = linha.get(mapa_colunas.get('Unidade Padrão', 'Unidade Padrão')) or linha.get('unidade padrão') or ''
        if unidade_padrao_existente and unidade_padrao_existente.strip():
            linha_processada['Unidade Padrão'] = unidade_padrao_existente
        else:
            # Determinar unidade baseado em categoria e nome
            unidade = determinar_unidade(categoria, nome_oficial, unidade_medida)
            linha_processada['Unidade Padrão'] = unidade
        
        # Tempero Sensível
        tempero_existente = linha.get(mapa_colunas.get('Tempero Sensível', 'Tempero Sensível')) or linha.get('tempero sensível') or ''
        if tempero_existente and tempero_existente.strip():
            linha_processada['Tempero Sensível'] = tempero_existente
        else:
            # Identificar automaticamente
            tempero_sensivel = identificar_tempero_sensivel(nome_oficial)
            linha_processada['Tempero Sensível'] = 'Sim' if tempero_sensivel else 'Não'
            if tempero_sensivel:
                print(f"⚠️ Linha {i}: Tempero sensível identificado: '{nome_oficial}'")
        
        # Aviso
        aviso_existente = linha.get(mapa_colunas.get('Aviso', 'Aviso')) or linha.get('aviso') or ''
        if aviso_existente and aviso_existente.strip():
            linha_processada['Aviso'] = aviso_existente
        else:
            # Criar aviso baseado em tempero sensível
            tempero_sensivel = linha_processada['Tempero Sensível'] == 'Sim'
            aviso = criar_aviso(tempero_sensivel)
            linha_processada['Aviso'] = aviso
        
        # Adicionar todas as colunas existentes (preservar dados originais)
        for col in colunas_existentes:
            # Se a coluna já foi processada, não sobrescrever
            if col not in linha_processada:
                linha_processada[col] = linha.get(col, '')
        
        linhas_processadas.append(linha_processada)
    
    # Escrever CSV processado
    try:
        # Criar lista de colunas para o CSV (manter ordem original + novas colunas)
        colunas_finais = []
        # Adicionar colunas existentes primeiro
        for col in colunas_existentes:
            if col not in colunas_finais:
                colunas_finais.append(col)
        # Adicionar novas colunas se não existirem
        novas_colunas = ['Tempero Sensível', 'Aviso']
        for nova_col in novas_colunas:
            if nova_col not in colunas_finais:
                colunas_finais.append(nova_col)
        
        with open(arquivo_saida, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=colunas_finais)
            writer.writeheader()
            writer.writerows(linhas_processadas)
        
        print(f"\n✅ CSV processado com sucesso!")
        print(f"📁 Arquivo de saída: {arquivo_saida}")
        print(f"📊 Total de linhas processadas: {len(linhas_processadas)}")
        
    except Exception as e:
        print(f"❌ Erro ao escrever CSV: {e}")
        sys.exit(1)

def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Uso: python processar_csv_ingredientes.py <arquivo_entrada.csv> [arquivo_saida.csv]")
        print("\nExemplo:")
        print("  python processar_csv_ingredientes.py ingredientes.csv ingredientes_processado.csv")
        sys.exit(1)
    
    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2] if len(sys.argv) > 2 else arquivo_entrada.replace('.csv', '_processado.csv')
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo não encontrado: {arquivo_entrada}")
        sys.exit(1)
    
    print(f"📂 Processando arquivo: {arquivo_entrada}")
    print(f"📁 Arquivo de saída: {arquivo_saida}")
    print()
    
    processar_csv(arquivo_entrada, arquivo_saida)
    
    print("\n💡 Próximos passos:")
    print("1. Revisar o CSV processado")
    print("2. Ajustar sinônimos manualmente se necessário")
    print("3. Verificar se todos os temperos sensíveis foram identificados")
    print("4. Importar para Google Sheets")

if __name__ == '__main__':
    main()

