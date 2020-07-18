import argparse

import connexion

# Create the application instance
app = connexion.App(__name__, specification_dir='./')

# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, nargs='?', default=5000)
    args = parser.parse_args()

    app.run(host='0.0.0.0', port=args.port, debug=True)
