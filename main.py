import pygame
import random
import os
from collections import deque
from telemetrix import telemetrix
from dotenv import load_dotenv

# =========================
# ARDUINO
# =========================
load_dotenv()

board = telemetrix.Telemetrix(
    com_port=os.getenv("BOARD")
)


# estados dos botões
estado_esq = 0
estado_dir = 0


# =========================
# CALLBACKS
# =========================

def callback_esq(data):

    global estado_esq

    estado_esq = data[2]


def callback_dir(data):

    global estado_dir

    estado_dir = data[2]


# configura botões
board.set_pin_mode_digital_input(
    int(os.getenv("DEVICE_1")),
    callback=callback_esq
)

board.set_pin_mode_digital_input(
    int(os.getenv("DEVICE_2")),
    callback=callback_dir
)

# =========================
# PYGAME
# =========================

pygame.init()

LARGURA = 600
ALTURA = 600
BLOCO = 20

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)

tela = pygame.display.set_mode(
    (LARGURA, ALTURA)
)

pygame.display.set_caption(
    "Snake Arduino"
)

clock = pygame.time.Clock()

fonte = pygame.font.SysFont(
    "Arial",
    30
)

# =========================
# COBRA
# =========================

cobra = deque([
    [100, 100]
])

direcao = "RIGHT"

# comida
comida = [
    random.randrange(
        0,
        LARGURA,
        BLOCO
    ),

    random.randrange(
        0,
        ALTURA,
        BLOCO
    )
]

pontos = 0
rodando = True

ultimo_esq = 0
ultimo_dir = 0

ultimo_movimento = pygame.time.get_ticks()

intervalo = 120

# =========================
# FUNÇÕES
# =========================

def virar_esquerda(dir_atual):

    ordem = [
        "UP",
        "LEFT",
        "DOWN",
        "RIGHT"
    ]

    idx = ordem.index(dir_atual)

    return ordem[
        (idx + 1) % 4
    ]


def virar_direita(dir_atual):

    ordem = [
        "UP",
        "RIGHT",
        "DOWN",
        "LEFT"
    ]

    idx = ordem.index(dir_atual)

    return ordem[
        (idx + 1) % 4
    ]


def desenhar_grade():

    cor_grade = (40, 40, 40)

    # linhas verticais
    for x in range(
        0,
        LARGURA,
        BLOCO
    ):

        pygame.draw.line(
            tela,
            cor_grade,
            (x, 0),
            (x, ALTURA)
        )

    # linhas horizontais
    for y in range(
        0,
        ALTURA,
        BLOCO
    ):

        pygame.draw.line(
            tela,
            cor_grade,
            (0, y),
            (LARGURA, y)
        )


# =========================
# LOOP PRINCIPAL
# =========================

while rodando:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            rodando = False

    # =========================
    # BOTÕES
    # =========================

    # esquerda
    if estado_esq == 1 and ultimo_esq == 0:
        direcao = virar_esquerda(
            direcao
        )

    # direita
    if estado_dir == 1 and ultimo_dir == 0:
        direcao = virar_direita(
            direcao
        )

    ultimo_esq = estado_esq
    ultimo_dir = estado_dir

    # =========================
    # MOVIMENTO
    # =========================

    agora = pygame.time.get_ticks()

    if (
        agora - ultimo_movimento
        > intervalo
    ):

        ultimo_movimento = agora

        x, y = cobra[0]

        if direcao == "UP":
            y -= BLOCO

        elif direcao == "DOWN":
            y += BLOCO

        elif direcao == "LEFT":
            x -= BLOCO

        elif direcao == "RIGHT":
            x += BLOCO

        nova = [x, y]

        # colisão parede
        if (
            x < 0 or
            x >= LARGURA or
            y < 0 or
            y >= ALTURA
        ):

            rodando = False

        # colisão corpo
        elif nova in cobra:

            rodando = False

        else:

            cobra.appendleft(nova)

            # comida
            if nova == comida:

                pontos += 1

                comida = [

                    random.randrange(
                        0,
                        LARGURA,
                        BLOCO
                    ),

                    random.randrange(
                        0,
                        ALTURA,
                        BLOCO
                    )
                ]

            else:
                cobra.pop()

    # =========================
    # DESENHO
    # =========================

    tela.fill(PRETO)

    desenhar_grade()

    # comida
    pygame.draw.rect(
        tela,
        VERMELHO,
        (
            comida[0],
            comida[1],
            BLOCO,
            BLOCO
        )
    )

    # =========================
    # COBRA
    # =========================

    for i, parte in enumerate(cobra):

        x = parte[0]
        y = parte[1]

        # cabeça
        if i == 0:

            pygame.draw.rect(
                tela,
                (0, 200, 0),
                (
                    x,
                    y,
                    BLOCO,
                    BLOCO
                )
            )

            # olhos
            olho1 = (x + 5, y + 5)
            olho2 = (x + 15, y + 5)

            if direcao == "UP":

                olho1 = (x + 5, y + 5)
                olho2 = (x + 15, y + 5)

            elif direcao == "DOWN":

                olho1 = (x + 5, y + 15)
                olho2 = (x + 15, y + 15)

            elif direcao == "LEFT":

                olho1 = (x + 5, y + 5)
                olho2 = (x + 5, y + 15)

            elif direcao == "RIGHT":

                olho1 = (x + 15, y + 5)
                olho2 = (x + 15, y + 15)

            pygame.draw.circle(
                tela,
                BRANCO,
                olho1,
                2
            )

            pygame.draw.circle(
                tela,
                BRANCO,
                olho2,
                2
            )

        # corpo
        else:

            pygame.draw.rect(
                tela,
                (0, 255, 0),
                (
                    x,
                    y,
                    BLOCO,
                    BLOCO
                )
            )

    # pontuação
    texto = fonte.render(
        f"Pontos: {pontos}",
        True,
        BRANCO
    )

    tela.blit(
        texto,
        (10, 10)
    )

    pygame.display.update()

    clock.tick(60)

# =========================
# GAME OVER
# =========================

tela.fill(PRETO)

fim = fonte.render(
    "GAME OVER",
    True,
    VERMELHO
)

pts = fonte.render(
    f"Pontos: {pontos}",
    True,
    BRANCO
)

tela.blit(
    fim,
    (180, 250)
)

tela.blit(
    pts,
    (220, 300)
)

pygame.display.update()

pygame.time.delay(3000)

pygame.quit()

board.shutdown()