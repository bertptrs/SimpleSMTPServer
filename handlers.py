import socket
import socketserver

from util import eprint, lookahead


class SMTPHandler(socketserver.StreamRequestHandler):

    def handle(self):
        eprint("recieved request")
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
            else:
                eprint("Unknown: ", *command)
                self.write_output(502, "Error: command not recognized.")


    def write_output(self, *args, sep=" "):
        message = sep.join(str(x) for x in args)
        eprint("Returning message: ", message)

        message += "\r\n"

        self.wfile.write(message.encode("ascii"))


    def handle_ehlo(self, command):
        eprint("Recieved EHLO from ", command[1])
        ehlo_mesg = [
                (socket.gethostname(), None),
                ("SIZE", 10240000),
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
        eprint("Incoming mail from '%s'" % self.mail_from)

        self.send_ok()


    def handle_rcpt(self, command):
        recipient = command[1][4:-1]
        eprint("Added recipient '%s'" % recipient)

        self.recipients.append(recipient)

        self.send_ok()


    def handle_data(self, command):
        pass


    def send_ok(self):
        self.write_output(250, "Ok")


