# Definir a arquitetura bridge
**Objetivo.** O ZTE termina a fibra XGS-PON e transporta o serviço de Internet. O gateway UniFi estabelece PPPoE e gere firewall, NAT, DHCP, DNS e as redes internas.

```bash
Fibra DIGI
  |
ZTE F8748
XGS-PON + bridge + VLAN 20 com PCP 0
  |
Ethernet 10 Gb/s sem etiqueta VLAN neste esquema
  |
Gateway UniFi
PPPoE + firewall + NAT + DHCP + redes locais
  |
Switches e pontos de acesso UniFi

```
**VLAN 20.** É o identificador de serviço previsto pelo exemplo de configuração. Mantê-la no ZTE é compatível com bridge: tratar etiquetas Ethernet não obriga o ZTE a fazer NAT ou a autenticar PPPoE. A VLAN WAN não obriga a usar VLAN 20 nas redes internas do UniFi.
**802.1p igual a 0.** Define a marca PCP prevista pelo exemplo. Alterar para 1 não aumenta a velocidade. A prioridade efetiva depende das filas e políticas dos equipamentos; no mapeamento habitual, 0 é Best Effort e 1 é Background. [R6]
**VLAN desligada.** Não foi demonstrado que este firmware faça passagem transparente de todas as etiquetas. Não bases a migração em VLAN Off no ZTE e VLAN 20 no UniFi sem testar essa alternativa separadamente. O procedimento reportado para o F8748 usa VLAN 20 e PCP 0 no ZTE. [R3]
**Suporte.** A DIGI Portugal exclui atualmente o PRO-DIGI 10 Gbps do serviço oficial de router próprio. Este procedimento é uma configuração manual a validar, não uma instrução oficial da operadora. [R4]
**Antes da migração.** Precisas do gateway próprio pronto, credenciais guardadas, cópia dos parâmetros atuais, acesso físico e uma forma de reposição. Num contexto empresarial, faz a mudança numa janela de manutenção e mantém uma ligação alternativa se a disponibilidade for crítica.

## Preparar o gateway UniFi
1. Faz a configuração inicial do gateway sem remover ainda a ligação PPPoE do ZTE. Não ligues duas sessões PPPoE em simultâneo para tentar validar a password.
2. Escolhe a porta WAN com capacidade de 10 Gb/s. Se for SFP+, confirma a compatibilidade do módulo RJ45 com o gateway e com a ligação Ethernet. Uma porta de 10 Gb/s não garante esse débito com PPPoE e inspeção de tráfego ativos.
3. Em Settings → Internet → WAN correspondente, prepara estes parâmetros. Os nomes dos campos podem variar com a versão UniFi.

| Parâmetro UniFi | Valor inicial |
| --- | --- |
| Ligação IPv4 | PPPoE |
| Username e password | Credenciais PPPoE recuperadas |
| VLAN ID na WAN | Desativada neste esquema |
| MTU | 1492 para começar |
| DNS | Automático inicialmente |
| Ligação física | WAN de 10 Gb/s ao ZTE |
A ausência de VLAN no UniFi pressupõe o ZTE a tratar a VLAN 20 na bridge. Não configures a mesma etiqueta nos dois lados por tentativa: isso pode produzir um encapsulamento diferente do esperado.
4. Usa uma LAN UniFi que não coincida com a gestão do ZTE. Exemplo: UniFi em 192.168.10.1/24 e gestão do ZTE numa sub-rede separada. Não ligues uma porta de gestão do ZTE à LAN normal sem desenhar esse acesso.
5. Mantém DHCP, NAT e firewall da rede interna no UniFi. A VLAN 20 da operadora não precisa de ser propagada aos switches ou pontos de acesso internos.
6. Planeia IPv6 com os parâmetros que a DIGI efetivamente fornecer. O UniFi suporta DHCPv6 e delegação de prefixo; confirma o método e o tamanho do prefixo antes de fixar /56, /60 ou /64. Depois distribui os prefixos pelas LANs conforme necessário. [R5]
**Ainda sem Apply no ZTE.** Confirma que consegues entrar localmente no UniFi e que o cabo e a porta WAN estão identificados. Esta preparação deve estar concluída antes de apagar o perfil atual de Internet.

## Criar a bridge no ZTE
A disponibilidade de Bridge Connection depende do firmware e dos privilégios da conta. A sequência abaixo adapta um procedimento público para o modelo e requer validação local antes de ser aplicada. [R3]
1. Guarda uma exportação de configuração, se disponível, e regista por captura ou por escrito os campos do perfil INTERNET e de Port Binding. Guarda-os localmente como dados privados.
2. Confirma acesso de manutenção por outra porta antes de remover a ligação atual. Não desligues DHCP ou alteres o IP de gestão sem saber como voltar a entrar com IP estático.
3. Abre Internet no menu superior e WAN no menu vertical esquerdo. Internet → Status → WAN é apenas uma página de estado e não permite criar perfis.
4. Abre o perfil INTERNET atual. Se Type estiver bloqueado, não é possível trocar PPPoE por bridge diretamente nesse formulário.
5. Na janela de manutenção, remove o perfil INTERNET original e recria-o em Create New Item. O relato para o F8748 indica que apenas desativá-lo não bastou e que é necessário reutilizar o nome INTERNET. Este comportamento precisa de validação local; mantém a reposição preparada.

