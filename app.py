from flask import Flask, render_template, redirect, url_for, session, request

app = Flask(__name__)
app.secret_key = "secret"

# Main onboarding sections
SECTIONS = [
    "Welcome",
    "Training",
    "Authentication",
    "Equipment",
    "Information sources",
    "Organisation structure",
    "myHR",
    "Employee benefits"
]

# Access checklist sections
ACCESS_SECTIONS = [
    "Jira", 
    "Confluence", 
    "Figma", 
    "ServiceNow", 
    "Service accounts", 
    "Developer folders",
    "Developer tools"
]

@app.route('/')
def home():
    return redirect(url_for('general', section_name=SECTIONS[0]))

@app.route('/general/<section_name>')
def general(section_name):
    return render_page(current_item=section_name)

@app.route('/access/<tool>')
def access(tool):
    return render_page(current_item=tool)

@app.route('/complete/<item>')
def complete(item):
    completed = session.get('completed', [])

    if item not in completed:
        completed.append(item)
        session['completed'] = completed
        session.modified = True   # ✅ add this

    return redirect(request.referrer or url_for('home'))

@app.route('/undo/<item>')
def undo(item):
    completed = session.get('completed', [])

    if item in completed:
        completed.remove(item)
        session['completed'] = completed
        session.modified = True

    return redirect(request.referrer or url_for('home'))

def render_page(current_item=None):
    completed = session.get('completed', [])
    return render_template(
        'index.html',
        sections=SECTIONS,
        access_sections=ACCESS_SECTIONS,
        current_item=current_item,
        completed=completed,
        content="Placeholder"
    )
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)