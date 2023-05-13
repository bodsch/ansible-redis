# python 3 headers, required if submitting to Ansible

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
      ansible filter
    """

    def filters(self):
        return {
            'network_bind': self.network_bind
        }

    def network_bind(self, data):
        """
        """
        result = []

        if (isinstance(data, str)):
            result.append(data)

        if (isinstance(data, list)):
            result = data

        display.v(f"return : {result}")
        return result
