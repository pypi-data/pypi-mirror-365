# beta-Cynosure
Aplicação para extrair dados Anuais e Trimestrais da CVM de todas as empresas

Este projeto realiza o download e processamento automatizado das demonstrações financeiras da CVM (DFP e ITR) para companhias abertas no Brasil. 

Ele foi o rascunho para a aplicação com AI para obtenção, processamento, armazenamento, atualização e análise de dados.

## Funcionalidade
Baixa os dados anuais (DFP) e trimestrais (ITR) diretamente do portal da CVM.

Calcula o número de trimestre com base nas datas.

Gera dois arquivos CSV: um com dados anuais e outro com dados trimestrais.

## Como usar
Installe a lib, use o comando b-cynosure acompanhado do ano de início - ano fim do período, exemplo:

```
b-cynosure 2020-2024
```

Execute o script principal: main.py.

Os arquivos de saída serão salvos na pasta output/.
