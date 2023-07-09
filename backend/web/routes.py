from flask import render_template, current_app as app


@app.route('/')
def home():
    """Landing page."""
    return render_template(
        'index.jinja2',
        title='Crypto Arbitrage Analytics bot',
        description='Main Page of the Crypto Arbitrage Analytics Bot App.',
        template='home-template',
        body='This is a homepage served with Flask.'
    )
