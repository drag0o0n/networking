from operator import itemgetter             # for sorting a list of tuples
from socket import *
import csv


serverPort = 5000                           # initiate port #5000
# AF_INET use ipv4, SOCK_STREAM use  TCP
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))         # bind python with actual socket
serverSocket.listen(1)                      # waitting
print('The server is ready to receive')

# list for  SmartPhone names and prices
smartPhones = []
ERRFlag = 0                                           # used for error detection

# -------------------------------------------------------------------------------------------------------------------
# response http/css/png/jpg file through TCP connection________________________________________________________


def responsePage(fileType, addr):
    try:
        # open the file in binary format for reading
        file = open(fileType, "rb")
    except (IOError, FileNotFoundError):                           # if file could not be opened
        print('I/O exception2')
        PageError(addr)
    else:
        dotLocation = fileType.index('.')
        extension = fileType[dotLocation+1:]
        # # indicates that the request has succeeded
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
        if extension == "html":
            connectionSocket.send(
                "Content-Type: text/html \r\n".encode())  # html file
        elif extension == "css":
            connectionSocket.send(
                "Content-Type: text/css \r\n".encode())   # css file
        elif extension == "jpg":
            connectionSocket.send(
                "Content-Type: image/jpg \r\n".encode())  # jpg file
        else:
            connectionSocket.send(
                "Content-Type: image/png \r\n".encode())  # png file

        connectionSocket.send("\r\n".encode())
        # read the file
        content = file.read()
        # send file
        connectionSocket.send(content)


# ---------------------------------------------------------------------------------------------------------
# opening phones file and reading phone names and prices_______________________________________________
def openCSVFile():
    # empty list of phones
    smartPhones.clear()
    try:

        with open("smartphone.csv") as csv_file:
            # csv file with ',' delimiter
            csv_reader = csv.reader(csv_file, delimiter=',')

            for row in csv_reader:
                # save info as tuples of (name, price)
                smartPhones.append((row[0], float(row[1])))

    except (IOError, FileNotFoundError):
        print('I/O exception')
        global ERRFlag
        ERRFlag = 1                                         # if theres an  flag = 1

# -----------------------------------------------------------------------------------------------------------------
# send http file


def tableFile(typesort):
    connectionSocket.send("HTTP/1.1 200 OK\r\n".encode()
                          )           # file was found
    # file of type html
    connectionSocket.send("Content-Type: text/html \r\n".encode())
    # end header
    connectionSocket.send("\r\n".encode())

    # send html file containing the phones and prices
    if typesort == 1:
        # complement file html
        connectionSocket.send(
            f"<h1  style= ""color:white; "" >sort by Price</h1>".encode())
    else:
        connectionSocket.send(
            f"<h1 style= ""color:white;"">sort by Name</h1>".encode())
    # html  table
    f1 = open("table.TXT", "rt")
    connectionSocket.send(f1.read().encode())

    # send tuples of (name, price) one by one
    for row in smartPhones:
        connectionSocket.send(
            f"<tr> <td>{row[0]}</td> <td>{row[1]}</td></tr>".encode())

    # complement file html
    connectionSocket.send(f"</table>    </body>  </html>".encode())

# ---------------------------------------------------------------------------------------------------------------------
# send http error page through TCP connection______________________________________________________________


def PageError(addr):
    # Error ==> send  not found
    connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
    # type file -> html
    connectionSocket.send("Content-Type: text/html \r\n".encode())
    # end header
    connectionSocket.send("\r\n".encode())

    f = open("error.txt", "rt")
    connectionSocket.send(f.read().encode())
    # send IP address and Port
    connectionSocket.send(
        f" <br><br>IP: {addr[0]} <br> port: {addr[1]} ".encode())
    connectionSocket.send("</body> </html>".encode())

# -----------------------------------------------------------------------------------------------------------------


while True:
    # accept handshake
    connectionSocket, addr = serverSocket.accept()
    sentence = connectionSocket.recv(1024).decode()
    print(sentence)
    # extracting request type from request
    names = sentence.split('\n')
    filename = names[0].split()[1]  # name file request with /
    fileType = filename.lstrip('/')  # remove the / on the left of the string

    # carry out the request
    if fileType.lower() == "sortname":  # __________________________________________________________
        openCSVFile()
        if ERRFlag == 0:
            smartPhones = sorted(
                smartPhones, key=itemgetter(0))  # sort by name
            tableFile(0)
        else:
            ERRFlag = 0
            # send Error page html
            PageError(addr)

    elif fileType.lower() == "sortprice":  # _______________________________________________________
        openCSVFile()
        if ERRFlag == 0:
            smartPhones = sorted(
                smartPhones, key=itemgetter(1))  # sort by Price
            tableFile(1)
        else:
            ERRFlag = 0
            PageError(addr)  # send Error page html

    elif fileType.lower() == "":  # ____________________________________________________
        responsePage("index.html", addr)

    elif fileType.lower().__contains__(".png"):  # __________________________________________________
        responsePage(fileType, addr)

    elif fileType.lower().__contains__(".jpg"):  # __________________________________________________
        responsePage(fileType, addr)

    elif fileType.lower().__contains__(".css"):  # __________________________________________________
        responsePage(fileType, addr)

    elif fileType.lower().__contains__(".html"):  # __________________________________________________
        responsePage(fileType, addr)
    else:  # ________________________________________________________________________________________
        PageError(addr)

    # close TCP connection
    connectionSocket.close()
