from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models import user_model
from flask_app.models import recipe_model

@app.route('/recipes/new')
def new_recipe():
    if 'user_id' not in session:
        return redirect('/logout')
    return render_template('new_recipe.html', user = user_model.User.get_one(session['user_id']))

@app.route('/recipes/create', methods=['POST'])
def create_recipe():
    if 'user_id' not in session:
        return redirect('/logout')
    if not recipe_model.Recipe.validate_recipe(request.form):
        return redirect('/recipes/new')
    recipe_model.Recipe.save(**request.form, user_id = session['user_id'])
    return redirect('/recipes')

@app.route('/recipes/edit/<int:recipe_id>')
def edit_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        'recipe': recipe_model.Recipe.get_one(recipe_id),
        'user': user_model.User.get_one(session['user_id'])
        }
    return render_template('edit_recipe.html', **data)

@app.route('/recipes/<int:recipe_id>')
def view_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        'user': user_model.User.get_one(session['user_id']),
        'recipe': recipe_model.Recipe.get_recipe_favorited_by(recipe_id)
        }
    for favs in data['recipe'].favorited_by:
        if session['user_id'] == favs.id:
            favd = True
            break
        else:
            favd = False
    print(favd)
    return render_template('view_recipe.html', recipe = data['recipe'], user = data['user'], favd = favd)

@app.route('/recipes/update/<int:recipe_id>', methods=['POST'])
def update_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect("/logout")
    if not recipe_model.Recipe.validate_recipe(request.form):
        return redirect(f"/recipes/edit/{recipe_id}")
    data = {
        'id': recipe_id,
        'name': request.form['name'],
        'description': request.form['description'],
        'instructions': request.form['instructions'],
        'date_made': request.form['date_made'],
        'under': request.form['under']
        }
    recipe_model.Recipe.edit_recipe(data)
    return redirect("/recipes")

@app.route('/recipes/add_favorite/<int:recipe_id>')
def add_user_favorite_to_recipe(recipe_id):
    favRecipe = {
        'recipe_id': recipe_id,
        'user_id': session['user_id']
    }
    user_model.User.add_favorite_recipe(favRecipe)
    return redirect(f'/recipes/{recipe_id}')

@app.route('/recipes/delete/<int:recipe_id>')
def delete_recipe(recipe_id):
    if 'user_id' not in session:
        return redirect("/logout")
    recipe_model.Recipe.delete(id = recipe_id)
    return redirect("/recipes")