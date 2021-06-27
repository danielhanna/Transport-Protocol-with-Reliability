import sys
import getopt
import Checksum
import BasicSender
'''
The UDP Reliable Transport protocol
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False):
        super(Sender, self).__init__(dest, port, filename, debug)

    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            pass
            #print("recv: %s" % response_packet) ############Removing output
        else:
            pass
            #print("recv: %s <--- CHECKSUM FAILED" % response_packet) ############Removing output
    # Main sending loop.
    def start(self):
        #Build Packets##################
        seqno = 0
        msg_raw = self.infile.read(1400)
        msg_type = None
        try:
            msg = msg_raw.decode()
        except UnicodeDecodeError:
            msg = str(msg_raw)

        while not msg_type == 'end':
            msg_raw_next = self.infile.read(1400)
            try:
                next_msg = msg_raw_next.decode()
                msg_type = 'data'
                if seqno == 0:
                    msg_type = 'start'
                elif next_msg == "":
                    msg_type = 'end'
            except UnicodeDecodeError:
                next_msg = str(msg_raw_next)
                msg_type = 'data'
                if seqno == 0:
                    msg_type = 'start'
                elif next_msg == "":
                    msg_type = 'end'

            #Make packet####################
            packet = self.make_packet(msg_type,seqno,msg)

            ####### My Functions ############################
            def split_return_packet(resp_str):
                pieces = resp_str.split('|')  # Seperates each element
                msg_type, seqno = pieces[0:2]  # first two elements always treated as msg type and seqno
                return seqno
            #I. Wait for a packet
            waiting = True
            wait_time = 0.0
            while waiting is True:
                response = self.receive(.500) ##wait for a response
                wait_time = wait_time + .500
                #If you have a response decode it. ##################
                if response != None: #Begin checking condition if no response from server
                    resp_str = response.decode()
                    self.handle_response(resp_str)
                    next_seqno = seqno + 1
                    getAck = split_return_packet(resp_str)
                    last_ack_received = int(getAck)
                    packet_checksum_validity = Checksum.validate_checksum(resp_str)
                    if packet_checksum_validity == True:
                        waiting = False
                        pass
                    else:
                        #ignore
                        waiting = True
                        continue
                    # 3. duplication ######################################################
                    #if duplication not True:
                    if last_ack_received != next_seqno: #Then this is a duplicate ack
                        waiting = True
                        continue #Start listening again (dont't send another packet)
                    elif last_ack_received == next_seqno:
                        waiting = False
                        continue #Start listening again (dont't send another packet)
                    else:
                        pass

                else: # No Repsonse  or elif packet_checksum_validity == False:
                    # 4. delay #############################################################
                    if wait_time >= 25:
                        sys.exit()
                    else:
                        self.send(packet.encode('utf-8'))  ##############Sending Packet Again
            ##### your code ends here ... #####
            msg = next_msg
            seqno += 1
        self.infile.close()
'''
U of A Code for Sender
'''
if __name__ == "__main__":
    def usage():
        print("BEARDOWN-TP Sender")
        print("-f FILE | --file=FILE The file to transfer; if empty reads from STDIN")
        print("-p PORT | --port=PORT The destination port, defaults to 33122")
        print("-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost")
        print("-d | --debug Print debug messages")
        print("-h | --help Print this usage message")

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:d", ["file=", "port=", "address=", "debug="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True

    s = Sender(dest,port,filename,debug)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()

#param_url = input("Enter a URL:  ")
#param_file = input("Enter a file name: ")

#Notes:
#python sender.py -f <input file> -a <destination adddress> -p <port>
#   python sender.py -f files/test.html -a localhost -p 33122
#   python sender.py -f files/test.html -a localhost -p 33122