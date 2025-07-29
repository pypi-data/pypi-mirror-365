
# heartbreak_code/passing_notes.py

import collections

class PassingNotes:
    """
    'Passing Notes': A Distributed Message Queue System.
    Implements a native system for asynchronous, inter-process communication
    based on a message queue pattern.
    """
    def __init__(self):
        self.channels = collections.defaultdict(collections.deque)

    def pass_note(self, channel_name, message):
        """
        Sends a message to a named channel.
        """
        print(f"Passing note '{message}' to channel '{channel_name}'")
        self.channels[channel_name].append(message)

    def listen_for_note(self, channel_name):
        """
        Listens for and retrieves a message from a named channel.
        Returns None if no message is available.
        """
        if self.channels[channel_name]:
            message = self.channels[channel_name].popleft()
            print(f"Received note '{message}' from channel '{channel_name}'")
            return message
        else:
            print(f"No notes in channel '{channel_name}'")
            return None

    def get_channel_status(self, channel_name):
        """
        Returns the number of messages currently in a channel.
        """
        return len(self.channels[channel_name])

