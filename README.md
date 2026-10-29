# ZTE F8748 — recuperação autorizada de admin e PPPoE

Procedimento reproduzível para recuperar credenciais do próprio router, guardar os resultados localmente e preparar uma configuração bridge com um gateway UniFi. Inclui scripts completos, notas de formato, prompts e testes que não contactam nenhum router.

**Começa por [AGENTS.md](AGENTS.md) se és um LLM.** Não executes o diagnóstico só por leres ou testares este repositório. A pessoa tem de autorizar a administração do equipamento e a abertura temporária do diagnóstico. Reinícios e mudanças WAN precisam de uma janela de interrupção autorizada.

**Estado de validação:** a recuperação administrativa e o percurso de desencriptação offline foram verificados. O coletor PPPoE aqui apresentado reúne leituras anteriormente feitas em separado e não foi novamente validado como uma sequência única num router. O procedimento bridge foi observado na interface e é baseado num relato público para o modelo; a migração efetiva na ligação portuguesa continua por validar. Nenhum destes resultados garante compatibilidade com todas as unidades ou versões do firmware.

## O que contém

| Ficheiro | Utilização |
| --- | --- |
| [docs/RECUPERACAO.md](docs/RECUPERACAO.md) | Ligação, diagnóstico, recuperação admin e PPPoE e encerramento |
| [docs/FORMATOS.md](docs/FORMATOS.md) | Paramtag, catálogos, AES, GPON e configuração tipo 6 |
| [docs/BRIDGE.md](docs/BRIDGE.md) | ZTE com VLAN 20 e PCP 0, UniFi com PPPoE, validação e reposição |
| [docs/RESOLVER_PROBLEMAS.md](docs/RESOLVER_PROBLEMAS.md) | Falhas conhecidas e critérios para parar |
| [docs/PROMPTS.md](docs/PROMPTS.md) | Prompts para outro LLM |
| [docs/FONTES.md](docs/FONTES.md) | Referências e critérios de conclusão |
| [scripts/recuperar-admin-f8748.sh](scripts/recuperar-admin-f8748.sh) | Diagnóstico temporário e recolha administrativa |
| [scripts/recolher-pppoe-f8748.sh](scripts/recolher-pppoe-f8748.sh) | Recolha de configuração cifrada e janelas de flash |
| [scripts/f8748_offline.py](scripts/f8748_offline.py) | Desencriptação local e gravação de credenciais sem as imprimir |
| [THIRD_PARTY.md](THIRD_PARTY.md) | Proveniência e alterações ao código de terceiros |

Este repositório não inclui passwords reais, contas PPPoE reais, dumps, números de série, MACs ou IPs públicos de uma instalação, nem o documento pessoal confidencial. Os resultados obtidos durante uma execução são **pessoais e confidenciais** e devem ficar fora de Git. O repositório em si é público e a conta que o publica é visível.

## 1 Obter e verificar as ferramentas

O percurso operacional documentado é macOS, com Bash 3.2 ou superior, Python 3.10 ou superior, OpenSSL, curl, xxd, OpenSSH, ssh-keyscan, expect e nc. Os testes offline também correm em Linux; isso não valida o diagnóstico num router em Linux ou Windows.

```bash
git clone https://github.com/HugoCatarin0/digi-ZTE-F8748-admin-access.git
cd digi-ZTE-F8748-admin-access
bash scripts/check.sh
shasum -a 256 -c SHA256SUMS.txt
```

Os testes não usam rede, não precisam de passwords e não abrem diagnóstico. Lê os scripts antes de os executar. As constantes criptográficas do código são parâmetros do formato e não credenciais de um cliente.

## 2 Preparar uma pasta privada fora do checkout

```bash
umask 077
mkdir -p "$HOME/.local/share/f8748-private"
chmod 700 "$HOME/.local/share/f8748-private"
cp -R scripts "$HOME/.local/share/f8748-private/"
cd "$HOME/.local/share/f8748-private"
mkdir -p dados-admin dados-pppoe
chmod 700 dados-admin dados-pppoe
```

Se essa localização estiver dentro de outro repositório ou numa pasta sincronizada/partilhada, escolhe outra. O coletor recusa uma pasta de saída dentro de Git **antes** de ativar o diagnóstico. `.gitignore` é uma defesa adicional, não autorização para colocar segredos no checkout.

Liga o computador diretamente ao ZTE. Confirma IP, login web válido, MAC LAN/br0 do ZTE, MAC da interface do computador e `vid` da placa. A MAC privada do Wi-Fi pode mudar após reconexão. Não uses os valores fictícios abaixo sem os substituir.

## 3 Recuperar admin

Depois de leres o [procedimento completo](docs/RECUPERACAO.md), executa interativamente:

