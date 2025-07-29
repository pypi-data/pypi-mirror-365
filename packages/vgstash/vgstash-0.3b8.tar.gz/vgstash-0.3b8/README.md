# VGStash - meaningful game collection tracker

VGStash is a video game collection tracker that gives the user a number of
fields to track their games with, including ownership, progress, and notes. It
also comes with a set of filters that give users the ability to make meaningful
inquiries to their collection.

For the nerds, VGStash is written in [Python 3](https://python.org) and is
mostly powered by [SQLite](https://sqlite.org) via internal VIEWs. It's
available under the [AGPL-3.0-only][spdx-agpl3] license.

# Installation

There is a [VGStash PyPI page](https://pypi.org/project/vgstash), and it is
available via `pip`:

~~~
pip install [--user] vgstash
~~~

If you are a developer, the source can be cloned via Git:

~~~
git clone https://git.zlg.space/vgstash
# or, if the above isn't online...
git clone https://notabug.org/zlg/vgstash
~~~

# Concept

The core data structure of VGStash is the Game. Every Game in a player's
collection has a few important attributes, all of which are obvious to the
player:

* Title
* System
* Ownership – in what form do you possess it?
* Progress – how far are you in it?

Think of any game that you have a history with. Let's say it was a game you
bought as part of a Humble Bundle, but haven't started playing yet. Internally,
VGStash tracks it somewhat like this:

```
.--------------------------------------------------------.
| Title                  | System | Ownership | Progress |
|------------------------+--------+-----------+----------|
| FTL: Faster Than Light | Steam  | digital   | new      |
'--------------------------------------------------------'
```

This is the bare minimum information you need to meaningfully track a video game
in your collection. With it, you can begin to ask and answer questions you may
have about your collection.

Other fields sometimes get added to the database format as new features are 
added to VGStash:

* Notes
* Purchase Date
* Beaten Date
* Completion Date

These values are completely optional in your collection, but can make VGStash 
more useful.

# Python Usage

Importing the `vgstash` module is enough to get started!

Here's a basic script that imports VGStash, initializes a database, records a
single game, and lists its contents:

```python
#!/usr/bin/env python3
# a minimalist vgstash client
import vgstash

# Create a DB in RAM, just for fun.
mydb = vgstash.DB(path=":memory:")

# Make sure our database schema is in place.
mydb.create_schema()

# Define and add our game. Note that you can reference the internal numbers via
# pre-defined dictionaries. Use the integers directly at your own risk!
mygame = vgstash.Game("Golden Sun", "GBA", vgstash.OWNERSHIP["physical"], vgstash.PROGRESS["beaten"])
mydb.add_game(mygame)

# list out the games we have! vgstash.list_games returns an iterable, so for
# best results you'll want to output in a loop of some sort.
for game in mydb.list_games():
    print(game['title'], "for", game['system'])
```

If the output from the above is `Golden Sun for GBA`, everything works and
you're ready to start hacking a game collection into your code!

# Command Line Usage

VGStash comes with a command line client of the same name, which gives you
high level commands to manipulate the database with.

If you wanted to add the example game from earlier to your collection, you'd do
it like this:

```bash
$ vgstash add 'FTL: Faster Than Light' Steam d n "Bought-From: Humble Bundle\n\nThis game is cool."
Added FTL: Faster Than Light for Steam. You digitally own it and you have not
started it. It also has notes.
```

Pretty easy, huh? Each title and system added to VGStash is free-form and can be
tuned to match the user's preferences. This allows one to specify between
different platforms within another platform, such as Steam or Origin instead of
just PC. Some may want to differentiate Virtual Console games from regular games
on those systems. In either case, both are text fields.

In the above command, the `digital` ownership was abbreviated to just `d`, and
the `new` progress was shortened to `n`. This is allowed when specifying values
for these fields! It cuts down on typos and excessive repetition. Consideration
is made for any new values in these fields, so each option should start with a
different letter and abbreviations should be forward-compatible.

It looks like we added notes to that game, too...?

```
$ vgstash notes 'FTL: Faster Than Light' Steam
Notes for FTL: Faster Than Light on Steam:

Bought-From: Humble Bundle

This game is cool.
```

*Nice!*

## Commands

VGStash has a fairly small set of commands. For each command's description,
arguments in brackets are optional

### add

```
add TITLE SYSTEM [OWNERSHIP] [PROGRESS] [NOTES] [P_DATE] [B_DATE] [C_DATE]
```

Adds a game to the database.

`OWNERSHIP` may be one of: physical, digital, both, member

`PROGRESS` may be one of: unbeatable, new, playing, beaten, complete

`NOTES` should be a fully-quoted string, with newlines escaped

`P_DATE` is an ISO8601 date string, i.e. "2025-07-27", representing the day you 
purchased a game.

`P_DATE` is an ISO8601 date string, i.e. "2025-07-27", representing the day you 
beat a game. (i.e. saw the credits or defeated the primary antagonist)

`C_DATE` is an ISO8601 date string, i.e. "2025-07-27", representing the day you 
completed (100%d) a game.

---

Adding a game is trickier than it seems; the OWNERSHIP and PROGRESS fields are
important to get right if you want the game tracked correctly. Here are some
game archetypes:

* *Normal releases* can be physical, digital, or both, and any progress
* *Collections* can be physical, digital, or both, but must be unbeatable
* *Members of a collection* should be stored under the original release system,
  with an ownership of 'member', and tracked progress where applicable

In short, don't count a collection as part of your progress! Add the individual
games in that collection, then mark the collection game as unbeatable.

Internally, members do not get listed for ownership filters, because *the
collection* is the item the user owns. Here's an example straight from ZLG's
VGStash:

```
Title                                |  System  | Own | Progress
-----------------------------------------------------------------
Mega Man ZX                          |    DS    |  M  |       C
Mega Man ZX Advent                   |    DS    |  M  |       C
Mega Man Zero                        |   GBA    |  M  |       C
Mega Man Zero 2                      |   GBA    |  M  |       C
Mega Man Zero 3                      |   GBA    |  M  |       C
Mega Man Zero 4                      |   GBA    |  M  |       C
Mega Man Zero/ZX Legacy Collection   |  Switch  | P   |
```

As seen above, the collection game is marked `physical`, but all of its members
are marked `member`, *and* are listed under the release that's made available on
the collection. This is the correct representation of a collection and its
members.

### delete

```
delete TITLE SYSTEM
```

Removes a game from the database.

### export

```
export [-f FORMAT] [PATH]
```

Exports the entire VGStash database to PATH in FORMAT format. FORMAT may be
either YAML or JSON. If FORMAT is omitted, it defaults to YAML. If PATH is
omitted, it will write to standard output (`stdout`).

### import

```
import [-f FORMAT] [-u] [PATH]
```

Imports games from PATH in FORMAT format, optionally updating games that already
exist in the database. If PATH is omitted, it will read from standard input
(`stdin`).

### list

```
list [FILTER] [-w WIDTH] [-r]
```

List games in the database, optionally using a FILTER or restricting the output
to WIDTH characters. Optionally set raw mode, outputting each row as
pipe-delimited lines instead of a table.

---

Most of VGStash's power is in the `list` command. It comes with a set of default
filters that allow you to reason about your game collection. For example, this
command will show you every game marked "playing" that you also own in some way:

```bash
$ vgstash list -w 40 playlog
Title       |  System  | Own | Progress
----------------------------------------
Crashmo     |   3DS    |   D |   P
Ever Oasis  |   3DS    | P   |   P
Fire Emblem |   3DS    | P   |   P
Monster Hun |   3DS    |   D |   P
Box Pusher  |   DSi    |   D |   P
Glow Artisa |   DSi    |   D |   P
Dark Souls  |   PS3    | P   |   P
```

The `list` command is where you can best ask probing questions about your
collection, which can help you manage inventory, track how long a game has been
in your collection unbeaten, how many versions of a game you own, how many games
you've beaten, and so on. Here's how!

#### How many games have I beaten?

This one's easy! First, ask yourself if you want to target *just* the beaten
ones, or any that've been beaten *or* completed! Let's assume you want both
beaten and completed:

```
$ vgstash list done
```

"Done" is a filter name that targets *all* games in your collection that are
marked 'beaten' or 'completed'.

Counting this list needs a little massaging. VGStash outputs a 2-line header for
its tables, so we need the raw (`-r`) flag and pass it to a line counter:

```
$ vgstash list -r done | wc -l
```

Awesome! Mine says `378`. How many have you beaten?

#### Which games do I own?

VGStash has a few filters for this:

* **`physical`** tracks games whose ownership is marked physical
* **`digital`** tracks games whose ownership is marked digital
* **`owned`** tracks games marked physical, digital, *or* both

So, let's say you're adding your digital games to your collection and you want
to double check everything's good. Easy!

```
$ vgstash list digital
```

There are also extra ownership filters:

* **`members`** tracks games marked as being a member of a collection
* **`unowned`** tracks games you've added that you don't own (usually because
  you've beaten or completed them)

#### Which games need to be beaten or completed?

VGStash has filters for this, too:

* **`playlog`** tracks games whose progress is marked playing, that you own
* **`backlog`** tracks games whose progress is playing *or* new, that you own
* **`incomplete`** tracks games whose progress is beaten, but *not* completed
* **`complete`** tracks games whose progress is marked completed

Check `vgstash list --help` for more.

### notes

```
notes [-e] TITLE SYSTEM
```

Read (or edit, with the `-e` flag) notes for TITLE on SYSTEM.

### update

```
update TITLE SYSTEM FIELD VALUE
```

Update the FIELD with VALUE for TITLE on SYSTEM.

If you beat a game, for example:

```
$ vgstash update 'Super Mario Bros.' NES progress b
```

# Quoting Game Titles

A note on characters: some shells treat certain characters differently. The most
common ones you'll run into are punctuation, like single quotes ('), double
quotes (") and exclamation points (!). You'll need to search your shell's manual
for "character escaping" to get the details.

Let's take a few game titles that might be problematic for a shell, and add them
to VGStash. These examples assume you're using bash (the Bourne Again SHell) or
something comparable.

First: a title with single quotes and exclamation points:

```bash
$ vgstash add "Eek! It's a Bomb!" Android d n
```

Double quotes are useful for quoting just about any game title.

Next is a little more insidious: a title with two (or more) exclamation points:

```bash
$ vgstash add 'Mario Kart: Double Dash!!' GCN p n
```

Note that we're using single quotes; if we used double quotes, then the `!!`
would expand to the last command entered into the shell, creating
`Mario Kart: Double Dash<your last command here>`. Quite different from what
you'd expect!

But what if we, somehow, had both single quotes *and* sequential exclamation
points? Single-quoted strings cannot escape a single quote character. Double
quotes won't stop the `!!` expansion. Escaping the exclamation points retains
the backslash; what is one to do? There are a few ways to tackle this one:

```bash
# The easy way
$ vgstash add $'Some title\'s crazy!!' PC d n

# The hard way
$ vgstash add Some\ title\'s\ crazy\!\! PC d n

# The exotic way
$ vgstash add "Some title"\''s crazy!!' PC d n
```

The `$'text'` form is handy when you need to use double and/or single quotes
alongside exclamation points, or you can just escape every special character
(including space) as needed.

The "exotic" one takes advantage of the shell's built-in string concatenation
and the ability to mix quoting styles. First we have `Some title` in double
quotes; then an escaped single quote for literal output; then `s crazy!!` in
single quotes to avoid the `!!` expansion.

The last option is to disable the feature (history expansion) altogether, though
you'll miss out on nice stuff like `sudo !!`. In bash, it's disabled with `set
+H` or `set +o histexpand`. Change `+` to `-` to turn it back on when you're
done.

These tips may not work in all shells, so try using `echo` to print the title
you want before trying to add it in VGStash! If you accidentally add a game this
way, copy the title that's output in the success message and paste it into your
delete command:

```bash
# Let's say I used 'ls' last
$ vgstash add "my game!!" PC d n
Added my gamels for PC. You own it digitally and it's new.
$ vgstash delete "my gamels" PC
Removed my gamels for PC from your collection.
```

That's it! This is something that the shell does before VGStash begins
processing its arguments, so please don't report any bugs dealing with quoting.

# Roadmap

Goals planned for the full 0.3 release:

With version `0.3b8`, I am feeling more confident in VGStash's capabilities. An 
RC is planned with support for generating your vgstash-web page.

Goals planned for the 0.4 release:

* Iron out any initial bugs on Windows and Mac (testers welcome!)

Goals planned for the 0.5 release:

* some sort of GUI (Tk, curses, and Qt are current candidates)

Goals planned for the 1.0 release:

* A richer GUI, built in LOVE2D, SDL, or maybe Web tech.

# Contributing

If this interests you, please [e-mail me](mailto:zlg+vgstash@zlg.space).

[spdx-agpl3]: https://spdx.org/licenses/AGPL-3.0-only.html
