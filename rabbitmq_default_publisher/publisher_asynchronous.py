import pika
import logging


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
                '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)

class publish_engine:

    def __init__(self):
        # number of messages to be published, global variables for connection and channel used in all callback methods
        self._number_of_messages = 10
        self._channel = None
        self._connection = None

    def on_open(self, connection):
        # Invoked when the connection is open
        print("Reached connection open \n")

        # opening a new channel by passing by passing callback function on_channel_open
        self._channel = self._connection.channel(self.on_channel_open)
        #connection.close()


    def on_declare(self, channel):
        # finally passing messages to the exchange
        print("Now in on declare")
        while self._number_of_messages > 0:
            print(self._number_of_messages)
            # empty '' string means default exchange, routing key (same as the queue name is automatically bound
            # to default exchange
            self._channel.basic_publish(exchange='',
                                routing_key='orders_q',
                                body='H' + str(self._number_of_messages),
                                properties=pika.BasicProperties(content_type='text/plain',
                                                        delivery_mode=2))

            self._number_of_messages -= 1
        self._connection.close()


    def on_channel_open(self, channel):
        # passing argument list
        print("Reached channel open \n")
        argument_list = {'x-queue-master-locator': 'random'}
        self._channel.queue_declare(self.on_declare, queue='orders_q', durable=True, arguments=argument_list)


    def on_close(self, connection, reply_code, reply_message):
        #This will be called on connection close
        print(reply_code)
        print(reply_message)
        print("connection is being closed \n")

    def run(self):
    # Create connection object, passing in the on_open method, logging = debug
        logging.basicConfig(level=logging.ERROR, format=LOG_FORMAT)
        credentials = pika.PlainCredentials('guest', 'guest')
        parameters = pika.ConnectionParameters('127.0.0.1', 5672, '/', credentials, socket_timeout=300)

        # starting asynchronous connection with server, on_open_callback ->
        # callback method that has to be called - when receiving response from rabbit mq server
        self._connection = pika.SelectConnection(parameters, on_open_callback=self.on_open)

        # callback method to be called when server is closed
        self._connection.add_on_close_callback(self.on_close)
        print("Script execution is done!! will start IO Loop")

        try:
            # Loop so we can communicate with RabbitMQ
            # if we receive connection open confirmation from RabbitMq the on_open method is called
            self._connection.ioloop.start()
        except KeyboardInterrupt:
            # Gracefully close the connection
            self._connection.close()

if __name__ == '__main__':
    # Create instance of class
    engine = publish_engine()
    engine.run()