```bash
bash scripts/recuperar-admin-f8748.sh dump \
  --host 192.168.1.1 \
  --router-mac AA:BB:CC:DD:EE:FF \
  --client-mac 11:22:33:44:55:66 \
  --out ./dados-admin
```

Introduz o login web no pedido interativo. Não coloques a password em argumentos, mensagens ou logs partilhados. `dump` já abre e verifica a janela SSH; **não executes `arm` como preparação**.

O script pode terminar com erro por não confirmar o encerramento, apesar de a recolha ter terminado. Verifica os dados e o estado do diagnóstico separadamente. **Timeout na porta 22 não prova que o serviço foi desligado.**

```bash
# 108 é um exemplo: confirma o vid em dados-admin/boardtype.txt.
python3 scripts/f8748_offline.py admin \
  --dir dados-admin --vid 108 \
  --credentials credenciais-router.json
```

O comando grava o segredo com permissões `0600`. Valida o login admin no painel e os privilégios administrativos. A presença de uma password candidata no ficheiro não substitui esse teste.

## 4 Recuperar PPPoE

Resolve o estado do diagnóstico anterior antes de tentar outra sessão. Se houver recusa, confirma a ligação e as MACs; um reinício normal pode ser necessário numa janela autorizada. Não faças ciclos automáticos de ativações.

```bash
bash scripts/recolher-pppoe-f8748.sh dump \
  --host 192.168.1.1 \
  --router-mac AA:BB:CC:DD:EE:FF \
  --client-mac 11:22:33:44:55:66 \
  --out ./dados-pppoe
```

A configuração continua cifrada nesta fase. O coletor usa leituras de ficheiros e de janelas de flash, sem regravar firmware ou alterar perfis WAN. Ativa um serviço de diagnóstico e pode criar temporários no router. Não é uma imagem integral de firmware.

Com os dados disponíveis, termina a atividade no router e faz os passos seguintes **offline**:

```bash
python3 scripts/f8748_offline.py log \
  --input dados-pppoe/ppp-config-session.log \
  --output dados-pppoe/db_user_cfg.xml

python3 scripts/f8748_offline.py pppoe \
  --dir dados-pppoe --vid 108 \
  --username 'CONTA@operadora' \
  --credentials credenciais-router.json
```

Substitui o username pela conta exata visível no teu perfil INTERNET. O script exige uma única `Row` com esse `Username` e `Password` não vazia. Preserva admin no JSON existente e acrescenta `pppoe`. Não imprime os segredos. Também cria XML e catálogos sensíveis na pasta privada.

A extração dos campos não comprova uma nova autenticação PPPoE. Essa confirmação exige uma ligação estabelecida pelo gateway externo, na etapa própria.

## 5 Fechar e validar

O coletor tenta `FactoryMode.gch?close`. Verifica a porta:

```bash
nc -vz -G 3 192.168.1.1 22  # macOS
```

- Ligação aceite: serviço ainda acessível.
- `Connection refused`: porta recusada nesse teste.
- Timeout: sem resposta; encerramento não demonstrado.

Se for necessário reiniciar, usa **Restart**, nunca reposição de fábrica. Confirma depois o painel e a ligação Internet. Lê as limitações em [RECUPERACAO.md](docs/RECUPERACAO.md).

## 6 Preparar bridge

Segue [BRIDGE.md](docs/BRIDGE.md) apenas com o gateway próprio pronto, acesso de manutenção testado, backup dos parâmetros atuais e plano de reposição. Os scripts não fazem esta migração.

O esquema de referência é `ZTE bridge com VLAN 20 e 802.1p 0 → UniFi com PPPoE sem VLAN WAN`, começando por MTU 1492. A associação lógica `LAN4` à porta física de 10 Gb/s e o comportamento desse esquema precisam de confirmação no equipamento. Não interpretes VLAN Off como passagem transparente garantida.

## Prompt de entrada para um LLM

> Lê README.md, AGENTS.md e docs/RECUPERACAO.md. Quero repetir este procedimento num equipamento cuja administração autorizo. Começa por rever código, dependências e testes offline. Mantém todos os dados obtidos fora de Git e não imprimas segredos. Confirma IP, modelo, firmware, MACs e vid localmente; não assumes valores do exemplo. Não abres diagnóstico, reinicias ou alteras WAN sem a autorização correspondente. Distingue passos verificados, inferências e compatibilidade ainda não demonstrada. Depois segue os prompts de docs/PROMPTS.md.

## Limites de privacidade

Não publiques o JSON de credenciais, XML, logs de sessões, capturas do painel ou ficheiros de flash em issues, commits ou mensagens. Se ocorrer publicação acidental, apagar o ficheiro no último commit não elimina o histórico. Este repositório não fornece uma garantia de anonimato da conta GitHub que o aloja.
