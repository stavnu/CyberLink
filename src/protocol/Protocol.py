def recvall(sock, b_count):
    buf = b''
    while b_count:
        newbuf = sock.recv(b_count)
        if not newbuf:
            return None
        buf += newbuf
        b_count -= len(newbuf)
    return buf
