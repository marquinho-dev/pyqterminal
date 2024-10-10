# PyQTerminal

**PyQTerminal** é um emulador de terminal simples desenvolvido com PyQt5, permitindo ao usuário executar comandos, ajustar a opacidade do terminal, personalizar a fonte e a cor do texto, e exibir o diretório atual de forma estilizada, tudo isso dentro de uma interface gráfica moderna e transparente.

## Características

- **Emulador de Terminal**: Executa comandos Bash e exibe os resultados diretamente na interface gráfica.
- **Opacidade Ajustável**: Controle deslizante para alterar a opacidade da área de saída, permitindo um fundo transparente.
- **Personalização de Fonte**: Alteração do tipo de fonte e cor do texto através de um menu interativo.
- **Suporte a Comandos `sudo`**: O terminal suporta comandos `sudo`, solicitando a senha quando necessário.
- **Exibição de Diretório Atual**: O diretório atual é exibido no topo do terminal, com formatação semelhante ao estilo Powerlevel10k.

## Instalação

Para executar o **PyQTerminal**, é necessário que você tenha o Python 3 e as dependências listadas abaixo instaladas:

### Dependências

- **Python 3.x**
- **PyQt5**: Interface gráfica para o Python.

Você pode instalar as dependências usando `pip`:

```bash
pip install PyQt5
