#!/usr/local/bin/python3

import ast
import datetime
import os
import signal
import string
import subprocess
import threading
import time
import socket
import sys
from platform import platform
from threading import Thread

import psutil
import serial
import spidev
import smbus
import time
import vcgencmd

########################################################################################################################
from gpiozero.pins import data

"""
    Функция вывода текущего времени.
"""
def current_time():
    try:
        return time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as be:
        print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
        print("\033[30m {}".format(""))
        return -1
########################################################################################################################
# """
#     Для форматированного вывода текста на консоль
# """
# class color:
#    PURPLE = '\033[95m'
#    CYAN = '\033[96m'
#    DARKCYAN = '\033[36m'
#    BLUE = '\033[94m'
#    GREEN = '\033[92m'
#    YELLOW = '\033[93m'
#    RED = '\033[91m'
#    BOLD = '\033[1m'
#    UNDERLINE = '\033[4m'
#    END = '\033[0m'

def setTerm(loop_counter):
    try:
        if loop_counter % 2 == 0:
            os.system("setterm -back yellow")
            os.system("setterm -fore black")

        else:
            os.system("setterm -back green")
            os.system("setterm -fore black")
    except Exception as be:
        print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
        print("\033[30m {}".format(""))
        return -1
#print(color.BOLD + 'Hello World !' + color.END)
########################################################################################################################
"""
   Функция прерывания программы по нажатию сочетаний клавиш  по нажатию CTRL + C .
"""

# CTRLZ.py
# Реализация прерывания по нажатию CTRL + C
def sigint_handler(signum, frame):
    print(current_time()+"\033[31m {}".format(' Выполнение программы прервано по нажатию CTRL + C !'))
    # os.abort()
    # raise SystemExit(1)
    os.kill(os.getpid(), 9)


signal.signal(signal.SIGINT, sigint_handler)
########################################################################################################################

# ToDo реализовать паттерн Singleton для запуска агента в единственном экземпляре, чтобы занимал ресурсы
"""
    Класс агента системы мониторинга. 
    Запускается всегда в единственном экземпляре (паттерн Singleton)
"""
class AgentMS:

    def __init__(self):
        # self.uds_receiver()
        print(' Объект агента системы мониторинга создан.')
        # @ToDo здесь в дальнейшем определить используемые ниже переменные в json-конфиге !
        # @ToDo взять значения из конфига и определить здесь
        self.loop_counter = 1
        self.serverPort = '999'
        self.sendDelayInSecs = 15  # 15
        self.rcvServerPort = '???'
        self.delay8 = 5
        self.delay9 = 5
        self.delay77 = 5
        # путь к пайпу межпрограммного взаимодействия в Ос
        self.fifoname = '/tmp/agentFifo0'

    ########################################################################################################################
    # @ ToDo TEST IT !
    """        
        Метод отправки информации средстами протокола UDP. Будет выполняться в отдельном потоке программы агента СМ
    """

    def send_HexInt_UDP(self, isRun4ever, ipaddr, port, bytesToSend):
        try:
            while True:
                uDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                uDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                uDPClientSocket.bind(('0.0.0.0', int(port)))
                serverAddressPort = (ipaddr, int(port))
                intArray = [int(x, 16) for x in bytesToSend]
                print(intArray)
                ba = bytearray(intArray)


                uDPClientSocket.sendto(ba, serverAddressPort)
                print("Sent "+ "\n" + " to the " + str(ipaddr) + ", " + str(port) + " at: " + " " + " by the: " + threading.currentThread().getName() + " ")
                print("Successfully sent")
                # Это условие для того, чтобы хотя бы один раз выполнились действия в теле цикла.
                if (isRun4ever == False):
                    break

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be)))
            print("\033[30m {}".format(""))
            return -1


########################################################################################################################
    """
        Метод получения и обработки информации средстами протокола UDP. Будет выполняться в отдельном потоке программы агента СМ
    """

    def UDP_receiver(self, port, ip='localhost'):
        import socket
        import sys

        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the port
        server_address = (ip, port)
        print('старт udp сервера {} на порте {}'.format(*server_address))
        sock.bind(server_address)

        while True:
            print('\nожидание получения сообщений по udp')
            data, address = sock.recvfrom(4096)

            print('получено {} байт от {}'.format(
                len(data), address))
            print(data)

            if data:
                sent = sock.sendto(data, address)
                print('отправлено {} обайт обратно к {}'.format(sent, address))
    # @ ToDo TEST IT ! UNDER CONSTRUCTION
    # def receivePackets(self, rcvServerPort):
    #     try:
    #         UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #         UDPClientSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         UDPClientSocket.bind(('0.0.0.0', int(rcvServerPort)))
    #         # UDPClientSocket.listen(2)'
    #         print()
    #         print(threading.currentThread().getName()
    #               + ": Server accepting data on: " + UDPClientSocket.getsockname())
    #         print()
    #
    #         while True:
    #             data, addr = UDPClientSocket.recvfrom(1024)
    #
    #             if int(data[0].encode('hex'), 16) == 9:
    #                 print(threading.currentThread().getName())
    #                 print("Code 9 Accepted!")
    #                 print("STOP SENDING INIT REQUEST")
    #                 print("Initialization Accepted...")
    #                 print("Test requesting...")
    #                 print(time.sleep(int(self.delay9)))
    #                 # Реализация сценария остановки потока отсылки init()
    #                 try:
    #                     pass
    #                     # sendPackets_thread.kill() #@ToDo sendPackets_thread
    #                 except NameError:
    #                     print("NameError caught")
    #                 finally:
    #                     print("TEST PASSED..OK")
    #                     # Чтение буффера(файл "udevice_out_data", сформированного pipeReceiver и отсылка ПМ-КУ обратно ответа
    #                     # Отсылаем ПМ-КУ содержимое файла "udevice_out_data" в который пишет модуль udevice через pipe
    #                     # send_HexInt_UDP(True, tmpdstIP, int(tmpdstPort), "9", readProtoConfig("udevice_out_data"), int(delay9)) #@ToDO sendPackets_thread
    #                     print("Stop sending code 9 result...")  # set flag_test, 9 send test'
    #                 print()
    #                 continue
    #
    #             elif int(data[0].encode('hex'), 10) == 77:
    #                 print(threading.currentThread().getName())
    #                 print("Code 77 Accepted!")
    #                 print("Switching to WORKING MODE")
    #                 # Реализация сценария остановки потока отсылки init()
    #                 try:
    #                     pass
    #                     # sendPackets_thread.kill()#@ToDo sendPackets_thread
    #                 except NameError:
    #                     print("NameError caught")
    #                 finally:
    #                     print()
    #                     # Чтение буффера, сформированного pipeReceiver и отсылка ПМ-КУ обратно ответа
    #                     # #senderPipe(True, fifoname, readProtoConfig("Protocol"),5, 10)
    #                     print()
    #                     " TEST PASSED..OK"
    #                     time.sleep(int(self.delay77))
    #                     # Чтение буффера(файл "udevice_out_data", сформированного pipeReceiver и отсылка ПМ-КУ обратно ответа
    #                     # Отсылаем ПМ-КУ содержимое файла "udevice_out_data" в который пишет модуль udevice через pipe
    #                     # send_HexInt_UDP(True, tmpdstIP, int(tmpdstPort), "9", readProtoConfig("udevice_out_data"), int(delay77))#@ToDO sendPackets_thread
    #                     pass
    #                     print("Stop sending code 77 result...")  # set flag_test, 9 send test')
    #                     print()
    #                     continue
    #             else:
    #                 print("INVALID RECEIVED PACKET. DROPPING IT AWAY ")
    #                 continue
    #         print(threading.currentThread().getName() + ": From address: " + str(
    #             addr[0]) + " on port: " +
    #               str(rcvServerPort) + " получен UDP: " + str(data[0]).decode()) + " c типом: " \
    #         + str(type(data[0]))
    #         print("Нажмите \"CTRL + C \ CTRL + Z\" для остановки программы...")
    #         print()
    #     except Exception as be:
    #         print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
    #         print("\033[30m {}".format(""))
    #         return -1
