import atexit

import transaction
from marrow.mailer import Mailer
from pyramid.settings import asbool
from zope.interface import Interface


class IMarrowMailer(Interface):
    pass


class MailDataManager(object):
    """Stolen from repoze/sendmail/delivery.py under ZPL 1.1 license"""

    def __init__(self, callable, args, kwargs):
        self.callable = callable
        self.args = args
        self.kwargs = kwargs
        # Use the default thread transaction manager.
        self.transaction_manager = transaction.manager

    def commit(self, transaction):
        pass

    def abort(self, transaction):
        pass

    def sortKey(self):
        return str(id(self))

    # No subtransaction support.
    def abort_sub(self, transaction):
        pass  # pragma NO COVERAGE

    commit_sub = abort_sub

    def beforeCompletion(self, transaction):
        pass  # pragma NO COVERAGE

    afterCompletion = beforeCompletion

    def tpc_begin(self, transaction, subtransaction=False):
        assert not subtransaction

    def tpc_vote(self, transaction):
        pass

    def tpc_finish(self, transaction):
        self.callable(*self.args, **self.kwargs)

    tpc_abort = abort


class TransactionMailer(Mailer):
    """Mailer that obeys zope transaction for sending emails"""

    def send(self, *a, **kw):
        send_ = super(TransactionMailer, self).send
        transaction.get().join(MailDataManager(send_, a, kw))


def includeme(config):
    """Configure marrow.mailer"""
    settings = config.registry.settings
    prefix = settings.get('pyramid_marrowmailer.prefix', 'mail.').rstrip('.')

    # handle boolean options and int options .digit .on
    mailer_config = dict(filter(lambda d: d[0].startswith(prefix),
                                settings.items()))
    for key, value in dict(mailer_config).items():
        if key.endswith('.on'):
            mailer_config[key[:-3]] = asbool(value)
        if key.endswith('.int'):
            mailer_config[key[:-4]] = int(value)

    # bugfix for https://github.com/marrow/marrow.mailer/issues/45
    manager = '%s.manager.use' % prefix
    if manager not in mailer_config:
        mailer_config[manager] = 'immediate'

    mode = '%s.mode' % prefix
    if mailer_config.get(mode) == 'direct':
        mailer = Mailer(mailer_config, prefix)
    else:
        mailer = TransactionMailer(mailer_config, prefix)

    mailer.start()

    config.registry.registerUtility(mailer, IMarrowMailer)
    config.set_request_property(get_mailer, "mailer", reify=True)

    # shutdown mailer when process stops
    atexit.register(lambda: mailer.stop())


def get_mailer(request):
    """Obtain a mailer previously registered via
    ``config.include('pyramid_marrrowmailer')``.
    """
    return request.registry.getUtility(IMarrowMailer)
