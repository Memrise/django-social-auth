from django.utils.translation import ugettext


class SocialAuthBaseException(ValueError):
    """Base class for pipeline exceptions."""
    pass

class BackendError(SocialAuthBaseException):
    def __unicode__(self):
        return ugettext('Backend error: %s' % self.message)

class WrongBackend(BackendError):
    def __init__(self, backend_name):
        self.backend_name = backend_name

    def __unicode__(self):
        return ugettext('Incorrect authentication service "%s"') % \
                self.backend_name


class NotAllowedToDisconnect(SocialAuthBaseException):
    """User is not allowed to disconnect it's social account."""
    pass


class StopPipeline(SocialAuthBaseException):
    """Stop pipeline process exception.
    Raise this exception to stop the rest of the pipeline process.
    """
    def __unicode__(self):
        return ugettext('Stop pipeline')


class AuthException(SocialAuthBaseException):
    """Auth process exception."""
    def __init__(self, backend, *args, **kwargs):
        self.backend = backend
        super(AuthException, self).__init__(*args, **kwargs)


class AuthFailed(AuthException):
    """Auth process failed for some reason."""
    def __unicode__(self):
        if self.message == 'access_denied':
            return ugettext('Authentication process was cancelled')
        else:
            return ugettext('Authentication failed: %s') % \
                        super(AuthFailed, self).__unicode__()


class AuthCanceled(AuthException):
    """Auth process was canceled by user."""
    def __unicode__(self):
        return ugettext('Authentication process canceled')


class AuthUnknownError(AuthException):
    """Unknown auth process error."""
    def __unicode__(self):
        err = 'An unknown error happened while authenticating %s'
        return ugettext(err) % super(AuthUnknownError, self).__unicode__()


class AuthTokenError(AuthException):
    """Auth token error."""
    def __unicode__(self):
        msg = super(AuthTokenError, self).__unicode__()
        return ugettext('Token error: %s') % msg


class AuthMissingParameter(AuthException):
    """Missing parameter needed to start or complete the process."""
    def __init__(self, backend, parameter, *args, **kwargs):
        self.parameter = parameter
        super(AuthMissingParameter, self).__init__(backend, *args, **kwargs)

    def __unicode__(self):
        return ugettext('Missing needed parameter %s') % self.parameter


class AuthStateMissing(AuthException):
    """State parameter is incorrect."""
    def __unicode__(self):
        return ugettext('Session value state missing.')


class AuthStateForbidden(AuthException):
    """State parameter is incorrect."""
    def __unicode__(self):
        return ugettext('Wrong state parameter given.')


class AuthAlreadyAssociated(AuthException):
    """A different user has already associated the target social account"""
    pass


class AuthTokenRevoked(AuthException):
    """User revoked the access_token in the provider."""
    def __unicode__(self):
        return ugettext('User revoke access to the token')
