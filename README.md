# BotListă — Bot Telegram pentru lista de cumpărături

Bot Telegram scris în Python care îți gestionează lista de cumpărături direct din chat.
Suportă categorii, undo, partajare și mai mulți utilizatori simultan.

---

## Instalare și rulare

### 1. Clonează / descarcă proiectul

```bash
cd shopping_bot
```

### 2. Creează un mediu virtual (recomandat)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Instalează dependențele

```bash
pip install -r requirements.txt
```

### 4. Configurează tokenul botului

```bash
cp .env.example .env
```

Deschide `.env` și înlocuiește valoarea cu tokenul tău real de la @BotFather.

### 5. Pornește botul

```bash
python bot.py
```

---

## Cum obții un token de la @BotFather

1. Deschide Telegram și caută **@BotFather**
2. Trimite comanda `/newbot`
3. Urmează instrucțiunile: alege un nume și un username (trebuie să se termine în `bot`)
4. BotFather îți va da un token de forma `123456789:AAF...` — copiază-l în fișierul `.env`

---

## Comenzi disponibile

| Comandă | Descriere | Exemplu |
|---------|-----------|---------|
| `/start` | Mesaj de bun venit | `/start` |
| `/help` | Ajutor detaliat | `/help` |
| `/add <produs>` | Adaugă un produs | `/add lapte` |
| `/add <produs> #categorie` | Adaugă cu categorie | `/add lapte #lactate` |
| `/list` | Afișează lista completă | `/list` |
| `/done <nr>` | Bifează/debifează produs | `/done 3` |
| `/remove <nr>` | Șterge definitiv produs | `/remove 3` |
| `/clear` | Golește toată lista | `/clear` |
| `/undo` | Anulează ultima acțiune | `/undo` |
| `/share` | Rezumat text pentru partajare | `/share` |

### Text liber

Orice mesaj care nu începe cu `/` se adaugă automat la listă:

```
lapte
pâine, ouă, unt
brânză #lactate
```

---

## Categorii disponibile

| Tag | Categorie |
|-----|-----------|
| `#lactate` | 🥛 Lactate |
| `#carne` | 🥩 Carne |
| `#legume` | 🥦 Legume |
| `#fructe` | 🍎 Fructe |
| `#igiena` | 🧴 Igienă |
| `#panificatie` | 🍞 Panificație |
| `#altele` | 🛒 Altele (implicit) |

---

## Structura proiectului

```
shopping_bot/
├── bot.py           # Punct de intrare, înregistrare handleri
├── handlers.py      # Toți handlerii de comenzi și butoane
├── storage.py       # Logica de salvare/citire date (JSON)
├── config.py        # Configurație și categorii
├── requirements.txt # Dependențe Python
├── .env.example     # Exemplu variabile de mediu
├── .gitignore       # Fișiere ignorate de git
└── README.md        # Acest fișier
```

Datele sunt salvate local în `data.json`, câte un obiect per utilizator (identificat prin `user_id` Telegram).