| Campo do perfil novo | Valor |
| --- | --- |
| Connection Name | INTERNET |
| Type | Bridge Connection |
| VLAN | On |
| VLAN ID | 20 |
| 802.1p | 0 |
6. Aplica o novo perfil. A autenticação PPPoE passará a ser feita pelo UniFi, pelo que o formulário bridge não precisa do username e password PPPoE.
7. Em Internet → Port Binding, associa INTERNET apenas à porta física de 10 Gb/s destinada ao UniFi. O relato usa LAN4; confirma a correspondência com as etiquetas e o estado de link do teu equipamento antes de aplicar.
8. Liga a porta de 10 Gb/s do ZTE à WAN do UniFi e ativa a ligação PPPoE preparada. Aguarda o estabelecimento e acompanha o estado no UniFi.
**Preserva a terminação da fibra.** Não alteres o perfil omci_ipv4_static_1, os identificadores PON ou os parâmetros de registo. Não uses Uplink Mode Switch para esta tarefa: opções PON e LAN selecionam a origem do uplink e não comprovam um modo ONU bridge.

## Validar e retirar funções locais do ZTE
**Primeiro valida Internet.** Antes de desligar outros serviços ou retirar o computador de manutenção, confirma que a nova ligação funciona.
1. No UniFi, confirma PPPoE ligado e um endereço WAN atribuído. Um endereço da faixa 100.64.0.0/10 continua a ser possível: bridge não remove o CGNAT da operadora.
2. Testa resolução DNS e abre vários sites. Testa também um cliente por cabo, para separar problemas WAN de problemas Wi-Fi.
3. Confirma negociação física a 10 Gb/s e mede o débito com equipamento capaz. Compara com a ligação anterior e com as capacidades PPPoE e de inspeção do gateway.
4. Valida IPv6 na WAN e nas LANs. Um endereço IPv6 na WAN não basta para provar que os clientes recebem um prefixo e navegam por IPv6.
5. Verifica acesso de manutenção ao ZTE. Se o plano usar uma porta separada e IP estático, testa-o agora. Não assumes que o IP do painel será automaticamente acessível através da sessão PPPoE do UniFi.
**Depois retira os serviços que já não usas.** Desliga o Wi-Fi do ZTE, incluindo as bandas e SSIDs ativos. Em firmware com MLO, poderá ser necessário desativar MLO primeiro. Desativa o DHCP local apenas depois de validares a forma de acesso de manutenção. [R3]
O ZTE deixa de fazer NAT para o serviço de Internet em bridge. O UniFi fará o NAT da LAN. Não é necessário nem apropriado tentar desligar todos os serviços internos do ZTE: a terminação da fibra e funções de gestão da operadora continuam a existir.
**Teste de persistência.** Reinicia normalmente os equipamentos numa janela adequada. Confirma que a ligação PPPoE volta, que as associações de portas persistem e que DHCP e Wi-Fi continuam no estado pretendido.
**Registo final.** Guarda os parâmetros aplicados, data, firmware, porta física e resultado de cada teste. Marca separadamente autenticação PPPoE, IPv6, desempenho, gestão e persistência. Só considera a migração concluída quando todos os elementos necessários para a tua rede estiverem confirmados.

## Repor a ligação anterior
O plano de reposição deve existir antes de apagar INTERNET. Não uses reposição de fábrica como primeira tentativa de resolver uma falha: pode perder parâmetros de serviço que não estejam documentados.
**Se PPPoE não estabelecer no UniFi.** Confirma primeiro o link físico, a porta associada em Port Binding, a VLAN 20 no ZTE, a ausência de uma segunda etiqueta no UniFi e as credenciais. Distingue ausência de resposta PPPoE de rejeição de autenticação. Não alteres vários parâmetros ao mesmo tempo.
**Reposição pelo painel.** Desliga a sessão PPPoE do UniFi. Entra no ZTE pelo acesso de manutenção previamente testado. Remove o perfil bridge e recria o perfil de encaminhamento original com os valores guardados. Se houver um backup de configuração compatível e o mecanismo de importação estiver confirmado, podes usar esse percurso em vez de reconstruir manualmente.

| Campo de referência | Valor a confirmar e repor |
| --- | --- |
| Nome | INTERNET |
| Tipo | Routing com PPPoE |
| Username e password | Credenciais guardadas |
| IP Version | IPv4 e IPv6 |
| NAT | On |
| MTU | 1492 |
| VLAN | On com ID 20 e prioridade 0 |
| Port Binding | Associações guardadas antes da mudança |
Os valores acima são uma referência para os campos principais, não uma cópia de uma configuração particular. Outros campos existentes devem ser repostos a partir do teu próprio registo; não assumes que esta tabela substitui uma cópia integral da configuração.
Volta a ativar DHCP e Wi-Fi caso tenham sido desligados e sejam necessários para a rede anterior. Confirma PPPoE, IPv4 e IPv6 ligados no estado WAN do ZTE e testa a navegação.
**Se perderes o painel.** Liga um computador à porta de manutenção e atribui um IP estático da sub-rede de gestão planeada. Confirma endereço, máscara, cabo e porta antes de considerar outras ações. Se esse acesso não tiver sido testado, evita mudanças adicionais e usa o suporte da operadora.
Para uma empresa, guarda o registo de reposição num local acessível sem Internet e não dependas exclusivamente de uma consola UniFi na nuvem durante a migração.

[R1]: https://github.com/686f6c61/DIGI-F8748
[R2]: https://github.com/yuleniwo/zxcfg
[R3]: https://bandaancha.eu/foros/configurar-modo-bridge-zte-f8748-1761099
[R4]: https://www.digi.pt/perguntas-frequentes/net
[R5]: https://help.ui.com/hc/en-us/articles/36378535649687-Configuring-IPv6-in-UniFi
[R6]: https://spdl.zyxel.com/GS1200-5/user_guide/GS1200-5_V2.00_Ed4.pdf
[R7]: https://github.com/morluto/rea
