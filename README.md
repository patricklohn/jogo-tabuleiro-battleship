# Batalha Naval Multiplayer (LAN)

Este projeto é uma versão em rede local (LAN) do clássico Batalha Naval, desenvolvida por alunos da Unisul:

* Erick Vieira
* Patrick Lohn
* Rafael Sonoki
* Ruan Oliveira

Baseado nos exemplos de Al Sweigart no livro **Making Games with Python & Pygame**:
[http://inventwithpython.com/pygame/chapters/](http://inventwithpython.com/pygame/chapters/)

---

## 🎯 Objetivo

Duelo de Batalha Naval para dois jogadores em computadores diferentes via LAN. Um servidor coordena o jogo e dois clientes Pygame realizam as jogadas, exibindo gráficos idênticos para cada participante.

---

## 🚀 Pré‑requisitos

* **Python 3.8+** instalado no sistema.
* Módulo **pygame** para interface gráfica.

### Instalação de dependências

```bash
pip install pygame
```

---

## 📂 Estrutura do Projeto

```
Battleship-LAN/
├── game_logic.py     # Lógica de tabuleiro: geração, posicionamento, checagem
├── server.py         # Servidor TCP que coordena partidas entre dois clientes
├── client.py         # Cliente Pygame que conecta ao servidor e desenha o jogo
├── img/              # Imagens de explosão (blowup1.png ... blowup6.png)
├── sound/            # Efeitos sonoros (pew.wav, boom.wav) e música de fundo
└── README.md         # Este arquivo de instruções atualizadas
```

---

## ▶ Como Executar

1. **Servidor** (máquina host):

   ```bash
   cd /caminho/para/Battleship-LAN
   python server.py
   ```

   O servidor aguardará duas conexões na porta **5000** e exibirá mensagens de status.

2. **Clientes** (ambos os jogadores):

   ```bash
   cd /caminho/para/Battleship-LAN
   python client.py <IP_do_servidor>
   ```

   * Substitua `<IP_do_servidor>` pelo endereço IP da máquina onde o servidor está rodando.
   * Cada cliente abrirá a interface gráfica do jogo e esperará sua vez.

3. **Jogar**:

   * Clique em uma célula do tabuleiro adversário para atirar.
   * Aguarde o resultado (acerto, afundou ou erro) e o turno do próximo jogador.
   * Quando todos os navios de um jogador forem afundados, a partida termina.

---

## 🎮 Controles

* **Mouse**: apontar e clicar para disparar em uma célula.
* **Teclado**:

  * `S` para ligar/desligar efeitos sonoros.
  * `M` para ligar/desligar música de fundo.
  * Qualquer tecla para fechar telas de ajuda ou fim de jogo.

---

## 📚 Referências & Tutoriais

* Biblioteca oficial Pygame: [https://www.pygame.org/](https://www.pygame.org/)
* Tutoriais Pygame: [https://www.pygame.org/wiki/tutorials](https://www.pygame.org/wiki/tutorials)
* Invent with Python (Al Sweigart): [http://inventwithpython.com/pygame/chapters/](http://inventwithpython.com/pygame/chapters/)

---

## 🤝 Colaboração

Este projeto é open‑source e está sendo gerenciado com **Git**. Sinta‑se à vontade para clonar, estudar o código e propor melhorias via pull request.

---

**Bom jogo em LAN** e que vença o melhor estrategista! 🎉
