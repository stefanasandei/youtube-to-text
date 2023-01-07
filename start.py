from src.main import init

debug = True

if not debug:
    host = '0.0.0.0'
    port = 80
else:
    host = '127.0.0.1'
    port = 5000

if __name__ == "__main__":
    app = init()
    app.run(debug=debug, host=host, port=port)