########################################################################################################################
    """
        Метод Unix Domain Socket receiver - реализация UDS-сервера. 
        По данной функции будет запускаться отдельный процесс/поток
        @param server_address - файл UDS-сокета
    """

    def uds_receiver(self, uds_socket_file):
        try:

            # uds_socket_file = './echo.socket'

            if os.path.exists(uds_socket_file):
                os.remove(uds_socket_file)

            print(" Открываем UNIX сокет...")
            server = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            server.bind(uds_socket_file)

            print(" Слушаем входящие сообщения от клиента в сокет-файле: \"{}\"".format(uds_socket_file))
            while True:
                datagram = server.recv(1024)
                if not datagram:
                    break
                else:
                    print("-" * 20)
                print(datagram)
                if b"DONE" == datagram:
                    break
            print(" -" * 20)
            print("Выключение...")
            server.close()
            os.remove(uds_socket_file)
            print(" Процесс с использованием UNIX domain socket завершен.")
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################

    """
        Метод отправки информации на UNIX domain socket 
    """

    def uds_sender(self, manual_input, uds_message, uds_socket_file):
        try:
        # SOCKET_FILE = '/tmp/uds_socket'
            print(" Подключение...")
            if os.path.exists(uds_socket_file):
                client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
                client.connect(uds_socket_file)
                print(" Процесс передачиз авершен")
                print(" Нажмите Ctrl + C чтобы выйти.")
                print(" Отправьте 'DONE' чтобы завершить серверный процесс UNIX domain socket.")
                while True:
                    if manual_input == True:
                        try:
                            uds_message = input("> ")  #
                            if "" != uds_message:
                                print(" ОТПРАВЛЕНО: %s" % uds_message)
                                client.send(uds_message.encode('utf-8'))
                                if "DONE" == uds_message:
                                    print(" Выключение клиентского процесса.")
                                    break
                        except KeyboardInterrupt as k:
                            print(" Выключение клиентского процесса.")
                            break
                    else:
                        print(" ОТПРАВЛЕНО сообщение на uds-сервер: %s" % uds_message)
                        client.send(uds_message.encode('utf-8'))
                client.close()
            else:
                print(" Не могу соединиться c uds-сервером!")
            print(" Выполнено")
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    ########################################################################################################################
    ################################################ РАБОТА С UNIX-pipes ###################################################
    ########################################################################################################################
    # @ToDo Test it and check !
    """ 
        Метод предоставления доступа к пайпам или uds сокетам
    """

    def allow_fifo_access(self, fifoname, password):
        try:
            if not os.path.exists(fifoname): print("File \" " + fifoname + " is not exist")
            if subprocess.Popen("chmod 777 " + fifoname) != 0 or \
                    subprocess.Popen("echo " + password + " sudo -S | chmod 777 " + fifoname) != 0 or \
                    subprocess.Popen("chmod 777 " + fifoname) != 0:
                print("Доступ к " + fifoname + " РАЗРЕШЕН")
            else:
                print("Доступ к " + fifoname + " не разрешен")
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    ########################################################################################################################

    """ 
        Метод получения информации через Unix-pipe, запускается в отдельном потоке программы 
    """

    def pipe_receiver(self, fifoname):
        try:
            while not os.path.exists(fifoname):
                # Cоздаем именованный канал системной утилитой mkfifo:
                os.mkfifo(fifoname)
                print("Именованный пайп  не существует в \"" + fifoname + "\" waiting for creation and data sending")
                time.sleep(1)

            print(threading.currentThread().getName())
            print("### " + threading.currentThread().getName() + " ###")
            print(" Процесс передачи данных средствами UNIX pipes начался ...")
            print(str(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") + " Ожидание входящих сообщений на: \"" + fifoname + "\""))
            print()

            while True:
                time.sleep(1)
                # блокируется до отправки данных в pipe, как только сообщение от клиента поступает в файл выводим его.
                pipein = open(fifoname, 'r')
                line = pipein.readline()

                print(' Пайп обработчик с pid = %d получил сообщение: "%s" на %s') \
                % (os.getpid(), line, str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                print("Нажмите \"CTRL + C \ CTRL + Z\" чтобы завершить..")
                print()
                return line
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
    """ 
        Метод отправки информации через Unix-pipe 
    """

    def pipe_sender(self, path2pipe, message2send):
        try:
            os.write(path2pipe, message2send)
            print(' Сообщение \"'
                  + message2send + '\" было отправлено в пайп с именем: \"' + '\"' + message2send)
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
########################################### Работа с разделяемой памятью ###############################################
########################################################################################################################
# https://docs.python.org/3/extending/extending.html @ToDo !!! РЕАЛИЗОВАТЬ сишные функции
    """
        @ToDo Метод-обертка над Си-функцией создания сегмента памяти.
    """

    def create_shared_memory_segment(self):
        try:
            print(" Сегмента разделяемой памяти создан: ")
            print(" Вызов Cи-функции с созданием общего буффера памяти")
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    ########################################################################################################################
    """
        @ToDo Метод-обертка над Си-функцией чтения из сегмента памяти.
    """

    def read_from_shared_memory_segment(self):
        try:
            print("Чтение из сегмента разделяемой памяти: ")
            print(' Вызов Си-функции printf("Process read from segment: %s\n", shmem);')
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
    """
        @ToDo Метод-обертка над Си-функцией записи в сегмент памяти.
    """

    def write_to_shared_memory_segment(self):
        try:
            print(" Вызов Cи-функции записи в общий буффер памяти memcpy(shmem, message2write, sizeof(message2write));")
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
####################################### РАБОТА c UART. Сбор параметров мониторинга #####################################
########################################################################################################################
    # pi@pi1:~ $ python3.pyseria7 -m serial.tools.list_ports
    """ Метод возвращает список интерфейсов UART"""
    def listOfUART_ifaces(self):
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            listOfUART_ifaces = []
            for port, desc, hwid in sorted(ports):
                print("{}: {} [{}]".format(port, desc, hwid))
                listOfUART_ifaces.append(port)
            print('Список UART-интерфейсов в системе: ' + str(listOfUART_ifaces))
            return listOfUART_ifaces
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
    """
        @param Элемент списка listOfUART_ifaces[]
        Перед выполнением установить sudo apt install setserial
    """

    def getUART_iface_info(self, UART_iface_name):
        try:
            print('Зарегистрирован UART интерфейс в ОС: ' + os.popen('setserial -g ' + UART_iface_name).read())
            print('Скорость потока(baudrate) интерфейса '+  UART_iface_name + ' = ' + os.popen('stty < ' + UART_iface_name).read())
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    ########################################################################################################################
    def testTransmitUART(self, port="/dev/ttyS0", baudrate=9600, quantity_bytes_to_read=10, sleep=0.03):

        try:
            # ser = serial.Serial("/dev/ttyAMA0", 9600)  # Open port with baud rate
            # ser = serial.Serial("/dev/ttyS0", 9600)  # Open port with baud rate
            ser = serial.Serial(port, baudrate)  # Open port with baud rate
            while True:
                received_data = ser.read(quantity_bytes_to_read)  # read serial port
                time.sleep(sleep)
                data_left = ser.inWaiting()  # check for remaining byte
                received_data += ser.read(data_left)
                print(received_data)  # print received data
                ser.write(received_data)  # transmit data serially
                print('Передача данных по UART прошла успешно !')
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    ########################################################################################################################
    """         
        Чтение из серийного порта (метод задумывался в рамках работы с UART) в зависимости от параметра unlimitedTx       
        ifaceFromRead может принимать значения "/dev/ttyAMA0","/dev/ttyAMA1",...,"/dev/ttyAMA(X)" , "/dev/ttyS0","/dev/ttyS1",...,"
        /dev/ttySX", "/dev/ttyS1",
        в зависимости от их доступности и настроек в config.txt или в  
        Список доступных интерфейсов в системе можно узнать командой:
            $ python3.x -m serial.tools.list_ports
        Позже будет реализован метод @ToDo listOfCOMs() показывающий данный список  реализующий данную команду
    """

    # @ ToDo TEST IT ! Configure UART to use in OS
    def readUART(self, ifaceFromRead, baudrate, quantity_bytes_to_read, unlimitedRX):
        try:
            ser = serial.Serial(ifaceFromRead)
            ser.baudrate = baudrate  # Set baud rate to 9600
            while True:
                received_data = ser.read(quantity_bytes_to_read)
                print(' Data' + str(received_data) + ' has be.with_traceback()en sucsessfully received from ' + str(
                    ifaceFromRead) + '')
                ser.close()
                if unlimitedRX == False: break
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
    # @ ToDo TEST IT ! после настройки ОС
    # @
    """ 
        Одно/много-кратная запись в серийный порт (в рамках работы с UART) в зависимости от параметра unlimitedTx       
        ifaceToWrite может принимать значения "/dev/ttyAMA0" , "/dev/ttyAMA1" , ... , "/dev/ttyAMA(X)" , "/dev/ttyS1" , ... , "/dev/ttySX" ,
        в зависимости от их доступности и настроек в config.txt или в  
        Список доступных интерфейсов в системе можно узнать командой:
        $ python3.x -m serial.tools.list_ports
        Позже будет реализован метод @ToDo listOfCOMs() показывий данный список
     """

    def writeUART(self, data2write, unlimitedTx=True, ifaceToWrite='/dev/ttyS1', baudrate=115200, quantChars2Read=10):
        try:
            ser = serial.Serial(ifaceToWrite)  # Откроем именованный последовательный порт для передачи данных
            ser.baudrate = baudrate  # установим скорость в бодах
            while True:
                ser.write(data2write)  # отправим данные в именованный последовательный  порт
                print(' Data' + str(data2write) + ' has be.with_traceback()en sucsessfully sent from ' + str(ifaceToWrite))
                ser.close()
                if unlimitedTx == False: break  # Для одноразовой передачи данных в последовательный интерфейс.
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
####################################### РАБОТА c vgencmd. Сбор параметров мониторинга ##################################
########################################################################################################################
    """
        vcgencmd - это утилита командной строки, которая может получать различную информацию от графического процессора VideoCore на Raspbe.with_traceback()rry Pi. 
        Большая часть доступной информации предназначена только для инженеров Raspbe.with_traceback()rry Pi, но есть ряд очень полезных опций, 
        доступных для конечных пользователей, которые будут описаны здесь.
    """
    """
        Метод обертка для команды "$ vcgencmd
        Метод возвращает структуру данных {список общих параметров мониторинга} основных узлов Raspbe.with_traceback()rry Pi со значениями
        Например:
        Clock Frequencies (Hz):
          arm       : 1500345728
          core      : 250000496
          h264      : 0
          isp       : 0
          v3d       : 499987808
          uart      : 0
          pwm       : 0
          emmc      : 250000496
          pixel     : 75001464
          vec       : 0
          hdmi      : 0
          dpi       : 0
        Voltages (V):
          core      : 0.8375
          sdram_c   : 1.1
          sdram_i   : 1.1
          sdram_p   : 1.1
        Temperatures (C):
                    : 62.0
        Codecs Enabled:
          h264      : False
          mpg2      : False
          wvc1      : False
          mpg4      : False
          mjpg      : False
          wmv9      : False
        Memory Allocation (bytes):
          arm       : 994050048
          gpu       : 79691776
    """

    def getAll_info_by_vcgencmd(self, interpretPath='/usr/local/bin/python3.8 '):
        try:
            os_output = os.popen(interpretPath + '-m vcgencmd').read()
            print(' Результат выполнения команды получения всех параметров мониторинга(getAll_info_by_vcgencmd) :')
            print(type(os_output))
            print(os_output)
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    ########################################################################################################################
    """
        Метод возвращает [список] общих параметров мониторинга основных узлов Raspbe.with_traceback()rry Pi 
        Нипример:
            ['arm', 'core', 'h264', 'isp', 'v3d', 'uart', 'pwm', 'emmc', 'pixel', 'vec', 'hdmi', 'dpi']
    """

    def getFrequency_Sources(self):
        try:
            print(vcgencmd.frequency_sources())
            return vcgencmd.frequency_sources()
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    ########################################################################################################################
    """
        Метод измерения частосты конкретного узла @param platform
        ['arm', 'core', 'h264', 'isp', 'v3d', 'uart', 'pwm', 'emmc', 'pixel', 'vec', 'hdmi', 'dpi']
        Clock:| Описание:
        -----------------
        arm   | ядра arm
        core  | VC4 скейлер ядра
        H264  | блок H264
        ISP   | Image Signal Processor
        v3d   | 3D-блок| 
        uart  | UART
        pwm   | ШИМ (аналоговый аудиовыход)
        emmc  | интерфейс SD-карты 
        pixel | пиксельный клапан
        vec   | Аналоговый видеокодер
        hdmi  | HDMI
        
        Периферийный интерфейс дисплея | dpi, например vcgencmd measure_clock
    """

    # def getMeasure_clock(self, measure_node='core'):
    #     print(' Частота узла "' + measure_node + '" = ' + str(vcgencmd.measure_clock(measure_node)) )
    #     return vcgencmd.measure_clock(measure_node)

    ########################################################################################################################
    """
        Метод измерения температуры конкретного узла @temp_source
        ['arm', 'core', 'h264', 'isp', 'v3d', 'uart', 'pwm', 'emmc', 'pixel', 'vec', 'hdmi', 'dpi']
        Возвращает температуру SoC, измеренную встроенным датчиком температуры.
    """

    def getMeasure_temp(self, temp_source):
        try:
            print(' Температура процессора: ' + str(vcgencmd.measure_temp()) + ' Градусов по цельсию')
            return vcgencmd.measure_temp()

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    ########################################################################################################################
    """
        Метод получения [списка источников] измерения напряжения, например:
        ['core', 'sdram_c', 'sdram_i', 'sdram_p']
    """

    def getVoltage_Sources(self, platform='core'):
        try:
            print (' Список источников для измерения напряжения:\n' + vcgencmd.voltage_sources())
            return vcgencmd.voltage_sources()
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    ########################################################################################################################
    """
        Метод получения источников напряжения .
    """

    def getVoltage_sources(self):
        try:
            print('Voltage sources are: ' + vcgencmd.voltage_sources())
            return vcgencmd.voltage_sources()
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    ########################################################################################################################
    """
        Метод измерения напряжения основных узлов(блоков) Raspbe.with_traceback()rry Pi  
        Отображает текущие напряжения, используемые конкретным блоком.
        Блок:      Описание:    
        core       VC4 core voltage
        sdram_c 
        sdram_i 
        sdram_p 
    """

    def getMeasure_volts(self, volts_source='core'):
        try:
            print(' Напряжение на узле "' + volts_source + '"' + '= ' + str(vcgencmd.measure_volts(volts_source)) + ' В')
            return vcgencmd.measure_volts(volts_source)
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################

    """
        Метод обертка для команды "$ vcgencmd get_config int "
    """

    def getConfig_vcgencmd(self):
        try:
            config = os.popen('vcgencmd get_config int').read()
            print(' Содержимое конфигурационного файла: ' + config)
            return config
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
    """
        Метод обертка для команды " $ vcgencmd get_throttled "
        This returns a hex numbe.with_traceback()r in which the following bits may be.with_traceback() set:
            0: under-voltage
            1: arm frequency capped
            2: currently throttled
            16: under-voltage has occurred
            17: arm frequency capped has occurred
            18: throttling has 
            
        Метод возвращает шестнадцатеричное число, в котором могут быть установлены следующие биты:
             0: пониженное напряжение
             1: частота arm ограничена
             2: в настоящее время ограничен
             16: произошло пониженное напряжение
             17: произошло ограничение частоты arm
             18: произошел троттлинг
        Нулевое значение указывает на то, что ни одно из указанных выше условий не выполняется.

        Чтобы определить, был ли установлен один из этих битов, преобразуйте возвращаемое значение в двоичный файл, 
        а затем пронумеруйте каждый бит вверху. Затем вы можете увидеть, какие биты установлены. Например:

        0x50000 = 0101 0000 0000 0000 0000

        Добавляя битовые числа вверху, получаем:

        19 18 17 16 15 14 13 12 11 10 9 8 7 6 5 4 3 2 1 0
         0  1  0  1  0  0  0  0  0  0 0 0 0 0 0 0 0 0 0 0
        Из этого мы можем видеть, что биты 18 и 16 установлены, что указывает на то, что Pi 
        ранее регулировался из-за пониженного напряжения, но в настоящее время не регулируется по какой-либо причине.
     """

    def getThrottled(self, interpretPath='/usr/local/bin/python3.8'):
        try:
            os_output = os.popen('vcgencmd get_throttled').read()
            print(' Статус троттлинга:  ')
            print((os_output[-4:-1]))
            return os_output[-4:-1]
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
    """
        Метод получения загрузки процессора
        "" "Возвращает число с плавающей точкой, представляющее текущий общесистемный процессор
             использование в процентах.
        
             Когда * интервал * равен> 0,0, сравнивается системное время ЦП, прошедшее до
             и после интервала (блокировка).
        
             Когда * interval * равен 0.0 или None, сравнивает прошедшее время системного процессора
             с момента последнего вызова или импорта модуля, возврат сразу (не
             блокирование). Это означает, что в первый раз это называется
             верните бессмысленное значение 0.0, которое вы должны игнорировать.
             В этом случае рекомендуется для точности, чтобы эта функция была
             вызывается с интервалом не менее 0,1 секунды.
        
             Когда *percpu* равно True, возвращает список с плавающей точкой, представляющий
             использование в процентах для каждого процессора.
             Первый элемент списка относится к первому процессору, второй элемент
             на второй процессор и так далее.
             Порядок в списке соответствует вызовам.
              >>> # blocking, system-wide
              >>> psutil.cpu_percent(interval=1)
              2.0
              >>>
              >>> # blocking, per-cpu
              >>> psutil.cpu_percent(interval=1, percpu=True)
              [2.0, 1.0]
              >>>
              >>> # non-blocking (percentage since last call)
              >>> psutil.cpu_percent(interval=None)
              2.9
              >>>
    """

    def getCPU_info(self):
        try:
            #print("\033[30m\033[1m {}".format(' ИНФОРМАЦИЯ О ПРОЦЕССОРE:'))
            #print('\x1b[1;11m' + 'ИНФОРМАЦИЯ О ПРОЦЕССОРE:' + '\x1b[0m')
            print('---------------------------------------------------------------------------------------------------')
            print('ИНФОРМАЦИЯ О ПРОЦЕССОРE:')
            print('---------------------------------------------------------------------------------------------------')
            setTerm(Agent_object.loop_counter)
            # map() конвертирует строковые элементы в intы
            listCPUload = list(map(int, psutil.cpu_percent(interval=1, percpu=True)))

            #print('Загрузка процессора: ' + str(listCPUload))
            #print('Частота процессора: ' + str(psutil.cpu_freq()))
            #print('Статистика процессора: ' + str(psutil.cpu_stats()))
            #print('CPU cpu_times_percent: ' + str(psutil.cpu_times_percent()))

            self.u1_1 = int(listCPUload[0])
            self.u1_2 = int(listCPUload[1])
            self.u1_3 = int(listCPUload[2])
            self.u1_4 = int(listCPUload[3])
            #Для намеренного вызова ошибки
            #self.u1_5 = listCPUload[4]
            listCPUfreq = psutil.cpu_freq(('percpu=True'))
            # частота ядра процессора 1
            self.u2_1 = int(str(listCPUfreq[0]).split('=')[1][:-7])
            #print(self.u2_1)
            # частота ядра процессора 2
            self.u2_2 = int(str(listCPUfreq[1]).split('=')[1][:-7])
            #print(self.u2_2)
            # частота ядра процессора 3
            self.u2_3 = int(str(listCPUfreq[2]).split('=')[1][:-7])
            #print(self.u2_3)
            # частота ядра процессора 4
            self.u2_4 = int(str(listCPUfreq[3]).split('=')[1][:-7])
            #print(self.u2_4)
            print('Загрузка ядра процессора 1: ' + str(self.u1_1) + '%, частота ядра процессора 1: ' + str(listCPUfreq[0]).replace('scpufreq(','').replace('current','Текущая').replace('min','Минимальная').replace('max','Максимальная').replace('.0',' МГц')[:-1])
            print('Загрузка ядра процессора 2: ' + str(self.u1_2) + '%, частота ядра процессора 2: ' + str(listCPUfreq[1]).replace('scpufreq(','').replace('current','Текущая').replace('min','Минимальная').replace('max','Максимальная').replace('.0',' МГц')[:-1])
            print('Загрузка ядра процессора 3: ' + str(self.u1_3) + '%, частота ядра процессора 3: ' + str(listCPUfreq[2]).replace('scpufreq(','').replace('current','Текущая').replace('min','Минимальная').replace('max','Максимальная').replace('.0',' МГц')[:-1])
            print('Загрузка ядра процессора 4: ' + str(self.u1_4) + '%, частота ядра процессора 4: ' + str(listCPUfreq[3]).replace('scpufreq(','').replace('current','Текущая').replace('min','Минимальная').replace('max','Максимальная').replace('.0',' МГц')[:-1])
            # Для намеренного вызова ошибки
            #print('Загрузка ядра процессора 5: ' + str(self.u1_5) + '%, частота ядра процессора 5: ' + str(listCPUfreq[4]).replace('scpufreq(','').replace('current','Текущая').replace('min','Минимальная').replace('max','Максимальная'))
            #listCPUfreq = list(map(int, psutil.cpu_freq(('percpu=False'))))
            return listCPUload
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
            #print("\033[31m {}".format(be.with_traceback().with_traceback()))
########################################################################################################################
    """
        Интегральная оценка загрузки процессора.
    """
    def getCPU_percent(self):
        try:
            # int() для округления float
            #print('\x1b[1;11m' + 'Интегральная оценка загрузки процессора:' + '\x1b[0m' + str(int(psutil.cpu_percent())) + '%')
            print('---------------------------------------------------------------------------------------------------')
            print('ИНТЕГРАЛЬНАЯ ОЦЕНКА ЗАГРУЗКИ ПРОЦЕССОРА:' + str(int(psutil.cpu_percent())) + '%')
            print('---------------------------------------------------------------------------------------------------')
            #print('Интегральная оценка загрузки процессора: ' + str(int(psutil.cpu_percent())) + '%')
            return int(psutil.cpu_percent())
        except Exception as e:
            print("\033[31m {}".format('Возникла ошибка в программе с кодом:' + "\033[31m {}".format(e)))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################

    def getCPU_virtual_memory(self):
        try:
            print(' Виртуальная память ' + str(psutil.virtual_memory()))
            return psutil.virtual_memory()
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################

    """
        Метод получения [списка] (массива) параметров мониторинга об ОС "
    """

    def getSoftware_version(self):
        try:
            release_name     = str(os.popen('lsb_release -i').read()).replace('Distributor ID','Имя релиза').replace('\t',' ')
            self.p2 = release_codename = str(os.popen('lsb_release -c').read()).replace('Codename','Кодовое имя релиза').replace('\t',' ')
            self.p3 = release_num      = str(os.popen('lsb_release -r').read()).replace('Release','Номер релиза').replace('\t',' ')
            self.p4 = kernel_ver = 'Версия ядра ОС: ' + os.popen('uname -r').read().replace('\t',' ')
            self.p5 = arch_type = 'Тип архитектуры: ' + os.popen('uname -m').read().replace('\t',' ')
            #os.popen('vcgencmd version').read()
            currOsVer = release_name + release_num + release_codename + kernel_ver + arch_type
            print('Информация об операционной системе: ')
            print(currOsVer)
            # Получаем список из срезов -1 - индекс последнего символа
            self.p1 = release_name[release_name.index(":") + 2: -1]
            self.p2 = release_codename[release_codename.index(":") + 2:-1]
            self.p3 = int(release_num[release_num.index(":") + 2:-1])
            self.p4 = kernel_ver[kernel_ver.index(":") + 2:-1]
            self.p5 = arch_type[arch_type.index(":") + 2:-1]

            currOsVer_list = [self.p1,self.p2,self.p3,self.p4,self.p5]
            #print(currOsVer_list)
            return currOsVer_list
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################

    """
        Метод обертка для команды "$ vcgencmd get_mem arm"
        Примечание. 
        На Raspbe.with_traceback()rry Pi 4 с объемом оперативной памяти более 1 ГБ опция  является неточной. 
        Это связано с тем, что микропрограммное обеспечение графического процессора, которое реализует эту команду, 
        знает только о первом гигабайте оперативной памяти в системе, поэтому при настройке режима всегда будет
        возвращаться 1 ГБ минус значение памяти GPU. Чтобы получить точный отчет об объеме памяти ARM, используйте 
        одну из стандартных команд Linux, 
        например free или cat /proc/meminfo
    """

    def getMem_arm(self):
        try:
            os_output = os.popen('vcgencmd get_mem arm').read()
            print('Объем оперативной памяти: ' + os_output)
            self.r1 = int(os_output[4:-2])
            #print(self.r1)
            return self.r1
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################

    def getRAM(self):
        try:
            print(' ИНФОРМАЦИЯ ПО СОСТОЯНИЮ ОПЕРАТИВНОЙ ПАМЯТИ cat /proc/meminfo: ')
            print('-------------------------------------------------')
            cat_proc_meminfo_raw = os.popen('cat /proc/meminfo').read()
            cat_proc_meminfo = str(cat_proc_meminfo_raw).split()
            #print(cat_proc_meminfo)
            self.m1 = int(float(cat_proc_meminfo[1]))
            print('Всего памяти: ' + str(self.m1) + ' kB')
            self.m2 = int(float(cat_proc_meminfo[4]))
            print('Свободно памяти: ' + str(self.m2) + ' kB')
            self.m3 = int(float(cat_proc_meminfo[7]))
            print('Доступно памяти: ' + str(self.m3) + ' kB')
            free = os.popen('free').read()
            #print('-------------------------------------------------')
            #print(' ИНФОРМАЦИЯ ПО RAM ИЗ КОМАНДЫ free info: \n' + free)
            #print('-------------------------------------------------')
            return [self.m1, self.m2, self.m3]
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
    """
        Метод обертка для команды "$ vcgencmd read_ring_osc"
        Возвращает текущее напряжение скорости и температуру кольцевого генератора.
    """

    def getRing_osc(self):
        try:

            ring_osc = os.popen('vcgencmd read_ring_osc').read()
            self.o1 = float(ring_osc[17:22]) # Скорость
            self.o2 = float(ring_osc[28:34]) # Напряжение
            self.o3 = int(ring_osc[38:40]) # Температура
            print('ТЕКУЩИЕ ЗНАЧЕНИЯ КОЛЬЦЕВОГО ГЕНЕРАТОРА (Ring Oscillator):')
            print('----------------------------------------')
            print(' Скорость = {} МГц\n Напряжение = {} В\n Температура = {} °C \n'.format(str(self.o1), str(self.o2), str(self.o3)))
            #print(self.o1,self.o2,self.o3)
            return [self.o1, self.o2, self.o3]
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    """
        Метод обертка для команды "$ vcgencmd
        Отображает включенное и обнаруженное состояние официальной камеры.
        1 означает да, 0 означает нет. Пока все прошивки (кроме урезанных версий)
        будет поддерживать камеру, эта поддержка должна быть включена с помощью raspi-config.
    """

    def get_Camera(self):
        try:
            # print(type(subprocess.Popen('vcgencmd get_camera')))
            camera_status = os.popen('vcgencmd get_camera').read()
            self.c1 = int(str(camera_status).split(' ')[0][-1])
            self.c2 = int(str(camera_status).split(' ')[1][-2])
            print('СОСТОЯНИЕ ПОДКЛЮЧЕННОЙ КАМЕРЫ:')
            print('-----------------------------------')
            print('{}\n{}'.format(str(camera_status).split(' ')[0].replace('supported=','Включена в настройках: ').replace('0','Нет').replace('1','Да'), str(camera_status).split(' ')[1].replace('detected=','Определяется в ОС: ').replace('0','Нет').replace('1','Да')))
            return [self.c1, self.c2]
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    """
        Отображает содержимое памяти одноразового программирования (OTP), которая является частью SoC.
        Это 32-битные значения, индексированные от 8 до 64. Более подробную информацию смотрите на странице битов OTP.
    """

    def get_otp_dump(self):
        try:
            otp_dump = os.popen('vcgencmd otp_dump').read()
            print('CОДЕРЖИМОЕ ПАМЯТИ ОДНОРАЗОВОГО ПРОГРАММИРОВАНИЯ (OTP):\nРегистр:Значение' )
            print("------------------------------------")
            print(otp_dump)
            return otp_dump
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    def get_ProcInfo(self):
        try:
            cat_proc_cpu = os.popen('cat /proc/cpuinfo').read()
            print(' ДАННЫЕ ПО ПАРАМЕТРАМ ПРОЦЕССОРА ИЗ /proc/cpuinfo :\n' + cat_proc_cpu)
            return cat_proc_cpu
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
####################################### РАБОТА c procfs. Сбор параметров мониторинга ###################################
########################################################################################################################
    """
        Метод чтения из procfs параметров параметров мониторинга аппаратной части:
            - Получено байт на указанному сетевом интерфейсе
            - Информации UDP дэйтаграммах прошедшим через указанный интерфейс  
    """

    def readProcfsData(self, procfs_input_parameter_to_monitor, interfaceName):
        try:
            from procfs import Proc
            proc = Proc()
            if procfs_input_parameter_to_monitor == 'all_params':

                print(' ПАРАМЕТРЫ МОНИТОРИНГА ПРОЦЕССОРА В ВИДЕ АССОЦИАТИВНОГО МАССИВА: ')
                print("------------------------------------")
                print(str(proc.loadavg))
                print("------------------------------------")
                print(str(proc.net.dev.wlan0.receive.bytes))
                print(str(proc.meminfo.MemFree))
                print(str(proc.net.snmp.Udp))

            # @ToDo ############################ REPLACE /proc/cpuinfo CALLING#####################################################
            if procfs_input_parameter_to_monitor == 'loadavg':
                print(' ПАРАМЕТРЫ МОНИТОРИНГА ПРОЦЕССОРА В ВИДЕ АССОЦИАТИВНОГО МАССИВА: ')
                print(str(proc.loadavg))
                print("------------------------------------")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "eth0":
                    print(
                        ' На указанном сетевом интерфейсе: \"' + str(interfaceName) + '\" получено байт: '
                        + str(proc.net.dev.eth0.receive.bytes))
                    print("------------------------------------")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "eth1":
                    print(
                        ' На указанном сетевом интерфейсе: \"' + str(interfaceName) + '\" получено байт: '
                        + str(proc.net.dev.eth1.receive.bytes))

            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "eth2":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.eth2.receive.bytes))
                    print("__________________________")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "eth3":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.eth3.receive.bytes))
                    print("------------------------------------")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlan0":
                    print(
                        ' На указанном сетевом интерфейсе: \"' + str(interfaceName) + '\" получено байт: '
                        + str(proc.net.dev.wlan0.receive.bytes))
                    print("------------------------------------")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlan1":
                    print(' На указанном сетевом интерфейсе: \"' + str(interfaceName) + ' получено байт: '
                          + str(proc.net.dev.wlan1.receive.bytes))
                    print("__________________________")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlan2":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + ' получено байт: ' + str(proc.net.dev.wlan2.receive.bytes))
                    print("__________________________")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlan3":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.wlan3.receive.bytes))
                    print("__________________________")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlp1s0":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.wlp1s0.receive.bytes))

            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlp2s0":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.wlp2s0.receive.bytes))

            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlp3s0":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.wlp3s0.receive.bytes))

            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlp1s1":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.wlp1s1.receive.bytes))

            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlp1s2":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.wlp1s1.receive.bytes))
                    print("------------------------------------")
            if procfs_input_parameter_to_monitor == 'eth_info':
                if interfaceName == "wlp1s3":
                    print(' На указанном сетевом интерфейсе: \"' + str(
                        interfaceName) + '\" получено байт: ' + str(proc.net.dev.wlp1s1.receive.bytes))
                    print("------------------------------------")
            # @ ToDo Добавить необходимые строчки кода для вычитывания по нужному интерфейсу, если необходимо.
            if procfs_input_parameter_to_monitor == 'mem_free_info':
                print(' свободной памяти: ' + str(proc.meminfo.MemFree) + " байт")
                print("------------------------------------")
            if procfs_input_parameter_to_monitor == 'udp_info':
                print(' Статистика UDP по дэйтаграммам : ')
                print("------------------------------------")
                for i in proc.net.snmp.Udp:
                    print("\t", i, ":", proc.net.snmp.Udp[i])
                print("------------------------------------")
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
################################### Использование дискового пространства ###############################################
########################################################################################################################
    """
        Метод обертка для команды для определения параметров пространства накопителя
    """

    def getDisk_usage(self, diskName='/dev/root'):
        try:
            getDiskUsageRaw = os.popen('df -Th').readlines()
            getDiskUsage = os.popen('df -Th').read()
            print('-------------------------------------------')
            print(' ВНУТРЕННЯЯ ПАМЯТЬ.ИСПОЛЬЗОВАНИЕ ДИСКА: \n' + os.popen('df -Th').read() )
            diskUsageList = []
            for d in getDiskUsageRaw:
                d =  list(filter(None,str(d[:-1]).split(' '))) # удаляем пустые элементы
                diskUsageList.append(d) #
            self.d1_1 = int(float(diskUsageList[1][4][:-1].replace(',','.'))) # Доступно  int(5,3)
            #print(self.d1_1)
            self.d1_2 = int(float(diskUsageList[1][3][:-1].replace(',','.'))) # Использовано  int(5,3)
            #print(self.d1_2)
            print('На ' + str(diskName) + ' ' + diskUsageList[0][5]+'упно' + ' свободного места ' +  diskUsageList[1][4])
            print('На ' + str(diskName) + ' ' + diskUsageList[0][4] + ' ' +  diskUsageList[1][3] + ' = ' + diskUsageList[1][5] + ' от свободного места')
            print(getDiskUsage)
            print('-------------------------------------------')
            externalDiskUsageRaw =  str(os.popen('du /media/pi').read())
            #internalDiskUsage = str(os.popen('du -h /media/pi').read().split('\n')[:-1])
            #print(internalDiskUsage) # Детализированный рекурсивный вывод
            print(' ВНЕШНЯЯ ПАМЯТЬ, СВОБОДНО ВСЕГО СУММАРНО на : ')
            print(externalDiskUsageRaw)
            #self.d2_1 = int(float(internalDiskUsageRaw[:3]))
            #print(self.d2_1)
            import re
            externalDiskUsage = re.findall('\d+M|K',externalDiskUsageRaw)
            #print(str([self.d1_1,self.d1_2] + externalDiskUsage))
            #return diskUsageList
            return [self.d1_1,self.d1_2] + externalDiskUsage

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    """
        Ноды памяти для измерения: mmcblk0, ram11, ram2, loop1, ram0, ram9, ram7, loop6, ram14, ram5, loop4, ram12, ram3, 
        loop2, ram10, ram1, loop0, ram8, loop7, ram15, ram6, loop5, ram13, ram4, loop3, 
    
    """
    def getDiskCapacity(self, diskName= 'all'):
        try:
            from sysfs import sys
            sys = Node()
            # print(sys.__dir__())
            # print(sys.__dict__)

            for bdev in sys.block:


                if diskName == 'all':
                    print('Емкость логического раздела хранения данных \"{}\" = '.format(bdev),
                          str(int(bdev.size) / 1024 / 1024) + ' Мегабайт')

                if(diskName == str(bdev)):
                    print('Емкость логического раздела хранения данных \"{}\" = '.format(bdev),
                          str(int(bdev.size) / 1024 / 1024) + ' Мегабайт')

                    break

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    '''
        https://www.raspbe.with_traceback()rrypi.org/forums/viewtopic.php?t=81463
        Вывод blkid содержит только UUID файловой системы. Серийный номер физической карты находится в /sys/block/mmcblk0/device/serial
    '''
    def getSdcard_info(self):
        print('ИНФОРМАЦИЯ ОБ SD-CARD:')
        print('-----------------------------------')
        try:
            blkid = os.popen('blkid').read().split()
            for b in blkid: print(b)

            print('Серийный номер sd-карты: ' + os.popen('cat /sys/block/mmcblk*/device/serial').read())

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
#######################################################################################################################
################################## Использование RTC-часов реального времени ###########################################
########################################################################################################################

    """
        Метод обертка для нахождения списка номеров шин i2c, 
    """

    def find_I2C_BusNUM(self):
        try:
        # -2 - предпоследний символ в выражении /dev/i2c-* с учетом пробела в конце.
            print('Найден номер шины I2C устройства в системе: ' + str(os.popen('ls /dev/i2c-*').read()[-2]))

            return os.popen('ls /dev/i2c-*').read()[-2].split('\n')
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
    def defineRTC_device(self, bus_numb):
        try:
            #return subprocess.Popen('echo ds1307 ' + address + ' > ' + path, shell=True)
            import smbus
            import errno

              # 1 indicates /dev/i2c-1
            bus = smbus.SMBus(bus_num)
            device_count = 0

            for device in range(3, 128):
                try:
                    bus.write_byte(device, 0)
                    print("Найдено {0}".format(hex(device)))
                    device_count = device_count + 1
                except IOError as e:
                    if e.errno != errno.EREMOTEIO:
                        print("\033[31m {}".format("Ошибка : {0} по адресу {1}".format(e, hex(device)))+ "\033[31m ")
                        return -1
                except Exception as e:  # exception if read_byte fails
                    print("Ошибка неизв.: {0} по адресу  {1}".format(e, hex(device)))
                    return -1
            bus.close()
            bus = None
            print("Найдено {0} устройств".format(device_count))
            return device_count
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
    def getI2C_baudrate(self):
        try:
            #dtparam = i2c_baudrate = 40000
            with open("/boot/config.txt") as myfile:
                for line in myfile:
                    if line.startswith('dtparam=i2c_baudrate='):
                        print('I2C скорость потока в бодах (baudrate) = ' + line.partition("=")[-1].partition("=")[-1] )
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################

    """
        Метод обертка для записи даты и времени в память RTС:
             
        @param time в формате "2020-04-19 15:11:40"
            #Примеры установки и работы со временем
            # sudo timedatectl set-time YYYY-MM-DD №
            # sudo timedatectl set-time HH:MM:SS
            # sudo timedatectl set-time '10:42:43'
            # sudo timedatectl set-time '2020-05-25 13:39:00'
            # date -s "2 NOV 2019 18:00:00"
            # date +%Y%m%d -s "20191107"
            # date

    """

    def setRTC_time(self, time2set):
        try:
            os.popen('modprobe.with_traceback() i2c-bcm2835')
            os.popen('modprobe.with_traceback() rtc-ds1307')
            os.popen('echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device')
            subprocess.Popen('timedatectl set-time ' + time2set, shell=True)
            print('Системное время было успешно установлено: ' + time2set)
            return os.popen('hwclock -w').read()

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
    """
        Метод обертка для чтения даты и времени из памяти RTC
        Если часы доступны получаем метку времени и дату:
            
        Если часы недоступны получаем следующее сообщение:
        
        hwclock: Cannot access the Hardware Clock via any known method.
        hwclock: Use the --verbose option to see the details of our search for an access method.
       
        прежде чем выполнять этот этот метод дать в visudo пользователю права на исполнение команды hwclock
        # Allow membe.with_traceback()rs of group sudo to execute any command
            %sudo   ALL=(ALL:ALL) ALL
            %sudo     ALL=(ALL) NOPASSWD: /sbin/hwclock 
        будут загружены путем записи магической строки, содержащей идентификатор устройства и адрес I2C,
        в специальный файл в /sys/class/i2c-adapter, предварительно загрузив драйвер для интерфейса I2C и устройства RTC командами:
            modprobe.with_traceback() i2c-bcm2835
            modprobe.with_traceback() rtc-ds1307
            echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device
        при повторном вызове предидущей строки может возникать IOError

    """

    def getRTC_time(self):
        try:
            os.system('sudo -S setfacl -m g:sudo:r /dev/rtc')
            os.system('modprobe.with_traceback() i2c-bcm2835')
            os.system('modprobe.with_traceback() rtc-ds1307')
            # при повторном вызове предидущей строки может возникать IOError
            #os.system('echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device')

            #os.system('/sbin/hwclock -r')
            self.t1 = os.popen('/sbin/hwclock -r').read()
            print('-----------------------------------')
            print(' ТЕКУЩЕЕ АППАРАТНОЕ ВРЕМЯ: ' + self.t1)
            print('-----------------------------------')
            return self.t1

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

