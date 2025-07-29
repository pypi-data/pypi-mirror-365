import vgstash
import sqlite3
import click
import os
import subprocess
import sys
import tempfile
import yaml
import json

# Click also has this, but it doesn't support a fallback value.
from shutil import get_terminal_size

def get_db():
    """Fetch a vgstash DB object from the default location.

    Change DEFAULT_CONFIG['db_location'] before calling this function
    to alter behavior."""
    return vgstash.DB(vgstash.DEFAULT_CONFIG['db_location'])


@click.group('vgstash')
def cli():
    pass


@cli.command()
def init():
    db = get_db()
    click.echo("Initializing the database...")
    if db.create_schema():
        click.echo("Schema created.")
    else:
        raise sqlite3.OperationalError("Cannot create schema.")

def row_format(row, width, header):
    """
    Prints a row from the result set into a nice table.
    """
    # The magic number comes from:
    #    3 chars per separator (9 chars total)
    #    8 chars for "System" (so there's an additional space on each side)
    #    3 chars for "Own"
    #    9 chars for "Progress" and an additional space
    #    Total is 29 characters
    twidth = int(width) - 29
    if header == True:
        click.echo("{:<{w}s} | {:^8s} | {:^3s} | {}".format(
            "Title",
            "System",
            "Own",
            "Progress",
            w=twidth)
        )
        click.echo("-" * int(width))

    titlestr = "{: <{w}s}".format(row['title'][:twidth], w=twidth)
    systemstr = "{: ^8s}".format(row['system'][:8])
    # unowned, physical, digital, both
    ownltr = [' ', 'P', '  D', 'P D', ' M']
    ownstr = "{: <3s}".format(ownltr[row['ownership']])
    progltr = {
        0: '',
        1: 'N',
        2: 'P',
        3: 'B',
        4: 'C'
    }
    progstr = "{}".format((" " * (row['progress'] - 1) * 2) + progltr[row['progress']])
    print(" | ".join((titlestr, systemstr, ownstr, progstr)))


@cli.command('add')
@click.argument('title', type=str)
@click.argument('system', type=str)
@click.argument('ownership', type=str, required=False, default=vgstash.DEFAULT_CONFIG['ownership'])
@click.argument('progress', type=str, required=False, default=vgstash.DEFAULT_CONFIG['progress'])
@click.argument('notes', type=str, required=False, default="")
@click.argument('p_date', type=str, required=False, default="")
@click.argument('b_date', type=str, required=False, default="")
@click.argument('c_date', type=str, required=False, default="")
def add(title, system, ownership, progress, notes, p_date, b_date, c_date):
    db = get_db()
    game = vgstash.Game(title, system, ownership, progress, notes, p_date, b_date, c_date)
    try:
        # Convert user-input (meant to be RFC2822/ISO8601 dates) to timestamps
        if game.p_date:
            game.p_date = vgstash.iso_to_unix(game.p_date)
        if game.b_date:
            game.b_date = vgstash.iso_to_unix(game.b_date)
        if game.c_date:
            game.c_date = vgstash.iso_to_unix(game.c_date)
        db.add_game(game, update=False)
        own_clause = (
            "do not own it",
            "physically own it",
            "digitally own it",
            "digitally and physically own it",
            "own it in a collection"
        )
        progress_clause = (
            "cannot beat",
            "haven't started",
            "are playing",
            "have beaten",
            "have completed",
        )
        note_clause = "" if len(game.notes) == 0 else " It has notes."
        date_clause = "" if not (game.p_date or game.b_date or game.c_date) else " It has date data."
        click.echo("Added {} for {}. You {} and {} it.{}{}".format(
            game.title,
            game.system,
            own_clause[game.ownership],
            progress_clause[game.progress],
            note_clause,
            date_clause
        ))
    except sqlite3.IntegrityError as e:
        print(e)
        click.echo("Couldn't add game.")


