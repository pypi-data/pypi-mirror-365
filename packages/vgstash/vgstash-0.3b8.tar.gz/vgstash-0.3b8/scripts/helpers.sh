#!/usr/bin/env bash

# This is a set of helper bash functions that are too small for their own file,
# but useful enough to be worth `source`ing in your bashrc.

# Faster general searching
function vgsrc() {
	case $# in
		1)
			vgstash list | grep -iE "$1"
			;;
		2)
			vgstash list "$1" | grep -iE "$2"
			;;
		*)
			echo "usage: vgsrc [game name]"
			echo " or    vgsrc [view name] [game name]"
			echo
			echo "Ex: vgsrc physical Borderlands"
			;;
	esac
}

# Faster adding
function vgadd() {
	vgstash add "$@"
}

# Shows you a list of *unique* game titles that you have beaten or completed.
# This allows you to weed out the games you own or have beaten on more than one
# platform.
function vgub() {
	# TODO: improve
	vgstash list -w 80 | head -n 2
	vgstash list done -w 80 | sed -e '1,2d' | sort | uniq -w50 | sort -b -t'|' -k 2,2
}

# Shows you the titles of games that you own on more than one system.
function vgmulti() {
	vgstash list owned -w 80 | sed -e '1,2d' | sort -b -t'|' -k 1,1 | uniq -d -w50 | cut -d'|' -f 1
}

# Prints the title and system of a random game that you need to beat.
# This tool is great for deciding what to play to knock out the backlog.
function vgrand() {
	local game=$(vgstash list playlog | sed -e '1,2d' | shuf -n 1 --random-source=/dev/random | cut -d '|' -f 1-2 | tr -s ' ' | sed -e 's: | :, for :' -e 's:\s$::')
	echo "You should play ${game}!"
}

# Filters your vgstash output by system. Depends on awk
function vgsys() {
	local f='allgames'
	local s=''
	case $# in
		1)
			# single arg means we want the default filter
			s="$1"
			;;
		2)
			f="$1"
			s="$2"
			;;
		*)
			echo "USAGE: vgsys [FILTER] SYSTEM"
			echo
			echo "Show all games from a given system (and optionally, filter)."
			echo "Defaults to 'allgames' filter if the argument is missing."
			return
			;;
	esac
	vgstash list $f -w 80 | awk 'BEGIN {FS="|"} $2 ~ /'$s'/'
}
