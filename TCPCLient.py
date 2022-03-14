from socket import *
from re import match

# --------------------
# Constants
# --------------------
# The states that the application can be in
states = [
    "disconnected",  # Connection to a chat server is not established
    "connected",     # Connected to a chat server, but not authorized (not logged in)
    "authorized"     # Connected and authorized (logged in)
]

TCP_PORT = 1300                # TCP port used for communication
SERVER_HOST = "datakomm.work"  # Set this to either hostname (domain) or IP address of the chat server

# --------------------
# State variables
# --------------------
current_state = "disconnected"  # The current state of the system
must_run = True                 # When this variable will be set to false, the application will stop

# Use this variable to create socket connection to the chat server
# Note: the "type: socket" is a hint to PyCharm about the type of values we will assign to the variable
client_socket = None  # type: socket


def quit_application():
    """ Update the application state so that the main-loop will exit """
    global must_run
    must_run = False


def send_command(command, arguments):
    """
    Send one command to the chat server.
    :param command: The command to send (login, sync, msg, ...(
    :param arguments: The arguments for the command as a string, or None if no arguments are needed
        (username, message text, etc)
    :return:
    """
    global client_socket
    if arguments == None: arguments=''
    msg=command+' '+arguments+'\n'
    try:
        client_socket.send(msg.encode())
    except error as e:
        print("Error: ", e)


def read_one_line(sock):
    """
    Read one line of text from a socket
    :param sock: The socket to read from.
    :return:
    """
    newline_received = False
    message = ""
    while not newline_received:
        character = sock.recv(1).decode()
        if character == '\n':
            newline_received = True
        elif character == '\r':
            pass
        else:
            message += character
    return message


def get_servers_response():
    """
    Wait until a response command is received from the server
    :return: The response of the server, the whole line as a single string
    """
    global client_socket
    return read_one_line(client_socket)


def connect_to_server():
    global client_socket
    global current_state

    client_socket=socket(AF_INET,SOCK_STREAM)
    try:
        client_socket.connect((SERVER_HOST,TCP_PORT))
    except error as e:
        print("Error: ", e)
        return
    else:
        current_state = "connected"
    
    send_command('sync',None)

    response=get_servers_response()
    if response == 'modeok':
        print("Mode changed to SYNC!")
    else:
        print("Failed to changed mode!")


def disconnect_from_server():
    global client_socket
    global current_state
    
    try:
        client_socket.close()
    except error as e:
        print("Error: ", e)
        return
    else:
        current_state = "disconnected"


def login():
    global current_state
    usr=input("Enter username: ")
    send_command('login', usr)
    response=get_servers_response()
    if response != 'loginok':
        print(response)
        return  
    print("Login successful!")
    current_state="authorized"


def public_message():
    msg=input("Enter message: ")
    send_command('msg', msg)
    response=get_servers_response()
    if not match('^msgok [0-9]*\w*',response): #returns matched object if found or None if not
        print(response)
    else:
        print("Message sent successful!")


def connected_users():
    send_command('users',None)
    response=get_servers_response()
    usr=response.split()[1:]
    print("Logged users:")
    for i in range(len(usr)): print(' {}) {}'.format(i+1,usr[i]))


def private_message():
    usr=input("Enter user: ")
    msg=input("Message: ")
    if usr == "": 
        print("Recipent does not exist")
        return 
    if msg == "":
        print("Empty message")
        return
    send_command('privmsg',usr+' '+msg)
    response=get_servers_response()
    if not match('^msgok [0-9]*\w*',response):
        print(response)
    else:
        print("Message sent successful!")


