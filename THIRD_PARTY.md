# Proveniência

## Base do diagnóstico

`scripts/recuperar-admin-f8748.sh` deriva de `DIGI-F8748-macos/digi-f8748.sh`, versão declarada 0.0.4, do projeto [686f6c61/DIGI-F8748](https://github.com/686f6c61/DIGI-F8748). Mantém a atribuição no cabeçalho. É uma adaptação local, não um lançamento oficial desse autor.

Adaptações incluídas:

- Preflight aceita `user` com `curRight=2`; admin continua a exigir validação posterior.
- Uma tentativa de ativação por execução; verificação do banner SSH durante a janela ativa.
- Contadores locais no encerramento e tentativa de limpeza após resposta incompleta.
- `umask 077`, recusa de saída em Git antes de ativar diagnóstico e omissão das credenciais SSH temporárias e da chave de sessão nos logs normais de ativação.
- A função `info` deixa de reutilizar a variável da pasta temporária para o título do painel.
- Temporário `digi_oss.bin` isolado na pasta temporária da execução, com remoção entre candidatos.
- Leitura big endian do comprimento do contentor oss no caminho legado `decrypt`.

A ferramenta base ainda contém comandos avançados e o comando legado `decrypt`, que pode imprimir credenciais. O percurso recomendado neste repositório é `dump` seguido de `f8748_offline.py`, sem `--keep-ssh`, sem `recover` e sem secrets nos argumentos.

## Coletor PPPoE

`scripts/preparar_coletor.py` deriva deterministicamente `scripts/recolher-pppoe-f8748.sh` da base incluída: lê boardtype e paramtag, recolhe a configuração cifrada e preserva as janelas de flash. Não importa dados do equipamento para o código-fonte.

## Descodificação e referências

`scripts/f8748_offline.py` implementa o percurso local documentado em [FORMATOS.md](docs/FORMATOS.md). A identificação dos formatos e parâmetros foi apoiada pelo código público [yuleniwo/zxcfg](https://github.com/yuleniwo/zxcfg). Não é um descodificador universal de firmwares ZTE.

Os testes criam fixtures sintéticas em memória e numa pasta temporária; não são cópias de dados de clientes.

## Licenças e atribuição

Este repositório não atribui uma nova licença global ao código de terceiros. Conserva as atribuições e consulta as condições nos projetos de origem antes de redistribuir ou relicenciar. Não se presume que a ausência de um ficheiro de licença permita relicenciamento.
