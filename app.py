from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'pawel'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sklep.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Produkt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nazwa = db.Column(db.String(100), nullable=False)
    cena = db.Column(db.Float, nullable=False)
    opis = db.Column(db.String(500)) 
    obrazek = db.Column(db.String(10))
    waga = db.Column(db.String(20))

def sortowanie_babelkowe(lista_produktow, tryb='rosnaco'):
    n = len(lista_produktow)
    posortowana = lista_produktow.copy()
    for i in range(n):
        for j in range(0, n - i - 1):
            zamien = False
            if tryb == 'rosnaco':
                if posortowana[j].cena > posortowana[j + 1].cena:
                    zamien = True
            elif tryb == 'malejaco':
                if posortowana[j].cena < posortowana[j + 1].cena:
                    zamien = True
            
            if zamien:
                posortowana[j], posortowana[j + 1] = posortowana[j + 1], posortowana[j]
    return posortowana

def inicjalizacja_bazy():
    with app.app_context():
        db.drop_all()
        db.create_all()

        p1 = Produkt(nazwa="kwiatowa ethiopia", cena=51.99, opis="nuty hibiskusa. delikatnie kwaśna. idealna pod przelew", obrazek="🌺", waga="250g")
        p2 = Produkt(nazwa="klasyk brazylijski", cena=49.99, opis="czekolada i orzechy. klasyk.", obrazek="🥜", waga="250g")
        p3 = Produkt(nazwa="sssnake blend", cena=99.99, opis="mocne espresso. nasza klasyczna mieszanka. kofeinowy strzał.", obrazek="🐍", waga="1000g")
        p4 = Produkt(nazwa="kenya-aaa", cena=42.99, opis="dla miłośników kwaśnych smaków. stworzona pod chemex", obrazek="🍋", waga="250g")
        p5 = Produkt(nazwa="gwatemalka", cena=45.99, opis="słodka, przyjemność dla podniebienia. dla spokojnych kawoszy", obrazek="🍯", waga="250g")
        p6 = Produkt(nazwa="bezkofeinowa", cena=67.99, opis="dla tych co nie mogą ale chcą. twoje serce będzie spokojne", obrazek="🫀", waga="500g")
        
        db.session.add_all([p1, p2, p3, p4, p5, p6])
        db.session.commit()

@app.route('/')
def index():
    produkty = Produkt.query.all()
    sort_mode = request.args.get('sort')
    if sort_mode == 'rosnaco':
        produkty = sortowanie_babelkowe(produkty, 'rosnaco')
    elif sort_mode == 'malejaco':
        produkty = sortowanie_babelkowe(produkty, 'malejaco')
    return render_template('index.html', produkty=produkty)

@app.route('/dodaj_do_koszyka/<int:id>')
def dodaj_do_koszyka(id):
    if 'koszyk' not in session:
        session['koszyk'] = []
    session['koszyk'].append(id)
    session.modified = True
    return redirect(url_for('index'))

@app.route('/koszyk')
def koszyk():
    ids_w_koszyku = session.get('koszyk', [])
    produkty_w_koszyku = [Produkt.query.get(id) for id in ids_w_koszyku if Produkt.query.get(id)]
    suma = sum(p.cena for p in produkty_w_koszyku)
    return render_template('koszyk.html', produkty=produkty_w_koszyku, suma=suma)

@app.route('/wyczysc_koszyk')
def wyczysc_koszyk():
    session.pop('koszyk', None)
    return redirect(url_for('koszyk'))

@app.route('/zloz_zamowienie', methods=['POST'])
def zloz_zamowienie():
    email = request.form.get('email')
    imie = request.form.get('imie')
    ids_w_koszyku = session.get('koszyk', [])
    produkty = [Produkt.query.get(id) for id in ids_w_koszyku if Produkt.query.get(id)]
    
    if not produkty:
        return redirect(url_for('koszyk'))

    suma = sum(p.cena for p in produkty)
 
    with open('zamowienia.txt', 'a', encoding='utf-8') as f:
        f.write(f"DATA: {datetime.now()} | KLIENT: {imie} ({email}) | KWOTA: {suma} PLN\n")

    session.pop('koszyk', None)
    return render_template('sukces.html', email=email, imie=imie)

if __name__ == '__main__':
    inicjalizacja_bazy()
    app.run(debug=True)