########################################################################################################################
    """
        Можно проверить доступность часов командой: 
        dmesg |grep rtc
        
        Если часы недоступны:
        [    7.079358] rtc-ds1307: probe.with_traceback() of 1-0068 failed with error -121
        Если часы доступны получаем : 
        [    6.871853] rtc-ds1307 1-0068: registered as rtc0

    """
    def getRTC_availability(self):
        
        try:
            
            getRTC = os.popen('dmesg |grep rtc').read()
            
            print(getRTC)
            return getRTC

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
    """
    @param bus_num = 0..N Номер шины
    """

    def I2C_scan(self, bus_num, start=0x03, end=0x78):
        from smbus2 import SMBus
        import sys
        try:

            bus = SMBus(bus_num)

            print(' ИНФОРМАЦИЯ по I2C:')
            print("Номер I2C шины: " + str(bus_num))
            print("Начальный адрес шины: " + hex(start))
            print("Конечный адрес шины: " + hex(end) + "\n")

            for i in range(start, end):
                val = 1
                try:
                    bus.read_byte(i)
                except OSError as e:
                    val = e.args[0]
                finally:
                    if val != 5:  # No device
                        if val == 1:
                            res = "Устройство доступно на шине I2C по адресу "
                            print(res + " -> " + hex(i))
                        elif val == 16:
                            res = "Устройство занято на шине I2C по адресу"
                            print(res + " -> " + hex(i))
                        elif val == 110:
                            res = "Таймаут опроса на шине I2C"
                            print(res )
                        else:
                            res = "на шине I2C код ошибки "+ str(val) +" по адресу"
                            #print(res + " -> " + hex(i))
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    """
        Метод чтения байта данных. Открыть шину I2C «0» и прочитать один байт по адресу 0x39, со смещением 0x0C (адрес регистра).
    """
    def i2cReadByteData(self, busNum=0, addess2read=0x39, offset=0x0C):
        bus = smbus.SMBus(busNum)
        try:
            data2read = bus.read_byte_data(addess2read, offset)
            print(data2read)
            bus.close()
        except BaseException as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    """
        Метод чтения массива данных. Открыть шину I2C «0» и записать один байт по адресу 0x39, со смещением 0x0C (адрес регистра).
    """
    # @ToDo UNDER CONSTRUCTION TEST IT !  запись байта
    def i2cwrite(self, busNum=0, data2write=45, addess2write=0x39, offset=0x0C):
        try:
            bus = smbus.SMBus(busNum)
            bus.write_byte_data(addess2write, offset, data2write)
            bus.close()
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
################################################# Работа с SPI #########################################################
########################################################################################################################

