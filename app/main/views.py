from flask import render_template, flash, redirect, url_for
from flask.ext.login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, QuestionForm
from .. import db
from ..models import User, Role, Permission, Question
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = QuestionForm()
    if current_user.can(Permission.ASK) and \
            form.validate_on_submit():
        question = Question(body=form.body.data,
                            detail=form.detail.data,
                            author=current_user._get_current_object())
        db.session.add(question)
        return redirect(url_for('.index'))
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    return render_template('index.html', form=form, questions=questions)


@main.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    questions = Question.query.order_by(Question.timestamp.desc()).all()
    return render_template('user.html', user=user, questions=questions)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form)
