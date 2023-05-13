import sys

import curses

def ask_number_with_pager(text, question="Pick a number (0 to quit):"):
	try:
		stdscr = curses.initscr()
		curses.noecho()
		curses.cbreak() # react on keys without enter

		text_len_lines = len(text.split('\n'))
		max_top_line = text_len_lines - (curses.LINES-2)
		scrollarea = curses.newpad(text_len_lines, curses.COLS)
		scrollarea.addstr(0, 0, text)
		scrollarea_topline_ptr = 0
		def ensure_scrollarea_bounds(scrollarea_topline_ptr):
			scrollarea_topline_ptr = max(scrollarea_topline_ptr, 0)
			scrollarea_topline_ptr = min(scrollarea_topline_ptr, max_top_line)
			return scrollarea_topline_ptr
		def scrollarea_refresh():
			scrollarea.refresh(scrollarea_topline_ptr, 0, 0, 0, curses.LINES-3, curses.COLS-1)
			# remove artefacts due to smaller status line when scrolling up
			controlbar.addstr(0, 0, ' ' * curses.COLS)
			controlbar.addstr(0, 0,
				"Use arrow keys or PgUp/PgDown to scroll - lines %i-%i/%i %i%%" % (
					scrollarea_topline_ptr,
					scrollarea_topline_ptr + (curses.LINES-2),
					text_len_lines,
					int(100*scrollarea_topline_ptr / max_top_line)
				),
				curses.A_REVERSE
			)

		controlbar = stdscr.subwin(2, curses.COLS, curses.LINES-2, 0)
		controlbar.keypad(True) # enable key bindings and conversions
		# ensure clean line
		controlbar.addstr(1, 0, ' ' * (curses.COLS-1))
		controlbar.addstr(1, 0, question, curses.A_BOLD)
		controlbar.refresh()
		scrollarea_refresh()

		question += ' '
		input_string = ''
		while not input_string.endswith('\n'):
			c = controlbar.getkey(1, len(question) + len(input_string))
			if c == 'KEY_PPAGE':
				scrollarea_topline_ptr -= (curses.LINES-2) // 2
				scrollarea_topline_ptr = ensure_scrollarea_bounds(scrollarea_topline_ptr)
				scrollarea_refresh()
			elif c == 'KEY_NPAGE':
				scrollarea_topline_ptr += (curses.LINES-2) // 2
				scrollarea_topline_ptr = ensure_scrollarea_bounds(scrollarea_topline_ptr)
				scrollarea_refresh()
			elif c == 'KEY_UP':
				scrollarea_topline_ptr -= 1
				scrollarea_topline_ptr = ensure_scrollarea_bounds(scrollarea_topline_ptr)
				scrollarea_refresh()
			elif c == 'KEY_DOWN':
				scrollarea_topline_ptr += 1
				scrollarea_topline_ptr = ensure_scrollarea_bounds(scrollarea_topline_ptr)
				scrollarea_refresh()
			elif c == 'KEY_HOME':
				scrollarea_topline_ptr = 0
				scrollarea_topline_ptr = ensure_scrollarea_bounds(scrollarea_topline_ptr)
				scrollarea_refresh()
			elif c == 'KEY_END':
				scrollarea_topline_ptr = sys.maxsize
				scrollarea_topline_ptr = ensure_scrollarea_bounds(scrollarea_topline_ptr)
				scrollarea_refresh()
			elif c == 'KEY_BACKSPACE':
				input_string = input_string[:-1]
				controlbar.addstr(1, len(question) + len(input_string), ' ')
			#elif c == 'KEY_LEFT' or c == 'KEY_RIGHT':
			#	pass
			elif c.startswith('KEY_') or len(c) > 1:
				pass
			else:
				input_string += c
				if c != '\n':
					controlbar.addstr(1, 0, question, curses.A_BOLD)
					controlbar.addstr(1, len(question), input_string)
		return input_string
	finally:
		curses.nocbreak()
		stdscr.keypad(False)
		curses.echo()
		curses.endwin()
