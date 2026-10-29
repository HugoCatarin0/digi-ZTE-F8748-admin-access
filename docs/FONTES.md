# Fontes e critérios de conclusão
As fontes públicas ajudam a interpretar o modelo, mas não substituem a validação no equipamento concreto. As referências seguintes descrevem materiais técnicos de terceiros e não contêm dados de uma instalação particular.
[R1] DIGI F8748 de 686f6c61. Base macOS v0.0.4 para o diagnóstico e recuperação. A cópia incluída é uma adaptação local, não um lançamento oficial do autor.
<https://github.com/686f6c61/DIGI-F8748>
[R2] zxcfg de yuleniwo. Referência de formatos ZTE e identificação de parâmetros GPON. O descodificador do repositório implementa o percurso de análise aqui descrito.
<https://github.com/yuleniwo/zxcfg>
[R3] Tutorial de Siemdiusadeu sobre bridge no ZTE F8748. Referência pública para nome INTERNET, VLAN 20, PCP 0 e associação à LAN4. A correspondência com cada equipamento e ligação requer validação.
<https://bandaancha.eu/foros/configurar-modo-bridge-zte-f8748-1761099>
[R4] FAQ NET da DIGI Portugal. A resposta sobre router próprio exclui PRO-DIGI 10 Gbps. Verifica as condições atuais antes de aplicar a configuração.
<https://www.digi.pt/perguntas-frequentes/net>
[R5] Ubiquiti Help Center. Configuração IPv6 e delegação de prefixo no UniFi.
<https://help.ui.com/hc/en-us/articles/36378535649687-Configuring-IPv6-in-UniFi>
[R6] Zyxel GS1200. Manual com o mapeamento recomendado de PCP 0 para Best Effort e PCP 1 para Background. O tratamento efetivo depende da rede.
<https://spdl.zyxel.com/GS1200-5/user_guide/GS1200-5_V2.00_Ed4.pdf>
[R7] REA de morluto. Ferramentas de análise de artefactos e JavaScript.
<https://github.com/morluto/rea>
**Recuperação concluída.** Credencial admin guardada e login validado; PPPoE extraído de um único registo com username exato; ficheiros privados protegidos; estado do diagnóstico descrito com a incerteza que o teste realmente permite.
**Bridge concluído.** Só depois de PPPoE no UniFi, conectividade necessária, acesso de gestão e persistência confirmados. A mera presença do formulário Bridge Connection não satisfaz esse critério.
**Verificação do repositório.** A sintaxe dos scripts shell foi verificada. O descodificador offline foi verificado separadamente. Este repositório não contém os ficheiros utilizados nessa verificação nem comprova a execução dos procedimentos numa instalação identificável.
