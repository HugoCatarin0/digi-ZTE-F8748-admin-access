# Detalhes técnicos para reproduzir a análise
Esta secção permite a outro LLM compreender os formatos e verificar o código incluído sem depender de uma ferramenta universal. Os algoritmos implementam os formatos ZTE suportados e devem ser confrontados com os dados do equipamento. [R1, R2]
**Paramtag.** O ficheiro começa por TAGH. A análise inicia os registos no offset 20, com cabeçalho <HHHHH em little endian. Registos cifrados observados usam f6=0 e f8=1. A chave AES de 256 bits é SHA256 dos primeiros 32 caracteres de zx279132 + vid + 8cc72b05705d5c46f412af8cbed55aad. O IV são os primeiros 16 bytes desse digest. Após AES CBC, remove-se padding válido e NUL; os valores observados contêm texto hexadecimal a converter novamente em bytes.
É essencial preservar valores binários: as MACs dos tags 0x100 a 0x104 e 0x300 não devem desaparecer por falharem uma conversão UTF-8. O tag 0x702 é usado para a password admin; 0x602 pode não existir.
**Catálogos hardcode.** Nas janelas de flash procuram-se fluxos zlib cujo resultado começa por 01 02 03 04. O comprimento cifrado no offset 64 destes contentores é big endian; o corpo começa no offset 72. Ler esse comprimento como little endian foi uma incorreção identificada no script de base.
A seed fornece o material de chave: soma-se 2 aos bytes dos caracteres 47:63, acrescenta-se seed[64:] e limita-se a 32 bytes antes de SHA256. O IV é derivado por SHA256 dos caracteres 2:34 com soma 3 por byte, usando os primeiros 16 bytes. O resultado AES CBC contém pares KEY=VALUE, incluindo parâmetros de dataprotocol.
**Configuração tipo 6.** O cabeçalho observado começa por 0102030400000006. No offset 60 existem três inteiros big endian com o comprimento em claro, comprimento cifrado e indicador de continuação. O corpo cifrado começa no offset 72.
A derivação implementada usa identificadores GPON e MAC do próprio equipamento. O descodificador testa apenas as combinações documentadas de serials dos tags 0x200, 0x880, 0x881 e 0x883 e MACs binárias locais, incluindo ordem invertida. A chave é SHA256 do material serial + MAC em hexadecimal; o IV deriva do catálogo ou da constante ZTE%FN$GponNJ025. Não é uma pesquisa de passwords de terceiros.
**Camada interior.** Após AES surge um contentor tipo 0. A partir do offset 60, blocos >III descrevem tamanho descomprimido, comprimido e continuação. Cada bloco zlib é validado, o XML final é analisado e os campos DM name e val são agrupados por Row. Não se escolhe uma Password apenas por aparecer perto do username num texto bruto.

[R1]: https://github.com/686f6c61/DIGI-F8748
[R2]: https://github.com/yuleniwo/zxcfg
[R3]: https://bandaancha.eu/foros/configurar-modo-bridge-zte-f8748-1761099
[R4]: https://www.digi.pt/perguntas-frequentes/net
[R5]: https://help.ui.com/hc/en-us/articles/36378535649687-Configuring-IPv6-in-UniFi
[R6]: https://spdl.zyxel.com/GS1200-5/user_guide/GS1200-5_V2.00_Ed4.pdf
[R7]: https://github.com/morluto/rea