@cli.command('list')
@click.argument('filter', type=click.Choice(vgstash.FILTERS.keys()), required=False, default="allgames")
@click.option('--raw', '-r', is_flag=True, show_default=True, default=False, help="Output raw, pipe-delimited lines")
def list_games(filter, raw):
    db = get_db()
    row_data = db.list_games(filter)
    if len(row_data) == 0:
        click.echo("No games matching this filter in your collection.")
        return

    if raw:
        for r in row_data:
            l = []
            for c in r:
                if c == None:
                    l.append(str(''))
                elif type(c) == int:
                    l.append(str(c))
                else:
                    tc = c.replace('\n', '\\n')
                    tc = tc.replace('\r', '\\r')
                    l.append(tc)
            click.echo("|".join(l))
        return

    # Get column names, and a list of widths ready to go with them
    columns = row_data[0].keys()
    widths = []
    for i in range(len(columns)):
        widths.append(len(columns[i]))

    # Make a cache to manipulate the data with
    row_cache = []
    for r in row_data:
        cache_row = []
        for c in r:
            cache_row.append(c)
        row_cache.append(cache_row)
    # We should have a full, mutable cache now!


    for r in row_cache:
        for i in range(len(columns)):
            # possible values for r[i]:
            #     title -> str
            #     system -> str
            #     ownership -> int
            #     progress -> int
            #     *_date -> int
            # process fields that need massaging for display
            if r[i] == None:
                r[i] = ""
            else:
                if columns[i] == "progress":
                    if r[i] == 0:
                        r[i] = ''
                    else:
                        r[i] = vgstash.vtok(r[i], vgstash.PROGRESS)[0].capitalize()
                if columns[i] == "ownership":
                    if r[i] == 0:
                        r[i] = ''
                    else:
                        r[i] = vgstash.vtok(r[i], vgstash.OWNERSHIP)[0].capitalize()
                if columns[i] == ("p_date") and r[i] != "":
                    r[i] = vgstash.unix_to_iso(int(r[i]))
                if columns[i] == ("b_date") and r[i] != "":
                    r[i] = vgstash.unix_to_iso(int(r[i]))
                if columns[i] == ("c_date") and r[i] != "":
                    r[i] = vgstash.unix_to_iso(int(r[i]))
                if columns[i] == "notes" and len(r[i]) > 0:
                    r[i] = "*"
            # if isinstance(r[i], int):
            #     r[i] = str(r[i])
            # Store width in relevant list
            w = len(str(r[i]))
            if w > widths[i]:
                widths[i] = w

    # print the top header
    l = []
    left_fst = "{: <{w}s}"
    right_fst = "{: >{w}s}"
    center_fst = "{: ^{w}s}"

    for i in range(len(columns)):
        l.append(center_fst.format(columns[i], w=widths[i]))
    click.echo(" | ".join(l))

    l = []
    for w in widths:
        l.append("-"*w)
    click.echo("-+-".join(l))

    # print the collection now that the hard part is done!
    for r in row_cache:
        l = []
        for i in range(len(columns)):
            # TODO: set different fstring based on column name
            if columns[i] == 'years' or columns[i] == 'days':
                l.append(right_fst.format(str(r[i]), w=widths[i]))
            else:
                l.append(left_fst.format(r[i], w=widths[i]))
        click.echo(" | ".join(l))
    
@cli.command('delete')
@click.argument('title', required=True)
@click.argument('system', required=True)
def delete_game(title, system):
    db = get_db()
    target_game = vgstash.Game(title, system)
    if db.delete_game(target_game):
        click.echo("Removed {} for {} from your collection.".format(title, system))
    else:
        click.echo("That game does not exist in your collection. Please try again.")


@cli.command('update')
@click.argument('title', required=True)
@click.argument('system', required=True)
@click.argument('attr', type=click.Choice(['title', 'system', 'ownership', 'progress', 'p_date', 'b_date', 'c_date']), required=True)
@click.argument('val', required=True)
def update_game(title, system, attr, val):
    """
    Update a specific game's attribute in the database.

    Use the title and system parameters to target the game to update.
    Ownership and progress can be their letter or numeric values.
    p_date, b_date, and c_date MUST be ISO8601 dates, i.e. 2025-07-27
    """
    # TODO: Consider namedtuple as a solution
    db = get_db()
    try:
        target_game = db.get_game(title, system)
    except:
        click.echo("Game not found. Please try again.")
        return
    if attr == 'ownership':
        val = vgstash.vtok(val, vgstash.OWNERSHIP)
    if attr == 'progress':
        val = vgstash.vtok(val, vgstash.PROGRESS)
    updated_game = vgstash.Game(
        title = val if attr == 'title' else target_game.title,
        system = val if attr == 'system' else target_game.system,
        ownership = val if attr == 'ownership' else target_game.ownership,
        progress = val if attr == 'progress' else target_game.progress,
        notes = target_game.notes,
        p_date = vgstash.iso_to_unix(val) if attr == 'p_date' else target_game.p_date,
        b_date = vgstash.iso_to_unix(val) if attr == 'b_date' else target_game.b_date,
        c_date = vgstash.iso_to_unix(val) if attr == 'c_date' else target_game.c_date
    )
    if db.update_game(target_game, updated_game):
        click.echo("Updated {} for {}. Its {} is now {}.".format(title, system, attr, val))


