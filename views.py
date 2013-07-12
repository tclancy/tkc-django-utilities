from django.conf import settings
from django.template import RequestContext, loader, Context
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response


# errors
def error_404(request):
	MEDIA_URL = settings.MEDIA_URL
	response = render_to_response('404.html',
			{
				'MEDIA_URL': settings.MEDIA_URL,
			})
	response.status_code = 404
	return response


def server_error(request, template_name='500.html'):
	t = loader.get_template(template_name)
	return HttpResponseServerError(t.render(Context({
		'MEDIA_URL': settings.MEDIA_URL,
	})))

def better_server_error(request, template_name='500.html'):
    t = loader.get_template(template_name)
    ltype, lvalue, ltraceback = sys.exc_info()
    sys.exc_clear()
    return HttpResponseServerError(t.render(Context({
            'MEDIA_URL': settings.MEDIA_URL,
            'type': ltype,
            'value': lvalue,
            'traceback': ltraceback
    })))