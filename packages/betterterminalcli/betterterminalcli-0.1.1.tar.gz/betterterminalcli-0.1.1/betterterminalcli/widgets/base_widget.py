from typing import Optional
from betterterminalcli import ScreenBuffer

class BaseWidget():
    """
    Widget base para a biblioteca BetterTerminalCLI.
    Cada widget deve saber sua posição e implementar renderização.
    """

    def __init__(self, name:str="No Name", x: int = 0, y: int = 0, width: Optional[int] = None, height: Optional[int] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.name = name

    def render(self, buffer: ScreenBuffer):
        """
        Renderiza o widget no buffer.
        Deve ser implementado pelas subclasses.
        """
        raise NotImplementedError("Subclasses devem implementar o método render")

    def move(self, x: int, y: int):
        """Move o widget para nova posição."""
        self.x = x
        self.y = y

    def resize(self, width: int, height: int):
        """Redimensiona o widget."""
        self.width = width
        self.height = height
        
    def update(self, dt:float) -> bool:
        """
        Faz a atualização do widget.
        
        args:
            dt (float) = DeltaTime (Tempo passado da última atualização)
        """
        raise NotImplementedError("Subclasses devem ou substituir com 'return false' ou com um método")