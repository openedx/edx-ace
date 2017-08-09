class AutomatedCommunicationEngine(object):
    def send(self, msg):
        # for now, the following calls are all made synchronously in the same process
        # TODO 1. send to all registered policies
        # TODO 2. send to configured presentation layer
        # TODO 3. send to registered delivery service for required channel
        pass
