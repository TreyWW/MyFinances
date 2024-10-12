from django.http import HttpResponseRedirect


def redirect_to_last_visited(request, fallback_url="dashboard"):
    """
    Redirects user to the last visited URL stored in session.
    If no previous URL is found, redirects to the fallback URL.
    :param request: HttpRequest object
    :param fallback_url: URL to redirect to if no previous URL found
    :return: HttpResponseRedirect object
    """
    try:
        last_visited_url = request.session.get("last_visited", fallback_url)
        return HttpResponseRedirect(last_visited_url)
    except KeyError:
        return HttpResponseRedirect(fallback_url)
