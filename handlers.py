import socket
import socketserver

from util import eprint, lookahead


class SMTPHandler(socketserver.StreamRequestHandler):

    def setup(self):
        super(SMTPHandler, self).setup()
        self.reset_state()


    def reset_state(self):
        self.recipients = []
        self.mail_from = None


    def handle(self):
        self.write_output(220, socket.gethostname(), "SimpleSMTPServer, how you doin'?")
        for line in self.rfile:
            command = line.decode("ascii").strip().split(" ")

            action = command[0].upper()

            if action == "QUIT":
                self.write_output(221, "Bye")
                break
            elif action == "MAIL":
                self.handle_mail(command)
            elif action == "EHLO":
                self.handle_ehlo(command)
            elif action == "RCPT":
                self.handle_rcpt(command)
            elif action == "DATA":
                self.handle_data(command)
            else:
                eprint("Unknown: ", *command)
                self.write_output(502, "Error: command not recognized.")


    def write_output(self, *args, sep=" "):
        message = sep.join(str(x) for x in args)
        message += "\r\n"

        self.wfile.write(message.encode("ascii"))


    def handle_ehlo(self, command):
        # Verify hostname
        try:
            peer_ip, peer_port = self.request.getpeername()

            _, _, valid_ips = socket.gethostbyname_ex(command[1])
            if peer_ip not in valid_ips:
                eprint("Warning: %s does not resolve to %s" % (command[1], peer_ip))
        except socket.error:
            eprint("Warning: unable to resolve peer name", command[1])


        # Construct EHLO messages
        ehlo_mesg = [
                (socket.gethostname(), None),
                ("SIZE", 10 * (1 << 30)), # 10MB should be enough for everyone
                ]

        for entry, last in lookahead(ehlo_mesg):
            if last:
                msg = "250 "
            else:
                msg = "250-"

            key, value = entry

            msg += str(key)
            if value is not None:
                msg += " " + str(value)

            self.write_output(msg)


    def handle_mail(self, command):
        self.mail_from = command[1][6:-1]
        self.recipients = []

        self.send_ok()


    def handle_rcpt(self, command):
        recipient = command[1][4:-1]

        self.recipients.append(recipient)

        self.send_ok()


    def handle_data(self, command):
        if self.mail_from is None:
            self.write_output(503, "No MAIL command")
            return
        elif not self.recipients:
            self.write_output(503, "No recipients specified")
            return

        self.write_output(354, "Go ahead, send message")
        message = ""

        prev = None
        crlf = "\r\n"
        for line in self.rfile:
            line = line.decode("ascii")

            if prev == crlf and line == "." + crlf:
                break
            elif prev is not None:
                message += prev
            prev = line


        self.send_ok()
        params = (
                self.mail_from,
                "' and '".join(self.recipients),
                message
                )
        eprint("Recieved message from '%s' to '%s':\n%s" % params)

        self.reset_state()


    def send_ok(self):
        self.write_output(250, "Ok")


