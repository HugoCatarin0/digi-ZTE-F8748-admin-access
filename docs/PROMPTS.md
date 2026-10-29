# Prompts para recuperar as credenciais
Os prompts seguintes podem ser usados com um LLM que tenha acesso local a ficheiros, Terminal e navegador. Fornece o README e o AGENTS.md e autoriza apenas o equipamento que pretendes administrar. Segredos devem ficar em ficheiros locais, não no texto da conversa.

## Prompt inicial

```text
Estou a seguir o README e o AGENTS.md deste repositório para uma recuperação autorizada. Tenho autorização para administrar o equipamento em causa e quero recuperar as credenciais web admin e PPPoE seguindo estas notas. Não publiques dados obtidos do equipamento. Primeiro revê os scripts do repositório, verifica os hashes e confirma modelo, hardware, firmware, IP e ligação direta. Usa os dados desta unidade e não os do exemplo. Antes de abrir sites, verifica ferramentas WebMCP e prefere uma ferramenta adequada; na ausência dela usa a interface. Não alteres WAN, não atives bridge, não faças reset e não reinicies sem uma janela autorizada. Guarda segredos localmente com permissões 0600 e não os imprimas nas respostas.

```

## Prompt para recolha administrativa

```text
Revê recuperar-admin-f8748.sh e usa o comando dump com as MACs LAN e do cliente confirmadas agora. Introduz credenciais interativamente. Faz só uma tentativa de ativação e verifica o banner SSH durante a janela ativa. Se houver erro, distingue recolha incompleta de fecho não confirmado. Tenta a limpeza prevista e verifica a porta 22. Não declares um timeout como prova de encerramento. Usa f8748_offline.py admin para guardar a credencial e valida o login no painel com privilégios administrativos, sem alterar configurações.

```

## Prompt para PPPoE

```text
Já existe uma credencial admin guardada. Revê o coletor PPPoE do repositório e recolhe paramtag, a configuração cifrada e as janelas de flash necessárias. Não uses passwords mascaradas do DOM nem placeholders. Depois trabalha offline: reconstrói o binário do log, preserva a última linha parcial, extrai catálogos com comprimentos big endian e deriva as chaves apenas de identificadores deste equipamento. Seleciona exatamente a Row do username PPPoE indicado por mim e grava a Password no JSON existente sem eliminar admin. Não estabeleças uma nova sessão PPPoE nesta etapa. Relata apenas se cada validação passou.

```
Se o LLM não tiver ferramentas locais, entrega-lhe os ficheiros da pasta scripts para revisão e executa os comandos interativamente. Não peças ao modelo para adivinhar passwords, MACs, prefixos IPv6 ou layouts de memória.

## Prompts para análise e migração bridge

## Prompt para analisar a interface com REA

```text
Analisa apenas os artefactos locais da interface do meu router e as observações autorizadas. Procura os caminhos do menu WAN, criação de perfil, Bridge Connection e Port Binding. Se REA estiver disponível, descobre o schema atual e usa a análise de JavaScript para os ficheiros guardados; não instales motores nativos sem necessidade. Distingue strings presentes no código de opções realmente observadas na interface e de alterações aplicadas. Não envies a configuração nem passwords para serviços externos. Não concluas que Bridge Default na tabela MAC é bridge WAN.

```
REA pode apoiar a análise estática do JavaScript da interface. A recuperação descrita usa também o script comunitário, ferramentas locais e verificação no painel. Para instalar ou configurar REA, segue a documentação atual do projeto e preserva a configuração existente do cliente. [R7]

## Prompt para preparar bridge

```text
Quero usar o ZTE apenas para terminação XGS-PON e bridge, com o gateway UniFi a gerir a rede. Ainda não apliques alterações. Confirma modelo UniFi, capacidade PPPoE, porta de 10 Gb/s, correspondência de LAN4 no ZTE, credenciais, backup e acesso de manutenção. Prepara INTERNET em Bridge Connection com VLAN 20 e PCP 0 no ZTE, associado apenas à porta de uplink do UniFi. No UniFi prepara PPPoE, VLAN WAN desativada e MTU inicial 1492. Preserva omci_ipv4_static_1 e os parâmetros PON. Entrega a configuração concreta e o plano de reposição. Assinala os pontos que ainda precisam de validação no equipamento e na ligação em causa.

```

## Prompt para executar numa janela autorizada

```text
O gateway UniFi está fisicamente ligado e preparado, o acesso de manutenção foi testado e a janela de interrupção está autorizada. Executa a migração preparada, registando cada alteração. Não faças factory reset. Valida PPPoE, DNS, IPv4, IPv6, negociação a 10 Gb/s, desempenho e persistência após reinício autorizado. Desliga Wi-Fi e DHCP do ZTE apenas depois de confirmares Internet e gestão. Se falhar e não houver diagnóstico dentro da janela combinada, repõe o perfil original com os valores guardados. No fim distingue testes concluídos de pendentes e não mostres passwords.

```

[R1]: https://github.com/686f6c61/DIGI-F8748
[R2]: https://github.com/yuleniwo/zxcfg
[R3]: https://bandaancha.eu/foros/configurar-modo-bridge-zte-f8748-1761099
[R4]: https://www.digi.pt/perguntas-frequentes/net
[R5]: https://help.ui.com/hc/en-us/articles/36378535649687-Configuring-IPv6-in-UniFi
[R6]: https://spdl.zyxel.com/GS1200-5/user_guide/GS1200-5_V2.00_Ed4.pdf
[R7]: https://github.com/morluto/rea
