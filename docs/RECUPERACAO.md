# Preparar a ligação e as dependências
1. Liga o Mac diretamente a uma porta LAN do ZTE ou ao Wi-Fi do próprio ZTE. Evita rede de convidados, VPN, repetidores ou outro router entre o computador e o equipamento durante a recuperação.
2. Confirma que o painel abre em http://192.168.1.1/ e que tens um login web válido. A conta user pode ter privilégios limitados. Usa apenas as credenciais válidas do equipamento a administrar.
3. Reserva uma janela para acompanhar o processo. Um reinício normal pode ser necessário se o diagnóstico ficar preso; interrompe a Internet e exige concordância de quem depende da ligação.
4. Clona este repositório, verifica-o e muda depois para uma pasta privada fora de Git, como explicado no README. Nos comandos seguintes, a pasta scripts contém as ferramentas copiadas desse checkout.

```bash
command -v bash curl openssl xxd ssh ssh-keyscan expect python3
umask 077
mkdir -p dados-admin dados-pppoe
chmod 700 dados-admin dados-pppoe scripts
chmod 700 scripts/*.sh
bash -n scripts/recuperar-admin-f8748.sh
bash -n scripts/recolher-pppoe-f8748.sh

```
Se faltar uma dependência, resolve-a antes de ativar o diagnóstico. Os scripts Python usam apenas a biblioteca padrão e o executável openssl. Os comandos destinam-se a macOS; não se presume compatibilidade com Windows.
**Identifica as duas MACs corretas.** A primeira é a MAC LAN ou br0 do ZTE; a segunda é a MAC da interface que o Mac usa para chegar ao ZTE. Não uses uma MAC de WAN diferente nem a de outro adaptador.

```bash
ping -c 1 192.168.1.1
arp -n 192.168.1.1
route -n get 192.168.1.1

```
Consulta a interface indicada por route com ifconfig, por exemplo ifconfig en0. O macOS pode apresentar octetos sem zeros iniciais no ARP. Normaliza a MAC para seis pares hexadecimais, como AA:BB:CC:DD:EE:FF. A MAC privada do Wi-Fi pode mudar depois de uma reconexão; volta a confirmar após reiniciar.
**Preparação de dados.** Guarda os ficheiros fora de Git e de pastas partilhadas. Os logs de sessões e os ficheiros recolhidos continuam a ser sensíveis, mesmo com a omissão de chaves e credenciais temporárias nas mensagens normais de ativação. O XML desencriptado pode conter outras credenciais além da PPPoE.

## Recuperar os dados de administrador
A ferramenta base usa o diagnóstico de fábrica para obter uma sessão SSH temporária. A credencial dessa sessão é diferente da conta admin do painel. A recuperação lê paramtag e janelas de flash e depois trabalha localmente. [R1]
1. A partir da pasta privada de trabalho, executa o comando abaixo. Substitui as duas MACs pelos valores confirmados na secção de preparação.

```bash
bash scripts/recuperar-admin-f8748.sh dump \
  --host 192.168.1.1 \
  --router-mac AA:BB:CC:DD:EE:FF \
  --client-mac 11:22:33:44:55:66 \
  --out ./dados-admin

```
2. Responde à confirmação de autorização e introduz o login web nos pedidos interativos. Não coloques a password em --web-pass, em prompts públicos ou no histórico da shell.
3. Acompanha as mensagens. O script deve confirmar o login web, obter a credencial temporária e verificar um banner SSH durante a janela ativa. Regista apenas se o banner começa por SSH-, sem divulgar os detalhes da sessão.
4. Aguarda a recolha. Não inicies outra ativação em paralelo nem interrompas apenas por a leitura demorar. O diagnóstico aceita um conjunto limitado de comandos; os blocos de 8192 bytes foram importantes para a extração.
5. Verifica os ficheiros locais mesmo que o script termine com erro na etapa de fecho.

```bash
ls -lh dados-admin

```
**Ficheiros esperados.** paramtag.bin, boardtype.txt, hardcode.seed e oss.bin. Confirma a integridade de cada ficheiro e consulta o identificador vid em boardtype.txt. Não uses tamanhos de outra unidade como critério de sucesso.
**Não executes arm antes de dump.** O comando arm abre e fecha a janela por omissão. Testar a porta 22 só depois de arm terminar não verifica a janela ativa. O comando dump já verifica a disponibilidade durante a janela correta.
**Estado de saída.** Um erro no encerramento não invalida automaticamente os ficheiros recolhidos. Distingue recolha concluída, desencriptação concluída e diagnóstico encerrado: são três verificações diferentes.

## Guardar admin e verificar o encerramento
**Guardar sem imprimir a password.** O descodificador incluído lê os tags de paramtag e grava um JSON privado. Usa o vid indicado em boardtype.txt; 108 nos comandos é um exemplo técnico que deve ser confirmado localmente.

```bash
python3 scripts/f8748_offline.py admin \
  --dir dados-admin --vid 108 \
  --credentials credenciais-router.json
chmod 600 credenciais-router.json

```
O tag 0x702 fornece a password. Se 0x602 não existir, o script usa admin como candidato de username; esse nome precisa de validação no painel. Confirma sempre o username com o catálogo disponível e com um login efetivo.
**Validar no painel.** Abre o JSON num editor local privado. Termina a sessão user e entra em http://192.168.1.1/ com a credencial recuperada. Confirma a conta admin e o acesso a Internet → WAN no menu vertical. Uma sessão administrativa pode ser identificada no código do painel por curRight=1. Não alteres a WAN nesta fase.
Se os tags forem insuficientes, a base também oferece decrypt --dir dados-admin, usando seed e oss. Esse comando imprime segredos no Terminal. Não guardes a sua saída num relatório partilhado; não confundas uma credencial candidata com um login verificado.
**Verificar o diagnóstico.** A base tenta FactoryMode.gch?close e exige recusa TCP explícita para considerar o fecho confirmado. Não trates mode=0 como equivalente a close sem confirmação para o firmware em uso.

