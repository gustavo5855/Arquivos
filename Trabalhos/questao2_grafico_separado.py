# -*- coding: utf-8 -*-

from threading import Thread, Semaphore
from multiprocessing import Queue, Manager
import time, os
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# filho T1 é responsável por ler os pacotes da placa de rede, examinar quantos bytes
# tem o pacote e se o protocolo é TCP, UDP ou SMTP, e colocar as duas informações no buffer B12
#
# T2 é responsável por ler o buffer B12 e calcular o número, o tamanho médio e a variância dos
# pacotes UDP, TCP e SMTP a cada 30 s e colocar estas seis informações no buffer B23
#
# 3 é responsável por ler o buffer B23 e mostrar e atualizar a cada 30 s uma figura na tela
# com seis gráficos, mostrando a evolução de cada uma destas seis variáveis

b12 = deque(maxlen=100)  # vetor de string de 20 posicoes
b23 = deque(maxlen=100)  # vetor de inteiros de 9 posicoes


def T1(buffer, semaphore1):
    i = 0
    while True:

        package = os.popen("sudo tcpdump -i any -c 1 -v|grep proto").read()
        print(package)
        if package != "":
            pacote = package[package.index("proto"):].split(" ")[1] + " " + package[package.index("proto"):].split(" ")[
                                                                                4][:-2]
            print(pacote)
            if ("TCP" in pacote) or ("UDP" in pacote) or ("IGMP" in pacote):
                semaphore1.acquire()
                buffer.append(pacote)
                semaphore1.release()
                i += 1

        print(i)


def T2(buffer1_2, buffer2_3, semaphore1, semaphore2):
    tcp = []
    udp = []
    igmp = []
    i = 0

    def media(lista, nome):
        if len(lista) > 0:
            return sum(lista) / len(lista)
        else:
            return 0

    def variancia(lista, nome):
        med = media(lista, nome)
        soma = 0
        variancia = 0
        if len(lista) > 0:
            for valor in lista:
                soma += pow((valor - med), 2)
            variancia = soma / float(len(lista))
            return variancia
        return 0

    while True:

        time.sleep(5)

        while len(buffer2_3) != 0:  # esvazia o buffer
            semaphore2.acquire()
            buffer2_3.popleft()
            semaphore2.release()

        teste = []

        while len(buffer1_2) != 0:
            semaphore1.acquire()
            teste.append(buffer1_2.popleft())  # passa os elementos do buffer para a lista
            semaphore1.release()

        for i in teste:  # usa a lista para verificar os pacotes

            print(i)

            if "TCP" in i:
                print("Package Received: TCP")
                tcp.append(sum([int(x) for x in i.split(" ")[1:]]))

            if "UDP" in i:
                print("Package Received: UDP")
                udp.append(sum([int(x) for x in i.split(" ")[1:]]))

            if "IGMP" in i:
                print("Package Received: IGMP")
                igmp.append(sum([int(x) for x in i.split(" ")[1:]]))

        print("============================================")
        print("PACOTES TCP:", tcp)
        print("PACOTES UDP:", udp)
        print("PACOTE IGMP:", igmp)
        print("media TCP:", media(tcp, "TCP"))
        print("variancia TCP:", variancia(tcp, "TCP"))
        print("media UDP:", media(udp, "UDP"))
        print("variancia UDP:", variancia(udp, "UDP"))
        print("media IGMP:", media(igmp, "IGMP"))
        print("variancia IGMP:", variancia(igmp, "IGMP"))
        print("============================================")

        semaphore2.acquire()
        buffer2_3.append(int(len(tcp)))
        buffer2_3.append(int(media(tcp, "TCP")))
        buffer2_3.append(int(variancia(tcp, "TCP")))

        buffer2_3.append(int(len(udp)))
        buffer2_3.append(int(media(udp, "UDP")))
        buffer2_3.append(int(variancia(udp, "UDP")))

        buffer2_3.append(int(len(igmp)))
        buffer2_3.append(int(media(igmp, "IGMP")))
        buffer2_3.append(int(variancia(igmp, "IGMP")))
        semaphore2.release()

        print("BUFER23: ", buffer2_3)

        tcp.clear()
        udp.clear()
        igmp.clear()


def T3(buffer2_3, semaphore2):
    fig = plt.figure()  # tela onde joga o grafico
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)

    # legends= ["num. pacote TCP", "media pacote TCP", "variancia pacote TCP",              so pra saber a ordem como estao dispostos os valoers de b23
    #           "num. pacote UDP", "media pacote UDP", "variancia pacote UDP",
    #           "num. pacote IGMP", "media pacote IGMP", "variancia pacote IGMP"]

    time.sleep(5)

    y1 = [[0], [0], [0]]  # valores do eixo y1
    x1 = [[0], [0], [0]]  # valores do eixo x1
    y2 = [[0], [0], [0]]
    y3 = [[0], [0], [0]]

    def animate(i):  # i é padrao

        teste = []  # vetor que sera uado para substiruir b23

        print("BUFFER23:", buffer2_3)
        while len(buffer2_3) != 0:  # coloca os elementos do buffer num array
            semaphore2.acquire()  # exclusao mutua
            teste.append(str(buffer2_3.popleft()))
            semaphore2.release()
        print(teste, len(teste))

        num = [teste[0], teste[3], teste[6]]
        media = [teste[1], teste[4], teste[7]]
        variancia = [teste[2], teste[5], teste[8]]

        print(teste)
        print(num)
        print(media)
        print(variancia)

        if len(teste) != 0:  # testa se o array n está vazio

            for i in range(3):
                print("Tamanho x: ", len(x1[i]))
                print("Tamanho y: ", len(y1[i]))
                print("Tamanho buffer: ", len(teste))
                x1[i].append(len(x1[i]))
                y1[i].append(num[i])
                y2[i].append(media[i])
                y3[i].append(variancia[i])

        ax1.clear()
        ax2.clear()
        ax3.clear()

        for j in range(3):
            ax1.plot(x1[j], y1[j], marker="s")
            ax2.plot(x1[j], y2[j], marker="s")
            ax3.plot(x1[j], y3[j], marker="s")

        ax1.legend(["num tcp", "num udp", "num igmp"], loc="upper right")
        ax1.set_xlabel("iteração")
        ax1.set_ylabel("Quantidade")

        ax2.legend(["media tcp", "media udp", "media igmp"], loc="upper right")
        ax2.set_xlabel("iteração")
        ax2.set_ylabel("Quantidade")

        ax3.legend(["var tcp", "var udp", "var igmp"], loc="upper right")
        ax3.set_xlabel("iteração")
        ax3.set_ylabel("Quantidade")

    plt.axis([0, 10, 0, 10])
    plt.tight_layout()
    anim = animation.FuncAnimation(fig, animate, interval=5000)
    plt.show()


def main():
    smf = Semaphore()
    smf2 = Semaphore()

    t1 = Thread(target=T1, args=(b12, smf))
    t2 = Thread(target=T2, args=(b12, b23, smf, smf2))
    t3 = Thread(target=T3, args=(b23, smf2,))

    t1.start()
    t2.start()
    t3.start()


if __name__ == '__main__':
    main()