# Ссылки ниже могут полезны при работе с LCD-дисплеем
#        https://docs.openmv.io/library/pyb.SPI.html
#       https://github.com/openmv/openmv/blob/b70d2e4210a1968fe831cf0fa92bd6bace9e37e3/scripts/libraries/ssd1306.py
    def getList_SPI_devs(self):
        try:
            list_SPI_devs = str(os.popen('ls /dev/spidev0.*').read()).split()
            print(' Список устройств SPI: ' + str(list_SPI_devs))
            return list_SPI_devs
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    """ Метод тестирования на работоспособность устройств по spi
        https://www.raspbe.with_traceback()rrypi.org/documentation/hardware/raspbe.with_traceback()rrypi/spi/README.md
        Приведенное выше записывает 3 байта, содержащихся в data_out, и копирует полученные данные в data_in. 
        Обратите внимание, что data_in всегда будет кортежем той же длины, что и data_out, и будет просто отражать состояние вывода MISO на протяжении транзакции. 
        Пользователь должен понять поведение устройства, подключенного к выводам SPI.

    """
    def cspidev_test(self, deviceNum):
        try:
            print(' Тестирование по SPI устройства /dev/spidev0.'+ str(deviceNum))
            tested = os.popen('./spidev_test -D '+ str(deviceNum)).read()
            print(tested)
            return tested
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    def spi_test(self, deviceNum):
        try:
            import spi
            # Откройте дескриптор файла на устройстве SPI с помощью одного из двух чипов:
            #device_0 = spi.openSPI(device="/dev/spidev0.1", mode=0, speed=500000, bits=8, delay=0)
            # Ключевое слово устройства может быть "/dev/spidev0.0" или "/dev/spidev0.1".
            # Разница относится к тому, какой вывод выбора микросхемы используется драйвером устройства SPI.
            # Ключевое слово mode может быть 0,1,2 или 3, и многие устройства SPI могут работать на частоте до 8000000 Гц,
            # Используйте возвращенный дескриптор устройства для проведения транзакции SPI

            # Открыть дескриптор файла для
            # spi device 0, использующий вывод CE0 для выбора чипа
            device = spi.openSPI(device=deviceNum,
                                   mode=0,
                                   speed=1000000)

            # Это не обязательно, а не просто демонстрировать обратную петлю
            #data_in = (0x00, 0x00, 0x00)
            # Транзактные данные
            data_out = (0xFF, 0x00, 0xFF)
            print("Отправлен запрос c числовой последовательностью: " + str(data_out) + " на устройство: " + str(deviceNum))
            # This is not necessary, not just demonstrate loop-back
            #data_in = (0x00, 0x00, 0x00)
            data_in = spi.transfer(device, data_out)
            print("Получен ответ от устройства " + str(deviceNum) + " c числовой последовательностью:" + str(data_in))
            print('------------------------------------------------------------')
            print('ПАРАМЕТРЫ SPI устройства {} :'.format(deviceNum))
            print('------------------------------------------------------------')
            #print(device)
            print('Ключевое слово mode: ' + str(device[b'mode']))
            print('Бит за слово (bits per word): ' + str(device[b'bits']))
            print('Скорость транзакции : ' + str(device[b'speed']) + ' Гц')
            print('Задержка : ' + str(device[b'delay']) + ' мс')

            # Close file descriptors
            spi.closeSPI(device)


        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    # @ ToDo UNDER CONSTRUCTION TEST IT !
    def spi_test_(self,CHIP_SELECT_0_OR_1, value_8bit= [191, 192 , 193]):
        try:
            import spidev
            spi = spidev.SpiDev()
            spi.open(0, CHIP_SELECT_0_OR_1)
            spi.max_speed_hz = 1000000

            resp = spi.xfer(value_8bit)
            print(' ОБРАЩЕНИЕ К АКСЕЛЕРОМЕТРУ MPU92/65 ПО SPI ')
            print('-----------------------------------------')
            print(' Ответ по SPI от устройства в виде числовой последовательности: ' + str(resp))
            zAccel = (value_8bit[1] << 8) + value_8bit[2]
            print(' Акселлерация по оси Z: ' + str(zAccel))
            return zAccel
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    """
        https://github.com/m-rtijn/mpu6050
    """
    def MPU6050_alive_(self):
        try:
            from mpu6050 import mpu6050
            sensor = mpu6050(0x68)
            accelerometer_data = sensor.get_accel_data()
            print(accelerometer_data)
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    """
    https://pypi.org/project/micropython-mpu9250/
    MPU-9250 - это система в ??? (System in Package), которая объединяет  микросхемы: 
    MPU-9255 - ?
    MPU-6500, который содержит 3-осевой гироскоп и 3-осевой акселерометр, и AK8963, 
    который представляет собой 3-осевой цифровой компас.
    MPU-6555 - ?
    """

    """
        @ToDo Under Construction !!!
        https://forum.micropython.org/viewtopic.php?t=4712
        https://www.raspbe.with_traceback()rrypi.org/forums/viewtopic.php?t=221293
        https://docs.openmv.io/library/pyb.SPI.html
    """
    def MPU9265_alive_via_SPI(self):
        import pyb
        from pyb import SPI
        from pyb import Pin
        try:
            # spi operation
            print(' \ SPI Test\n')
            print('  Включение...')
            # wait for power up mpu9250
            pyb.delay(500)
            print('Успешно заделэили SPI!')

            # int_spi = Pin('Y11', Pin.IN, Pin.PULL_UP)
            cs_spi1 = Pin('Y11', Pin.OUT_PP)
            cs_spi2 = Pin('Y9', Pin.OUT_PP)
            cs_spi = (cs_spi1, cs_spi2)
            cs_spi[1].high()
            cs_spi[0].high()

            # based on datasheet, baudrate is exception
            spi = SPI(1, SPI.MASTER, baudrate=115200, polarity=1, phase=1, firstbit=SPI.MSB)

            sendW = bytearray(2)  # for write operation (w/data)
            sendR = bytearray(1)  # for read operation
            recvRo = bytearray(1)  # for read operation, temporary data container
            recvRs = bytearray(12)  # for read operation, data container

            # pwr mgmt1 addr, reset device
            sendW[0] = 0x6B
            sendW[1] = 0x80
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()
            pyb.delay(200)
            print('\nСброс устройства произведен успешно!')

            # автоматический выбор источника часов, гироскоп или внутренний
            sendW[1] = 0x01
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # pwr mgmt2 addr
            sendW[0] = 0x6C
            sendW[1] = 0x00
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()
            pyb.delay(400)

            # int addr, отключить все прерывания
            sendW[0] = 0x38
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # fifo addr, отключить все fifo
            sendW[0] = 0x23
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # pwr mgmt1 addr, включить внутренний источник синхронизации
            sendW[0] = 0x6B
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # i2c включить адрес, отключить мастер i2c
            sendW[0] = 0x24
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # пользовательский контроль addr, отключение режимов i2c и fifo
            sendW[0] = 0x6A
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # Сброс fifo and dmp
            sendW[1] = 0x0C
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            pyb.delay(100)

            # config addr, установить фильтр низких частот 188 Гц
            sendW[0] = 0x1A
            sendW[1] = 0x01
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # делитель частоты дискретизации addr, set 1khz
            sendW[0] = 0x19
            sendW[1] = 0x00
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # gyro cfg addr, максимальная чувствительность
            sendW[0] = 0x1B
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # accel cfg addr, mаксимальная чувствительность
            sendW[0] = 0x1C
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            gyroSense = 131  # LSB,deg,sec
            accelSense = 16384  # LSB,g

            # user control addr, отключить i2c режимы and fifo
            # включить fifo
            sendW[0] = 0x6A
            sendW[1] = 0x40
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            print('\nНакопление 40 образцов...')
            # user control addr, enable fifo
            sendW[0] = 0x6A
            sendW[1] = 0x40
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # fifo addr, включаем gyro + accel fifo
            sendW[0] = 0x23
            sendW[1] = 0x78
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            # накапливать 40 сэмплов за 40 миллисекунд, 480 байт
            pyb.delay(40)

            # fifo addr, выключаем gyro + accel fifo
            sendW[0] = 0x23
            sendW[1] = 0x00
            cs_spi[0].low()
            spi.send(sendW)
            cs_spi[0].high()

            print('Готово, накоплено 40 сэмплов!')
            # fifo hi-count addr, read fifo
            sendR[0] = 0x72 | 0x80
            cs_spi[0].low()
            for i in range(2):
            # spi.send(0x00)
            # spi.recv(recvRs) -  ff. errors so 'recvRo' временный контейнер
                spi.send_recv(sendR, recvRo)
                recvRs = recvRo[0]
                cs_spi[0].high()

            fifo_cnt = recvRs[0] << 8 | recvRs[1]
            packet_cnt = fifo_cnt / 12

            print('\n--Raw result of samples--')
            print('fifo cnt: ', fifo_cnt)
            print('packet cnt: ', packet_cnt, '\n')

            temp = bytearray(2)
            # whoami
            sendW[0] = 0x75 | 0x80
            sendW[1] = 0x00
            cs_spi[0].low()
            spi.send(sendW)
            spi.recv(temp)
            cs_spi[0].high()
            print('\nWho am I dev1: ', temp, ', I should be.with_traceback() 0x71 -> 113 or 0x68 -> 104\n')

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
########################################################################################################################
############################################### Работа с Ethernet ######################################################
########################################################################################################################
    def getEthernet_ifaces(self):
        import netifaces
        from get_nic import getnic
        import pprint
        try:
            print('СПИСОК СЕТЕВЫХ ИНТЕРФЕЙСОВ ОПРЕДЕЛЕННЫХ В ОС: \n')
            print('--------------------------------')
            pprint.pprint(getnic.interfaces())
            print('--------------------------------')
            print('СПИСОК ПАРАМЕТРОВ СЕТЕВЫХ ИНТЕРФЕЙСОВ В ВИДЕ ВЛОЖЕННОГО МНОГОМЕРНОГО АССОЦИАТИВНОГО МАССИВА: \n')
            pprint.pprint(getnic.ipaddr(getnic.interfaces()))
            gws = netifaces.gateways()
            for i in getnic.interfaces():
                addrs = netifaces.ifaddresses(i)
                print(addrs)
            #print(addrs[netifaces.AF_INET])
                #

            print()
            # for g in gws:

            try:
                print('Шлюз:' + str(gws['default'][netifaces.AF_INET][0]) + ' для сетевого интерфейса: ' + str(gws['default'][netifaces.AF_INET][1]) )
            except BaseException as be:
                print('Возникла ошибка определения сетевого интерфейса с кодом ошибки: ' + str(be.with_traceback()))
            print('--------------------------------')
            #os.popen("route -n get default | grep 'gateway' | awk '{print $2}'")

            with open('dns.txt', 'w') as f:
                dns = os.popen('cat /etc/resolv.conf').read()
                print('Записи, соответствующие настройкам DNS:\n ' +  dns)


            #ifaces4mtu = os.popen('cat /sys/class/net/*').read()
            mtu = os.popen('cat /sys/class/net/*/mtu').read()
            print('MTU:\n' + mtu)

            return getnic.interfaces()
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1

    def time_rec(self):
        try:
            os.system('sudo -S setfacl -m g:sudo:r /dev/rtc')
            os.system('modprobe.with_traceback() i2c-bcm2835')
            os.system('modprobe.with_traceback() rtc-ds1307')
            # при повторном вызове предидущей строки может возникать IOError
            #os.system('echo ds1307 0x68 > /sys/class/i2c-adapter/i2c-1/new_device')

            #os.system('/sbin/hwclock -r')
            ct = os.popen('/sbin/hwclock -r').read()[:-14] # 2020-05-28 18:53:06.690236+03:00
            print (ct)
            ctt=os.popen('sudo timedatectl set-time \''+ct+'\'').read()
            print(ctt)
            print('-----------------------------------')
            #print(' ТЕКУЩЕЕ АППАРАТНОЕ ВРЕМЯ: ' + self.t1)
            print('-----------------------------------')
            return self.t1

        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1


