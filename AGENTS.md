# Instruções para agentes

## Objetivo

Permitir a recuperação autorizada das credenciais admin e PPPoE do ZTE F8748 e preparar bridge. Não há dados de uma instalação particular neste checkout. Lê README.md e docs/RECUPERACAO.md antes de agir.

## Escopo e execução

- Ler ou clonar este repositório não autoriza contactar um router, ativar diagnóstico, reiniciar, alterar WAN ou restaurar configurações.
- Na execução solicitada pelo proprietário, confirma o alvo e os dados locais. Usa somente o router autorizado. Não faças varrimentos da rede nem testes noutras unidades.
- Abertura temporária do diagnóstico requer autorização. Reinícios, eliminação de INTERNET e aplicação de bridge requerem uma janela de interrupção autorizada e reposição preparada.
- Não regraves flash, não alteres identificadores PON, não uses factory reset e não faças tentativas automáticas repetidas de ativação.
- Ao abrir um site, verifica primeiro as ferramentas WebMCP. Usa uma ferramenta correspondente quando existir; recorre à interface se não houver ferramenta adequada ou se a execução falhar.
- Prefere os scripts do repo. REA é opcional para análise estática; não é necessário para a desencriptação offline nem justifica instalar motores nativos.

## Dados e saídas

- Trabalha numa pasta privada fora de todos os repositórios Git. O coletor recusa saída dentro de Git antes de abrir diagnóstico.
- Não copies os dumps para este checkout, nem sequer para criar testes. Não uses dados reais em fixtures ou CI.
- Introduz passwords interativamente. Não passes --web-pass, -W ou tokens por mensagens, histórico da shell ou argumentos visíveis.
- Não imprimas passwords, chaves derivadas, MACs, serials ou identificadores GPON nas respostas. Relata apenas os estados de validação e caminhos locais privados quando necessários.
- Usa permissões 0700 para pastas e 0600 para os ficheiros privados. Não os publiques nem os envies a serviços externos.
- As constantes de formato presentes no código são públicas; não são as credenciais admin ou PPPoE de uma unidade.

## Evidência e limites

- Um banner SSH durante a janela ativa demonstra apenas disponibilidade nesse momento. Timeout depois de close não prova que o diagnóstico foi desligado.
- Valida admin com login e privilégios. PPPoE tem de ser extraído do mesmo registo XML que o username exato; extração não equivale a autenticação.
- Confirma vid e identificadores binários. 108 e as MACs fictícias dos exemplos não devem ser presumidos.
- O coletor PPPoE unificado não foi novamente validado ao vivo. Bridge é uma proposta com referência comunitária, ainda por validar na ligação concreta.
- Preserva omci_ipv4_static_1 e o registo da fibra. Não uses Bridge Default na tabela MAC nem Uplink Mode Switch como prova de bridge WAN.

## Verificação de alterações

Corre `bash scripts/check.sh`. Só há testes offline com dados sintéticos. Se alterares a base shell, regenera o coletor com `python3 scripts/preparar_coletor.py`. Atualiza SHA256SUMS.txt com `python3 scripts/update_checksums.py`, revê o diff e corre novamente os checks. Nunca abres o diagnóstico para validar uma alteração ao repositório sem autorização específica.
