from fresco import FrescoApp, context

import views
import model

config = {
    'DATABASE': 'sample.db',
}

app = FrescoApp()
app.options.update(config)
app.options.update_from_file('settings.py')

model.setup_database(app.options.DATABASE)

app.include('/user/<username:str>/credentials', views.CredentialManager())
app.include('/user/<username:str>/host', views.HostManager())
app.include('/user', views.UserManager())
app.include('/', views.RootManager())

