from .views import index, history


def setup_routes(app):
    app.router.add_get('/{currency:\w+}', history, name='history')
    app.router.add_get('/', index)
