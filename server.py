#start server file
from core.settings import create_app

config = {
 'development': 'config.Development',
 'production': 'config.Production'
}
app = create_app(config)

if __name__ == '__main__':
    app.run()
