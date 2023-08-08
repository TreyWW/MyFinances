from django.urls import reverse


class Notification:
    def __init__(self, level, message, extra_tags='', colour='danger', time=False, buttons=None):
        self.level = level
        self.message = message
        self.extra_tags = extra_tags
        self.colour = colour
        self.buttons = buttons or []
        self.time = time

    def add_to_request(self, request):
        notifications = request.session.get('notifications', [])
        notifications.append({
            'level': self.level,
            'message': self.message,
            'extra_tags': self.extra_tags,
            'colour': self.colour,
            'buttons': self.buttons,
            'time': self.time
        })
        request.session['notifications'] = notifications

    @staticmethod
    def get_from_request(request):
        notifications = request.session.get('notifications', [])
        request.session['notifications'] = []
        return notifications


class Toast:
    def __init__(self, title, message, level='info', time=5000, autohide=True, delay=None, icon=None, progress=False, request=None):
        self.title = title
        self.message = message
        self.level = level
        self.time = time
        self.autohide = autohide
        self.delay = delay
        self.icon = icon
        self.progress = progress
        self.request = request

        if self.request is not None:
            self.add_to_request(self.request)

    def add_to_request(self, request):
        toasts = request.session.get('toasts', [])
        toasts.append({
            'title': self.title,
            'message': self.message,
            'level': self.level,
            'time': self.time,
            'autohide': self.autohide,
            'delay': self.delay,
            'icon': self.icon,
            'progress': self.progress,
        })
        request.session['toasts'] = toasts

    @staticmethod
    def get_from_request(request):
        toasts = request.session.get('toasts', [])
        request.session['toasts'] = []
        return toasts


class Toasts:
    def refresh(self):
        return {
            "title": "Page is outdated", "level": "warning",
            "text": "Your page is out of date. Please <a href='#' onclick='location.reload();return false;'>Click here to refresh</a>.",
            "position": "top-center"
        }


TOASTS = Toasts()


class Modals:
    @staticmethod
    def example(id="create_customer", success_message="Customer created with the name of ${$('#nameInput').val()}", toasts=[TOASTS.refresh()]):
        return {

        }