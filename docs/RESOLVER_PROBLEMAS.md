# Resolver problemas frequentes
**Login válido mas o preflight diz que falhou.** A base original exigia curRight=1. A conta user pode ter curRight=2. A cópia incluída aceita nível 2 apenas para user e continua a exigir a validação posterior de admin.
**SSH parece fechado depois de arm.** Esse comando já terá fechado a janela. Usa dump e observa o banner durante a janela ativa. Um banner confirmado prova disponibilidade naquele momento; não prova disponibilidade após a limpeza.
**FactoryMode não devolve credencial.** Confirma as MACs LAN e do cliente, a ligação direta e o login web. Se houve reconexão, confirma a MAC privada atual. A adaptação faz uma única tentativa de ativação por execução; não contornes esse limite com ciclos externos.
**O diagnóstico recusa uma nova sessão.** Um reinício normal autorizado pode ajudar a limpar o estado do diagnóstico. Confirma depois o regresso da Internet; este passo não garante que a ativação passe a funcionar. Não confundas restart com factory reset.
**Dump termina com erro apesar de haver ficheiros.** Pode ter falhado apenas a confirmação estrita do fecho. Analisa separadamente a existência e integridade dos dados e o estado do diagnóstico. Timeout não significa encerramento confirmado.
**Configuração desencriptada incompleta.** Confirma que o último segmento hexadecimal do log foi preservado. Valida os comprimentos indicados pelos cabeçalhos e a integridade dos blocos. Não ajustes o conteúdo para atingir tamanhos retirados de outro equipamento.
**A chave não funciona.** Preserva os tags binários, confirma vid, formato tipo 6 e comprimentos big endian. O serial de fabrico apresentado no painel pode não corresponder ao material de chave necessário; preserva os identificadores GPON e as MACs. Não substituas estes elementos pelos dados do exemplo ou de outro equipamento.
**Há Password no XML mas não sabes se é PPPoE.** Agrupa os elementos DM pela mesma Row. Exige correspondência exata de Username e uma única linha com Password. Não uses regex sobre todo o XML para apanhar a primeira password.
**Não aparece Create New Item.** Confirma login admin e WAN no menu vertical. A aba WAN dentro de Status é só leitura. Type bloqueado no perfil atual não significa que o formulário novo não ofereça Bridge Connection.
**Aparece Bridge Default na tabela MAC.** É um nome de interface de comutação local. Não comprova que a ligação WAN esteja em bridge. Não apagues entradas da tabela MAC para tentar ativar esse modo.
**Bridge não dá Internet.** Revê perfil, VLAN, associação à porta e PPPoE nessa ordem. Se não houver diagnóstico claro e a janela de manutenção terminar, aplica o plano de reposição em vez de acumular alterações.

[R1]: https://github.com/686f6c61/DIGI-F8748
[R2]: https://github.com/yuleniwo/zxcfg
[R3]: https://bandaancha.eu/foros/configurar-modo-bridge-zte-f8748-1761099
[R4]: https://www.digi.pt/perguntas-frequentes/net
[R5]: https://help.ui.com/hc/en-us/articles/36378535649687-Configuring-IPv6-in-UniFi
[R6]: https://spdl.zyxel.com/GS1200-5/user_guide/GS1200-5_V2.00_Ed4.pdf
[R7]: https://github.com/morluto/rea
