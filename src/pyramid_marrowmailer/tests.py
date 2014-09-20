from __future__ import with_statement
import unittest
import logging

from pyramid import testing


class ListHandler(logging.Handler):
    """Logging handler for testing"""

    debug = []
    warning = []
    info = []
    error = []
    critical = []

    def emit(self, record):
        getattr(self.__class__, record.levelname.lower())\
            .append(record.getMessage())

    @classmethod
    def reset(cls):
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), list):
                setattr(cls, attr, [])


class BaseFunctionalTest(unittest.TestCase):

    def setUp(self):
        self.request = testing.DummyRequest()
        self.config = testing.setUp(request=self.request)

    def tearDown(self):
        testing.tearDown()


class get_mailerTest(BaseFunctionalTest):
    def test_it(self):
        from pyramid_marrowmailer import get_mailer, TransactionMailer
        self.config.registry.settings['mail.transport.use'] = 'mock'
        self.config.include('pyramid_marrowmailer')
        mailer = get_mailer(self.request)
        self.assertTrue(isinstance(mailer, TransactionMailer))


class includemeTest(BaseFunctionalTest):
    def test_boolean_option(self):
        from pyramid_marrowmailer import get_mailer
        self.config.registry.settings['mail.transport.use'] = 'smtp'
        self.config.registry.settings['mail.transport.debug.on'] = 'true'
        self.config.include('pyramid_marrowmailer')
        self.assertTrue(get_mailer(self.request).config['transport.debug'])

    def test_digit_option(self):
        from pyramid_marrowmailer import get_mailer
        self.config.registry.settings['mail.transport.use'] = 'smtp'
        self.config.registry.settings['mail.transport.port.int'] = '100'
        self.config.include('pyramid_marrowmailer')
        self.assertEqual(get_mailer(self.request).config['transport.port'],
                         100)

    def test_mailer_config_prefix(self):
        from pyramid_marrowmailer import get_mailer
        settings = self.config.registry.settings
        settings['pyramid_marrowmailer.prefix'] = 'foobar.'
        settings['foobar.transport.use'] = 'smtp'
        self.config.include('pyramid_marrowmailer')
        self.assertEqual(get_mailer(self.request).config['transport.use'],
                         'smtp')

class directTest(BaseFunctionalTest):
    def configure(self):
        settings = self.config.registry.settings
        settings['mail.mode'] = 'direct'
        settings['mail.transport.use'] = 'logging'
        settings['mail.message.author'] = 'foobar@foo.com'
        self.config.include('pyramid_marrowmailer')

        logging.basicConfig()
        root_logger = logging.getLogger()
        self.handler = ListHandler()
        self.handler.reset()
        root_logger.addHandler(self.handler)

    def test_send(self):
        self.configure()
        from pyramid_marrowmailer import get_mailer
        mailer = get_mailer(self.request)

	message = mailer.new()
	message.subject = "foobar"
	message.to = "foobar@bar.com"
	message.plain = "hi"
	message.send()
	self.assertEqual(self.handler.info, [])

        self.assertTrue('DELIVER' in self.handler.info[1])

class transactionTest(BaseFunctionalTest):
    def configure(self):
        settings = self.config.registry.settings
        settings['mail.transport.use'] = 'logging'
        settings['mail.message.author'] = 'foobar@foo.com'
        self.config.include('pyramid_marrowmailer')

        logging.basicConfig()
        root_logger = logging.getLogger()
        self.handler = ListHandler()
        self.handler.reset()
        root_logger.addHandler(self.handler)

    def test_send(self):
        self.configure()
        from pyramid_marrowmailer import get_mailer
        mailer = get_mailer(self.request)

        import transaction
        with transaction.manager:
            message = mailer.new()
            message.subject = "foobar"
            message.to = "foobar@bar.com"
            message.plain = "hi"
            message.send()
            self.assertEqual(self.handler.info, [])

        self.assertTrue('DELIVER' in self.handler.info[1])

    def test_send_abort(self):
        self.configure()
        from pyramid_marrowmailer import get_mailer
        mailer = get_mailer(self.request)

        import transaction
        try:
            with transaction.manager:
                message = mailer.new()
                message.subject = "foobar2"
                message.to = "foobar2@bar.com"
                message.plain = "hi"
                message.send()
                raise ValueError
        except ValueError:
            pass

        self.assertEqual(self.handler.info, [])
