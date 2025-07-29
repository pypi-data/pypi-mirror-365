# Book Note Repository

A terminal-based note-taking app for organizing your thoughts on books. Fast, keyboard-driven, and distraction-free, built with Python and `curses`.

> Made for readers who prefer the terminal.

---

## Features

- Create and edit book entries  
- Take notes with line-wrapping  
- Tag books with multiple labels  
- Browse all tags and filter by tag  
- Search books or tags (case-insensitive)  
- Delete book entries  
- Keyboard-only UI  
- Saves data locally in `books.json`  

---

## How to Use

- `n`: New book  
- `Enter`: Open note or select tag  
- `Tab`: Switch between books and tags  
- `e`: Edit tags  
- `d`: Delete book  
- `/`: Search  
- `r`: Reset filters  
- `Ctrl+S`: Save note  
- `q`: Quit  

---

## Installation

Install via pip:

```bash
pip install booknotes
```

Then run the app:

```bash
booknotes
```

To install from source:

```bash
git clone https://github.com/bearenbey/book-notes.git
cd book-notes
pip install .
```

---

## Data Storage

All notes and metadata are saved in a single `books.json` file in the project directory. You can back this up or sync it across devices if needed.

---

## License

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU General Public License as published by  
the Free Software Foundation, either version 3 of the License, or  
(at your option) any later version.

This program is distributed in the hope that it will be useful,  
but WITHOUT ANY WARRANTY; without even the implied warranty of  
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the  
GNU General Public License for more details.

You should have received a copy of the GNU General Public License  
along with this program. If not, see <https://www.gnu.org/licenses/>.

© 2025 Eren Öğrül [termapp@pm.me](mailto:termapp@pm.me)
