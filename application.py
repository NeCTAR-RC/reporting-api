import json
from webob import Request, Response
import webob.dec
import webob.exc

class Application(object):

	def _get_method(self, func_name):
		return getattr(self, func_name, None)

	@webob.dec.wsgify
	def __call__(self, req_dict):
		req = Request(req_dict.environ)
		if 'wsgiorg.routing_args' in req.environ:
			routing_args = req.environ['wsgiorg.routing_args']
			for ent in routing_args:
				if isinstance(ent, dict) and 'method' in ent:
					method_name = ent['method']
					if method_name.startswith('_'):
						# Attempt to call a private method
						return webob.exc.HTTPForbidden()
					method = self._get_method(method_name)
					if method is None:
						# Method specified in interface specification, but not matching Python method found
						return webob.exc.HTTPNotImplemented()
					return method(routing_args[1])
		return webob.exc.HTTPNotFound()
