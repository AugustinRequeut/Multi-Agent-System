#!/usr/bin/env python3

from enum import Enum


class MessagePerformative(Enum):
    """MessagePerformative enum class.
    Enumeration containing the possible message performative.
    """
    CFP = 101 # Call for proposal
    PROPOSE = 102 # I am interested
    ACCEPT_PROPOSAL = 103 # I choose you as a partner
    INFORM = 104 # I have arrived

    def __str__(self):
        """Returns the name of the enum item.
        """
        return '{0}'.format(self.name)