def print_inbox():
    global client_socket
    send_command('inbox',None)
    number_of_msg_in_inbox=int(get_servers_response().split()[1])
    print("You have {} messages in the inbox.\n".format(number_of_msg_in_inbox))

    if number_of_msg_in_inbox == 0: return

    message=""
    while True:
        character = client_socket.recv(1).decode()
        if character == '\n':
            number_of_msg_in_inbox-=1
            if number_of_msg_in_inbox<=0: break
            message += ';'
        elif character == '\r':
            pass
        else:
            message += character
    message=message.split(';')

    private=[]
    public=[]
    for msg in message:
        tmp=msg.split()
        if tmp[0] == 'privmsg': private.append((tmp[1],' '.join(tmp[2:])))
        else: public.append((tmp[1],' '.join(tmp[2:])))
    
    if len(private)>0:
        print("Private messages")
        for i in private: print("Sender: {}\tMessage: {}".format(i[0],i[1]))

    if len(public)>0:
        print("\nPublic messages")
        for i in public: print("Sender: {}\tMessage: {}".format(i[0],i[1]))
    

def get_joke():
    send_command('joke',None)
    response=get_servers_response().split()[1:]
    print(' '.join(response))
    

"""
The list of available actions that the user can perform
Each action is a dictionary with the following fields:
description: a textual description of the action
valid_states: a list specifying in which states this action is available
function: a function to call when the user chooses this particular action. The functions must be defined before
            the definition of this variable
"""
available_actions = [
    {
        "description": "Connect to a chat server",
        "valid_states": ["disconnected"],
        "function": connect_to_server
    },
    {
        "description": "Disconnect from the server",
        "valid_states": ["connected", "authorized"],
        "function": disconnect_from_server
    },
    {
        "description": "Authorize (log in)",
        "valid_states": ["connected", "authorized"],
        "function": login
    },
    {
        "description": "Send a public message",
        "valid_states": ["connected", "authorized"],
        "function": public_message
    },
    {
        "description": "Send a private message",
        "valid_states": ["authorized"],
        "function": private_message
    },
    {
        "description": "Read messages in the inbox",
        "valid_states": ["connected", "authorized"],
        "function": print_inbox
    },
    {
        "description": "See list of users",
        "valid_states": ["connected", "authorized"],
        "function": connected_users
    },
    {
        "description": "Get a joke",
        "valid_states": ["connected", "authorized"],
        "function": get_joke
    },
    {
        "description": "Quit the application",
        "valid_states": ["disconnected", "connected", "authorized"],
        "function": quit_application
    },
]


def run_chat_client():
    """ Run the chat client application loop. When this function exists, the application will stop """
    while must_run:
        print_menu()
        action = select_user_action()
        perform_user_action(action)
    print("Thanks for watching. Like and subscribe! 👍")


def print_menu():
    """ Print the menu showing the available options """
    print("==============================================")
    print("What do you want to do now? ")
    print("==============================================")
    print("Available options:")
    i = 1
    for a in available_actions:
        if current_state in a["valid_states"]:
            print("  %i) %s" % (i, a["description"]))
        i += 1
    print()


def select_user_action():
    """
    Ask the user to choose and action by entering the index of the action
    :return: The action as an index in available_actions array or None if the input was invalid
    """
    number_of_actions = len(available_actions)
    hint = "Enter the number of your choice (1..%i):" % number_of_actions
    choice = input(hint)

    try:
        choice_int = int(choice)
    except ValueError:
        choice_int = -1

    if 1 <= choice_int <= number_of_actions:
        action = choice_int - 1
    else:
        action = None

    return action


def perform_user_action(action_index):
    """
    Perform the desired user action
    :param action_index: The index in available_actions array - the action to take
    :return: Desired state change as a string, None if no state change is needed
    """
    if action_index is not None:
        print()
        action = available_actions[action_index]
        if current_state in action["valid_states"]:
            function_to_run = available_actions[action_index]["function"]
            if function_to_run is not None:
                function_to_run()
            else:
                print("Internal error: NOT IMPLEMENTED (no function assigned for the action)!")
        else:
            print("This function is not allowed in the current system state (%s)" % current_state)
    else:
        print("Invalid input, please choose a valid action")
    print()
    return None


if __name__ == '__main__':
    run_chat_client()