@cli.command('notes')
@click.argument('title', required=True)
@click.argument('system', required=True)
@click.option('--edit', '-e', is_flag=True, default=False)
def notes(title, system, edit):
    db = get_db()
    try:
        target_game = db.get_game(title, system)
    except:
        click.echo("Game not found. Please try again.")
        return

    if edit:
        with tempfile.NamedTemporaryFile() as tmpfile:
            tmpfile.write(target_game.notes.encode("UTF-8"))
            tmpfile.flush()
            pre_stat = os.stat(tmpfile.name)
            o_mtime = pre_stat.st_mtime
            o_size = pre_stat.st_size
            try:
                process = subprocess.run([os.getenv("EDITOR", "vim"), tmpfile.name])
            except:
                click.echo("Could not run editor. Is it set correctly?")
                return
            tmpfile.flush()
            tmpfile.seek(0)
            post_stat = os.stat(tmpfile.name)
            n_mtime = post_stat.st_mtime
            n_size = post_stat.st_size
            note_arr = []
            for line in tmpfile:
                note_arr.append(line.decode("UTF-8").rstrip("\r\n"))
            target_game.notes = "\n".join(note_arr)
            db.update_game(target_game, target_game)
            if process.returncode == 0:
                # determine what actually happened
                if o_mtime == n_mtime:
                    if o_size == n_size:
                        click.echo("Notes for {} on {} left unchanged.".format(target_game.title, target_game.system))
                elif n_mtime > o_mtime and o_size != n_size:
                    click.echo("Notes for {} on {} have been updated!".format(target_game.title, target_game.system))
                return
            else:
                click.echo("The editor crashed. Please try again.")
                return
    else:
        if len(target_game.notes) > 0:
            click.echo("Notes for {} on {}:".format(target_game.title, target_game.system))
            click.echo()
            click.echo(target_game.notes)
        else:
            click.echo("No notes for {} on {}.".format(target_game.title, target_game.system))


@cli.command("import")
@click.option("--format", "-f", type=click.Choice(["yaml", "json"]), required=False, default="yaml")
@click.option("--update", "-u", is_flag=True, default=False, help="Overwrite existing games with the file's data")
@click.argument("filepath",
                type=click.Path(
                    readable=True,
                    resolve_path=True,
                    dir_okay=False,
                    file_okay=True),
                default=sys.stdin,
                required=False,
                )
def import_file(format, filepath, update):
    """
    Import game data from an external file matching the chosen format.

    The default format is YAML.

    Available formats:

    * JSON
    * YAML
    """
    with open(filepath) as fp:
        if format == "yaml":
            data = yaml.safe_load(fp)
        if format == "json":
            data = json.load(fp)
    db = get_db()
    count = len(data)
    for game in data:
        try:
            db.add_game(
                vgstash.Game(
                    game["title"],
                    game["system"],
                    game["ownership"],
                    game["progress"],
                    game["notes"]
                ),
                update=update
            )
        except sqlite3.IntegrityError as e:
            # skip games that already exist
            count -= 1
    if count > 0:
        click.echo("Successfully imported {} games from {}.".format(count, filepath))
    else:
        click.echo("Couldn't import any games. Is the file formatted correctly?")


@cli.command("export")
@click.option("--format", "-f", type=click.Choice(["yaml", "json"]), required=False, default="yaml")
@click.argument("filepath",
                type=click.Path(
                    exists=False,
                    readable=True,
                    writable=True,
                    resolve_path=True,
                    dir_okay=False,
                    file_okay=True),
                required=False,
                )
def export_file(format, filepath):
    """
    Export the game database to a file written in the chosen format.

    The default format is YAML.

    Available formats:

    * JSON
    * YAML
    """
    db = get_db()
    data = db.list_games()
    game_set = []
    # Time to re-read the master branch's code
    for game in data:
        g = {}
        for field in game.keys():
            g.update({field: game[field]})
        game_set.append(g)
    if not filepath:
        if format == "yaml":
            yaml.dump(game_set, sys.stdout, default_flow_style=False,
                             indent=4, allow_unicode=True)
        if format == "json":
            json.dump(game_set, sys.stdout, allow_nan=False, indent=1, skipkeys=True, sort_keys=True)
    else:
        with open(filepath, "w") as fp:
            if format == "yaml":
                yaml.dump(game_set, fp, default_flow_style=False,
                                 indent=4, allow_unicode=True)
            if format == "json":
                json.dump(game_set, fp, allow_nan=False, indent=1, skipkeys=True, sort_keys=True)
    if len(game_set) > 0:
        if filepath:
            click.echo("Successfully exported {} games to {}.".format(len(game_set), filepath))
    else:
        click.echo("Could not export any games; have you made sure your collection has games in it?")

