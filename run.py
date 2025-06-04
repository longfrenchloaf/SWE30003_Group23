from app import create_app
import logging

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    app.debug = True
    app.logger.setLevel(logging.DEBUG)
    # To see logger output in terminal when running with `python run.py`
    # you might need to ensure the default stream handler is also at DEBUG
    # For simple `print`, this is not needed.
    # For `app.logger`, Flask usually configures a basic handler.
    print("Starting Flask app with run.py, DEBUG=True")