########################################################################################################################
####################################### РАБОТА c sysfs. Сбор параметров мониторинга ####################################
########################################################################################################################
"""
Упрощенный интерфейс Python SysFS. 
"""
# @ ToDo TEST IT !
__all__ = ['sys', 'Node']

from os import listdir
from os.path import isdir, isfile, join, realpath, basename


class Node(object):
    __slots__ = ['_path_', '__dict__']

    ########################################################################################################################
    def __init__(self, path='/sys'):
        try:
            self._path_ = realpath(path)
            if not self._path_.startswith('/sys/') and not '/sys' == self._path_:
                raise RuntimeError('Using this on non-sysfs files is dangerous!')

            self.__dict__.update(dict.fromkeys(listdir(self._path_)))
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    ########################################################################################################################
    def __repr__(self):
        return '<sysfs.Node "%s">' % self._path_

    ########################################################################################################################

    def __str__(self):
        return basename(self._path_)

    ########################################################################################################################
    def __setattr__(self, name, val):
        try:
            if name.startswith('_'):
                return object.__setattr__(self, name, val)

            path = realpath(join(self._path_, name))
            if isfile(path):
                with open(path, 'w') as fp:
                    fp.write(val)
            else:
                raise RuntimeError('Cannot write to non-files.')
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    ########################################################################################################################

    def __getattribute__(self, name):
        try:
            if name.startswith('_'):
                return object.__getattribute__(self, name)

            path = realpath(join(self._path_, name))
            if isfile(path):
                with open(path, 'r') as fp:
                    return fp.read().strip()
            elif isdir(path):
                return Node(path)
        except Exception as be:
            print("\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be.with_traceback())))
            print("\033[30m {}".format(""))
            return -1
    ########################################################################################################################

    def __setitem__(self, name, val):
        return setattr(self, name, val)

    def __getitem__(self, name):
        return getattr(self, name)

########################################################################################################################
    def __iter__(self):
        return iter(getattr(self, name) for name in listdir(self._path_))
########################################################################################################################
################################################# Запуск программы #####################################################
########################################################################################################################

if __name__ == '__main__':
    try:
        if not os.geteuid() == 0:
            sys.exit("\nOnly root can run this script\n")

        print()
        print()
        print(current_time() +' Старт программы агента системы мониторинга...')
        ########################################################################################################################
        # Создаем объект Агента мониторинга
        Agent_object = AgentMS()
        # Agent_object.time_rec() # Запись времени
        Agent_object.loop_counter = 1
        # тестирование функции передачи потока в сокет UDS в отдельном потоке:




        #senderUDP_thread = (Thread(target=Agent_object.send_HexInt_UDP, args = ([False,'192.168.99.2','20001',hexlist])))
        #senderUDP_thread = (Thread(target=Agent_object.send_HexInt_UDP, args = ([False,'127.0.0.1','999',hexlist])))
        #senderUDP_thread.setName("UDP SENDER\'S THREAD:")
        #senderUDP_thread.start()

        receiverUDP_thread = (Thread(target=Agent_object.UDP_receiver, args = ([33333,''])))
        receiverUDP_thread.setName("UDP RECEIVER\'S THREAD:")
        receiverUDP_thread.start()

        # senderUDS_thread = (Thread(target=Agent_object.uds_sender, args = ([False, 'message to send', '/tmp/uds_socket'])))
        # senderUDS_thread.setName("UDS SENDER\'S THREAD:")
        # senderUDS_thread.start()
        # ----------------------------------- TESTING IS DONE !!! ----------------------------------------
        ########################################################################################################################
        # Создаем поток подпрограммы для получения информации через pipe
        # Данный поток будет обрабатывать/парсить информацию возможно появление @ToDo отдельных потоковых функций обработки
        # pipeReceiver_thread = (Thread(target=Agent_object.pipe_receiver, args=([Agent_object.fifoname])))
        # pipeReceiver_thread.setName("PIPE RECEIVER\'s THREAD")
        # pipeReceiver_thread.start()
        # ТЕСТИРУЕМ метод uds_sender(self, uds_message, uds_address):
        # Для реализации метода uds_sender(self, uds_message, uds_address)
        # необходимо существование файла UDS-сокета, по пути, указанному в параметре uds_address
        # Если UDS-сервер не запущен, получим ошибку "[Errno 111] Connection refused"
        # Поэтому UDS-сервер необходимо запустить в отдельном потоке, ждущем подключение UDS клиента
        # Создаем поток подпрограммы для получения информации через UDS сокет
        # Данный поток будет обрабатывать/парсить информацию возможно появление @ToDo отдельных потоковых функций обработки
        # receiverUDS_thread = Thread(target=Agent_object.uds_receiver, args=(['/tmp/uds_socket']))
        # receiverUDS_thread.setName("UDS RECEIVER\'S THREAD:")
        # receiverUDS_thread.start()

        while True:
            # Меняем цвет фона терминала и шрифта в зависимости от четности итерации ,бесконечного цикла опроса
            setTerm(Agent_object.loop_counter)
            print(current_time())
            hexlist = list()
            tempbytes = bytes(range(101))
            for value in tempbytes:
                hexlist.append("0x" + tempbytes[value:value + 1].hex())
            #print(hexlist)
            Agent_object.send_HexInt_UDP(False,'192.168.99.2','20001',hexlist)
            Agent_object.getSoftware_version()  # TEST OK!
            #print('Вывод переменных агента:')
            #print(Agent_object.p1) # Имя релиза
            #print(Agent_object.p2) # Кодовое имя релиза
            #print(str( Agent_object.p3)) # int Номер релиза
            #print(Agent_object.p4) # Версия ядра ОС
            #print(Agent_object.p5) #Тип архитектуры # TEST OK!
            print('-----------------------------------')
            #Agent_object.getCPU_info()  # TEST OK!
            Agent_object.getCPU_percent()  # TEST OK!
            #print('-----------------------------------')
            #print(Agent_object.u1_1) # Загрузка ядра процессора 1 # TEST OK!
            #print(Agent_object.u1_2) # Загрузка ядра процессора 2 # TEST OK!
            #print(Agent_object.u1_3) # Загрузка ядра процессора 3 # TEST OK!
            #print(Agent_object.u1_4) # Загрузка ядра процессора 4 # TEST OK!
            #print(Agent_object.u2_1) # Частота ядра процессора 1 # TEST OK!
            #print(Agent_object.u2_2) # Частота ядра процессора 2 # TEST OK!
            #print(Agent_object.u2_3) # Частота ядра процессора 3 # TEST OK!
            #print(Agent_object.u2_4) # Частота ядра процессора 4 # TEST OK!
            #print('-----------------------------------')
            Agent_object.getMeasure_temp('core')# TEST OK!
            print('-----------------------------------')
            #
            #Agent_object.getMeasure_volts('core') # TEST OK!
            #print('-----------------------------------')
            #
            #Agent_object.get_ProcInfo()  # TEST OK!
            #print('-----------------------------------')
            #
            Agent_object.getRAM() #TEST OK!
            print('-----------------------------------')
            #
            Agent_object.getMem_arm() #TEST OK!
            print('-----------------------------------')
            #
            listOfNetIfaces = Agent_object.getEthernet_ifaces() # TEST OK !
            print('-----------------------------------')

            Agent_object.readProcfsData('eth_info', listOfNetIfaces[2])  # TEST OK !
            Agent_object.readProcfsData('eth_info', listOfNetIfaces[1])  # TEST OK !
            Agent_object.readProcfsData('eth_info', listOfNetIfaces[0])  # TEST OK !
            Agent_object.readProcfsData('udp_info', 'wlan0')  # TEST OK !
            print('-----------------------------------')

            # ТЕСТИРУЕМ метод readProcfsData()n3.8n
            #Agent_object.readProcfsData('all_params', 'wlan0')  # TEST OK !
            #Agent_object.readProcfsData('loadavg', 'wlan0')  # TEST OK !
            #Agent_object.readProcfsData('mem_free_info','wlan0') # TEST OK !
            #print('-----------------------------------')
            #Agent_object.readProcfsData('abracaddabra','wlan0') # TEST FAKE data OK !
            #print('-----------------------------------')

            Agent_object.getRTC_time() # TEST OK !
            print('-----------------------------------')

            Agent_object.getDisk_usage() # TEST OK !
            print('-----------------------------------')

            Agent_object.getDiskCapacity() # TEST OK !
            print('-----------------------------------')

            Agent_object.getSdcard_info() # TEST OK !
            print('-----------------------------------')

            #Agent_object.i2cReadByteData(busNum=1)
            #print('-----------------------------------')

            #Agent_object.find_I2C_BusNUM()
            #print('-----------------------------------')

            #Agent_object.getI2C_baudrate()
            #print('-----------------------------------')

            #Agent_object.defineRTC_device()
            #print('-----------------------------------')

            Agent_object.I2C_scan(1)
            print('-----------------------------------')

            uarts = Agent_object.listOfUART_ifaces() # TEST OK !
            for uart in uarts: Agent_object.getUART_iface_info(uart) # TEST OK !

            #for spidev in Agent_object.getList_SPI_devs():
            #    Agent_object.spi_test(spidev) #TEST OK !

            #for spidev in Agent_object.getList_SPI_devs():
            #     Agent_object.cspidev_test(spidev) # TEST OK !
            #print('----------------------------------')

            #Agent_object.get_otp_dump() #TEST OK!
            #print('-----------------------------------')

            #Agent_object.getThrottled()  # TEST OK!
            #print('-----------------------------------')

            #Agent_object.get_Camera() #TEST OK!
            #Agent_object.spi_test_(0)
            #print('-----------------------------------')

            #Agent_object.MPU6050_alive_()
            #print('-----------------------------------')

            #Agent_object.getAll_info_by_vcgencmd() # TEST OK!
            #print('-----------------------------------')

            #Agent_object.testTransmitUART()
            #print('-----------------------------------')

            #Agent_object.writeUART('/dev/ttyAMA0', '9600', 10, 'Hello be.with_traceback()autiful world !')
            #Agent_object.readUART('/dev/ttyAMA0', '9600', 10)
            #print('-----------------------------------')

            #Agent_object.getRing_osc() #TEST OK!
            #print(Agent_object.o1)#TEST OK!
            #print(Agent_object.o2)#TEST OK!
            #print(Agent_object.o3)#TEST OK!
            #print(Agent_object.o4)#TEST OK!


            #Agent_object.getFrequency_Sources() # TEST OK!
            #print('-----------------------------------')



            # ----------------------------------- TESTING IS DONE !!! ----------------------------------------
            ########################################################################################################################
            # Возможно появление @ToDo отдельных потоковых функций обработки:
            # uds_receiver_handler_thread = Thread(target=agent.uds_receiver_handler(), args=(['someInputUDSInfo']))
            # ----------------------------------- TESTING IN PROGRESS !!! -----------------------------------
            # тестирование функции передачи потока в сокет UDS:
            #Agent_object.uds_sender(True, 'message to send', '/tmp/uds_socket') #
            #Agent_object.uds_sender(True, 'message to send', '/tmp/uds_socket') #
            #Agent_object.uds_sender(True, 'message to send', '/tmp/uds_socket') # @ToDo !

            # ----------------------------------- TESTING IS DONE !!! ----------------------------------------
            ########################################################################################################################
            Agent_object.loop_counter+=1
            if Agent_object.loop_counter == 9: Agent_object.loop_counter=1; # Сбрасываем счетчик во избежания переполнения
            time.sleep(1)
            print('########################################################################################################################')

    except Exception as be:
        print(current_time() + "\033[31m {}".format('Возникла ошибка в программе:' + "\033[31m {}".format(be)))
        print("\033[30m {}".format(""))
        sys.exit(-1)
########################################################################################################################



