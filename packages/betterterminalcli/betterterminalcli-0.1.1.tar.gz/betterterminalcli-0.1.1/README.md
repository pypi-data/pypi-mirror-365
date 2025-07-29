# Better Terminal #

Uma biblioteca Python para criar interfaces dinâmicas e interativas no terminal de forma simples e eficiente. Utiliza threading para facilitar a mudança em tempo real e de forma inteligente o terminal.

---

## Recursos principais ##

### Terminal ###

- ScreenBuffer - Controle total de renderização no terminal.
- TerminalApp - Gerenciador principal da aplicação no terminal.

### Widgets ###

- BaseWidget - Classe base para criar componentes personalizados.
- TextWidget - Exibição e manipulação de texto. (One-Liner)

---

## Instalação ##

```bash
pip install betterterminal
```

Ou instale localmente.

## Exemplo Básico de Uso ##

```python
from betterterminalcli.core.terminal_app import TerminalApp
from betterterminalcli.widgets.text_widget import TextWidget
import time

app = TerminalApp()
text = TextWidget("Hello, Better Terminal!", x=5, y=5)
app.add_widget(text)
app.start()

time.sleep(3)
text.change_text("I changed my text!")
time.sleep(3)

app.stop()
```

## Planos Futuros ##

Em ordem, as futuras atualizações devem conter:

- Adição de widgets mais complexos (barras de progresso, tabelas, menus interativos).
- Sistema de eventos e callbacks para widgets.
- Suporte estendido para diferentes terminais e cores.
- Sistema de suporte para animações

## Licença ##

MIT License © 2025 Mauricio Reisdoefer
