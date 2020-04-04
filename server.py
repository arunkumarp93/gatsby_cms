#start server file
from core.settings import create_app

config = {
 'development': 'config.Development',
 'production': 'config.Production'
}

if __name__ == '__main__':
    app = create_app(config)
    app.run()