```bash
nc -vz -G 3 192.168.1.1 22

```

| Resultado | Interpretação |
| --- | --- |
| Ligação aceite ou banner SSH | Serviço ainda acessível |
| Connection refused | Porta explicitamente recusada nesse teste |
| Timeout | Sem resposta; não prova que o serviço foi desligado |
Se SSH responder durante a janela e passar a timeout após close, o script pode devolver erro por não confirmar recusa explícita. Não declares o serviço definitivamente encerrado com base nesse timeout.
Se o estado continuar incerto, faz um reinício normal numa janela autorizada e repete a verificação. Não uses Reset nem reposição de fábrica. Confirma também que o painel voltou e que PPPoE, IPv4 e IPv6 estão ligados.

## Recolher a configuração para PPPoE
O painel e a API podem devolver valores mascarados ou placeholders e omitir o campo Password. Não uses asteriscos, tabs nem o texto redacted como credencial.
O percurso descrito lê /userconfig/cfg/db_user_cfg.xml, ainda cifrado, e obtém os elementos necessários a partir do próprio equipamento. O coletor não depende de consultas diretas a WANCPPP nem de acesso direto a /etc/hardcodefile/dataprotocol, que podem ser recusados.
1. Confirma que já guardaste admin. Resolve o estado do diagnóstico anterior antes de abrir uma nova sessão. Se o firmware recusar a ativação, não encadeies tentativas; confirma ligação e MACs e considera um reinício normal autorizado.
2. Revê ou regenera o coletor. Esta etapa é exclusivamente local.

```bash
python3 scripts/preparar_coletor.py
bash -n scripts/recolher-pppoe-f8748.sh

```
3. Executa a recolha com as MACs atuais. Introduz interativamente um login web válido. A variante aceita o mesmo preflight da base.

```bash
bash scripts/recolher-pppoe-f8748.sh dump \
  --host 192.168.1.1 \
  --router-mac AA:BB:CC:DD:EE:FF \
  --client-mac 11:22:33:44:55:66 \
  --out ./dados-pppoe

```
O coletor lê boardtype e paramtag, guarda o hexdump da configuração em ppp-config-session.log e preserva flash-windows.bin quando encontra seed e oss. São janelas concatenadas, não uma imagem integral nem uma cópia restaurável de firmware.
4. Confirma a existência de paramtag.bin, hardcode.seed, flash-windows.bin e ppp-config-session.log. Faz novamente a verificação de encerramento da secção Guardar admin e verificar o encerramento, mesmo que a recolha pareça bem-sucedida.
**Limite conhecido.** As janelas e caminhos são específicos do layout suportado pelo script; /dev/mtd9 é um dos candidatos previstos. Não substituas automaticamente por offsets aleatórios ou comandos de gravação se outra unidade tiver layout diferente. Conserva os erros para análise e interrompe essa expansão.

## Desencriptar PPPoE e guardar as credenciais
Os passos desta secção são offline. Depois de recolhidos os ficheiros, não precisam de SSH nem de voltar a abrir o diagnóstico.
1. Reconstrói o binário da configuração a partir do log. O parser aceita também a última linha parcial do hexdump e remove espaços finais. Ignorá-la pode produzir um ficheiro truncado.

```bash
python3 scripts/f8748_offline.py log \
  --input dados-pppoe/ppp-config-session.log \
  --output dados-pppoe/db_user_cfg.xml

```
2. Desencripta e seleciona o registo pelo username PPPoE conhecido. Substitui CONTA@operadora pela conta da tua ligação, consultável no perfil INTERNET. Não inventes nem derives a password a partir do username.

```bash
python3 scripts/f8748_offline.py pppoe \
  --dir dados-pppoe --vid 108 \
  --username 'CONTA@operadora' \
  --credentials credenciais-router.json

```
3. O script extrai catálogos, deriva candidatos limitados a identificadores do equipamento, valida os contentores e o XML e exige exatamente um registo com esse Username e uma Password não vazia. Acrescenta pppoe ao JSON sem eliminar os campos admin existentes.
4. Confirma as permissões e abre o JSON apenas num editor local privado.

```bash
chmod 600 credenciais-router.json
ls -l credenciais-router.json

```
**Formato de saída esperado.** Os valores abaixo são exemplos de campos, não credenciais utilizáveis.

```json
{
  "username": "admin",
  "password": "VALOR_RECUPERADO",
  "pppoe": {
    "username": "CONTA@operadora",
    "password": "VALOR_RECUPERADO"
  }
}

```
O programa também guarda plain-config.xml e hardcode-catalogues.json na pasta de dados. Trata-os como segredos. O sucesso da extração prova que os dois campos vieram do mesmo registo PPP; a confirmação de autenticação só acontece quando o UniFi estabelece efetivamente uma nova sessão PPPoE.

[R1]: https://github.com/686f6c61/DIGI-F8748
[R2]: https://github.com/yuleniwo/zxcfg
[R3]: https://bandaancha.eu/foros/configurar-modo-bridge-zte-f8748-1761099
[R4]: https://www.digi.pt/perguntas-frequentes/net
[R5]: https://help.ui.com/hc/en-us/articles/36378535649687-Configuring-IPv6-in-UniFi
[R6]: https://spdl.zyxel.com/GS1200-5/user_guide/GS1200-5_V2.00_Ed4.pdf
[R7]: https://github.com/morluto/rea
