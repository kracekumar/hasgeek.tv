# -*- coding: utf-8 -*-

from flask import render_template, abort, g, flash, url_for
from coaster.views import load_model, load_models
from baseframe.forms import render_redirect, render_form, render_delete_sqla

from hgtv import app
from hgtv.views.login import lastuser
from hgtv.forms import PlaylistForm
from hgtv.models import db, Channel, Playlist


@app.route('/<channel>/new', methods=['GET', 'POST'])
@lastuser.requires_login
@load_model(Channel, {'name': 'channel'}, 'channel')
def playlist_new(channel):
    if channel.userid not in g.user.user_organization_ids():
        abort(403)
    # Make a new playlist
    form = PlaylistForm()
    form.channel = channel
    if form.validate_on_submit():
        playlist = Playlist(channel=channel)
        form.populate_obj(playlist)
        if not playlist.name:
            playlist.make_name()
        db.session.add(playlist)
        db.session.commit()
        flash(u"Created playlist '%s'." % playlist.title, 'success')
        return render_redirect(url_for('playlist_view', channel=channel.name, playlist=playlist.name), code=303)
    return render_form(form=form, title="New Playlist", submit=u"Create",
        cancel_url=url_for('channel_view', channel=channel.name), ajax=True)


@app.route('/<channel>/<playlist>/edit', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist')
    )
def playlist_edit(channel, playlist):
    if channel.userid not in g.user.user_organization_ids():
        abort(403)
    form = PlaylistForm(obj=playlist)
    form.channel = channel
    if form.validate_on_submit():
        form.populate_obj(playlist)
        db.session.commit()
        flash(u"Edited playlist '%s'" % playlist.title, 'success')
        return render_redirect(url_for('playlist_view', channel=channel.name, playlist=playlist.name), code=303)
    return render_form(form=form, title="Edit Playlist", submit=u"Save",
        cancel_url=url_for('playlist_view', channel=channel.name, playlist=playlist.name), ajax=True)


@app.route('/<channel>/<playlist>/delete', methods=['GET', 'POST'])
@lastuser.requires_login
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist')
    )
def playlist_delete(channel, playlist):
    if channel.userid not in g.user.user_organization_ids():
        abort(403)
    return render_delete_sqla(playlist, db, title=u"Confirm delete",
        message=u"Delete playlist '%s'? This cannot be undone." % playlist.title,
        success=u"You have deleted playlist '%s'." % playlist.title,
        next=url_for('channel_view', channel=channel.name))


@app.route('/<channel>/<playlist>')
@load_models(
    (Channel, {'name': 'channel'}, 'channel'),
    (Playlist, {'name': 'playlist', 'channel': 'channel'}, 'playlist')
    )
def playlist_view(channel, playlist):
    return render_template('playlist.html', channel=channel, playlist=playlist)
