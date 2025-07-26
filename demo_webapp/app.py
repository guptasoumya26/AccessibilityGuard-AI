from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string('''
    <html>
    <head><title>Demo Web App - Base</title></head>
    <body>
        <h1>Welcome to the Base Version</h1>
        <button style="color: #eee; background: #fff;">Low Contrast Button</button>
        <img src="/static/logo.png">
        <p>Tab to the button to see a visible focus indicator.</p>
        <style>
            button:focus { outline: 2px solid #ff9800; }
        </style>
    </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(port=8001)
