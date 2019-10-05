from .config import CRM_URLS


def get_url(request, prefix, uri):
    root = request.build_absolute_uri().split(prefix)[0]
    # print(root)
    return root + CRM_URLS[uri]
