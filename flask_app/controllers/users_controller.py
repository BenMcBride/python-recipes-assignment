from flask_app import app
from flask import render_template,redirect,request,session
from flask_app.models import user_model
from flask_app.models import recipe_model

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/recipes')
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    if not user_model.User.validate_user(request.form):
        return redirect('/')
    user_id = user_model.User.save(request.form)
    session.clear()
    session['user_id'] = user_id
    return redirect("/recipes")

@app.route('/login', methods=['POST'])
def login():
    user = user_model.User.validate_login(request.form)
    if not user:
        return redirect('/')
    session['user_id'] = user.id
    return redirect('/recipes')

@app.route('/recipes')
def recipes():
    if 'user_id' not in session:
        return redirect('/logout')
    user = user_model.User.get_one(session['user_id'])
    all_recipes = recipe_model.Recipe.get_all()
    return render_template("recipes.html", user = user, all_recipes = all_recipes)

@app.route('/favorites')
def favorites():
    if 'user_id' not in session:
        return redirect('/logout')
    user_obj = user_model.User.get_one(session['user_id'])
    user = user_model.User.get_user_fav_recipes(user_obj)
    if len(user.favorite_recipes) > 0:
        has_favs = True
    else:
        has_favs = False
    return render_template("view_favorites.html", user = user, has_favs = has_favs)

@app.route('/recipes/remove_favorite/<int:recipe_id>')
def remove_favorite(recipe_id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        'user_id': session['user_id'],
        'recipe_id': recipe_id
        }
    user_model.User.remove_favorite(data)
    return redirect(f'/recipes/{recipe_id}')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')