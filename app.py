from flask import Flask, request, send_file, render_template_string
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import mm
import os, datetime, io, uuid

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB max upload

W, H = landscape(A4)
ASSETS = os.path.join(os.path.dirname(__file__), 'assets')

# ── Paleta ────────────────────────────────────────────────────────────────────
BG    = colors.HexColor('#0d2e2a')
PANEL = colors.HexColor('#1a3d35')
TEAL  = colors.HexColor('#4ecdc4')
WHITE = colors.white
GRAY  = colors.HexColor('#a8ccc8')
LGRAY = colors.HexColor('#6a9e99')
RED   = colors.HexColor('#e05c3a')
DARK  = colors.HexColor('#0a2420')
TDARK = colors.HexColor('#0d2e2a')
GD    = colors.HexColor('#0f3d30')

# ── Tabela de preços ──────────────────────────────────────────────────────────
TABELA = {
    'SPA RUBI':            {'TOP':11490,'EXCLUSIVE':12490,'PRIME':13490,'TOP COM DECK':16490,'EXCLUSIVE COM DECK':17490,'PRIME COM DECK':19590},
    'SPA TURQUESA':        {'TOP NEW':13990,'TOP NEW COM DECK':19990,'TOP':17490,'TOP COM DECK':22990,'EXCLUSIVE':18490,'EXCLUSIVE COM DECK':23990,'PRIME':19990,'PRIME COM DECK':25490},
    'SPA TURMALINA':       {'TOP':13490,'TOP COM DECK':18990,'EXCLUSIVE':14990,'EXCLUSIVE COM DECK':19490,'PRIME':19490,'PRIME COM DECK':24990},
    'SPA SAFIRA':          {'TOP':9490,'TOP COM DECK':14490,'EXCLUSIVE':10490,'EXCLUSIVE COM DECK':15490,'PRIME':11490,'PRIME COM DECK':16490},
    'SPA ESMERALDA':       {'TOP':9490,'TOP COM DECK':14490,'EXCLUSIVE':10490,'EXCLUSIVE COM DECK':15490,'PRIME':11490,'PRIME COM DECK':16490},
    'SPA DIAMANTE':        {'TOP':10990,'TOP + DECK':16490,'EXCLUSIVE':12490,'EXCLUSIVE + DECK':17490,'PRIME':14990,'PRIME + DECK':20490},
    'BANHEIRA JADE INDIVIDUAL': {'TOP':4990,'EXCLUSIVE':5990,'PRIME':6490},
    'BANHEIRA JADE DUPLA':      {'TOP':6068,'EXCLUSIVE':6490,'PRIME':6990},
    'BANHEIRA AMETISTA DUPLA':  {'TOP':6068,'EXCLUSIVE':6490,'PRIME':6990},
}

SPECS = {
    'SPA RUBI': ['01 Controle de nível','06 Jatos direcionais reguláveis em inox','12 Mini jatos em inox','01 Motobomba 1,5CV silenciosa','01 Filtro de papel','01 Acionador eletrônico c/ termômetro','01 Entrada de água','01 Ralo de fundo + 02 sucção','01 Aquecedor 8000W','01 Cromoterapia','04 Apoios de cabeça','Gel coat alto brilho + Fibra de vidro','Espessura 4,5 a 5mm · Skin Coat'],
    'SPA TURQUESA': ['01 Controle de nível','04 Jatos direcionais em inox','08 Mini jatos em inox','01 Motobomba 1,5CV silenciosa','01 Acionador eletrônico c/ termômetro','01 Entrada de água','01 Ralo de fundo','02 Sucção','01 Aquecedor 8000W','01 Cromoterapia','Gel coat alto brilho + Fibra de vidro','Espessura 4,5 a 5mm · Skin Coat'],
    'SPA TURMALINA': ['04 Jatos direcionais em inox','24 Mini jatos em inox','02 Motobomba 1,5CV silenciosa','01 Entrada de água','01 Controle de nível','01 Acionador eletrônico c/ termômetro','01 Filtro de papel','01 Aquecedor 8000W','04 Cromoterapias','01 Cascata em inox c/ motobomba 0,5CV','02 Camas','Gel coat alto brilho + Fibra de vidro','Espessura 4,5 a 5mm · Skin Coat'],
    'SPA SAFIRA': ['01 Controle de nível','04 Jatos direcionais reguláveis em inox','08 Mini jatos em inox','01 Motobomba 1CV silenciosa','01 Acionador eletrônico c/ termômetro','01 Entrada de água','01 Ralo de fundo','02 Sucção','01 Aquecedor 8000W','01 Cromoterapia','04 Apoios de cabeça','Gel coat alto brilho + Fibra de vidro','Espessura 4,5 a 5mm · Skin Coat'],
    'SPA ESMERALDA': ['01 Controle de nível','04 Jatos direcionais em inox','08 Mini jatos em inox','01 Motobomba 1CV silenciosa','01 Acionador eletrônico c/ termômetro','01 Entrada de água','01 Ralo de fundo','02 Sucção','01 Aquecedor 8000W','01 Cromoterapia','04 Apoios de cabeça','Gel coat alto brilho + Fibra de vidro','Espessura 4,5 a 5mm · Skin Coat'],
    'SPA DIAMANTE': ['04 Jatos direcionais em inox','08 Mini jatos em inox','01 Motobomba 1CV silenciosa','01 Acionador eletrônico c/ termômetro','01 Entrada de água','01 Aquecedor 8000W','01 Cromoterapia','Gel coat alto brilho + Fibra de vidro','Espessura 4,5 a 5mm · Skin Coat'],
    'BANHEIRA JADE INDIVIDUAL': ['Banheira individual retangular','01 Aquecedor','Hidromassagem completa','Gel coat alto brilho + Fibra de vidro','Tecnologia Skin Coat','20 anos de garantia estrutural'],
    'BANHEIRA JADE DUPLA': ['Banheira dupla retangular','01 Aquecedor','Hidromassagem completa','Gel coat alto brilho + Fibra de vidro','Tecnologia Skin Coat','20 anos de garantia estrutural'],
    'BANHEIRA AMETISTA DUPLA': ['Banheira dupla retangular','01 Aquecedor','Hidromassagem completa','Gel coat alto brilho + Fibra de vidro','Tecnologia Skin Coat','20 anos de garantia estrutural'],
}

SUBTITULOS = {
    'SPA RUBI': '7 Lugares Octagonal — 2,10 × 2,10 × 0,95m',
    'SPA TURQUESA': '6 Lugares Retangular — 2,00 × 2,20 × 0,95m',
    'SPA TURMALINA': '7 Lugares com 2 Camas — 2,20 × 2,40 × 0,85m',
    'SPA SAFIRA': '4 Lugares Quadrado — 1,70 × 1,60 × 0,80m',
    'SPA ESMERALDA': '4 Lugares Redondo — 1,80 × 1,80 × 0,93m',
    'SPA DIAMANTE': '4 Lugares Completo — 1,80 × 1,80 × 0,96m',
    'BANHEIRA JADE INDIVIDUAL': 'Individual Retangular — 1,70 × 0,80 × 0,45m',
    'BANHEIRA JADE DUPLA': 'Dupla Retangular — 1,72 × 1,20 × 0,45m',
    'BANHEIRA AMETISTA DUPLA': 'Dupla Retangular — 1,80 × 1,30 × 0,45m',
}

ADIC_MAP = {
    'Deck de madeira': 5000, 'Capa protetora': 3000, 'Kit Cascata': 3000,
    'Kit Air Blower': 3000, 'Ozônio': 1000, 'Escada alongada': 3000,
    'Cromoterapia adicional': 500, 'Módulo Wi-Fi': 800,
}

TODOS_ADICS = [
    ('Cromoterapia adicional', 'Luzes RGB para relaxamento'),
    ('Deck de madeira', 'Acabamento premium em madeira nobre'),
    ('Escada alongada', 'Acesso facilitado com escada integrada'),
    ('Kit Cascata', 'Cascata em inox com motobomba exclusiva'),
    ('Módulo Wi-Fi', 'Controle total pelo smartphone'),
    ('Capa protetora', 'Proteção térmica e contra sujeira'),
    ('Kit Air Blower', 'Bolhas de ar para relaxamento extra'),
    ('Ozônio', 'Purificação e tratamento da água'),
]

# ── Helpers PDF ───────────────────────────────────────────────────────────────
def fill(c, col=None): c.setFillColor(col or BG); c.rect(0,0,W,H,fill=1,stroke=0)
def box(c,x,y,w,h,col=PANEL,r=0):
    c.setFillColor(col)
    if r: c.roundRect(x,y,w,h,r,fill=1,stroke=0)
    else: c.rect(x,y,w,h,fill=1,stroke=0)
def boxs(c,x,y,w,h,col=PANEL,scol=TEAL,sw=1,r=5):
    c.setFillColor(col); c.setStrokeColor(scol); c.setLineWidth(sw); c.roundRect(x,y,w,h,r,fill=1,stroke=1)
def ln(c,x1,y1,x2,y2,col=TEAL,w=1): c.setStrokeColor(col); c.setLineWidth(w); c.line(x1,y1,x2,y2)
def t(c,s,x,y,sz=11,col=WHITE,bold=False,align='l'):
    c.setFillColor(col); c.setFont('Helvetica-Bold' if bold else 'Helvetica', sz); s=str(s)
    if align=='c': c.drawCentredString(x,y,s)
    elif align=='r': c.drawRightString(x,y,s)
    else: c.drawString(x,y,s)
def full_img(c, path):
    try: c.drawImage(path,0,0,width=W,height=H,preserveAspectRatio=False,mask='auto')
    except: fill(c)
def pimg(c,path,x,y,w,h):
    try: c.drawImage(path,x,y,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')
    except: box(c,x,y,w,h,col=PANEL,r=4)
def dot(c,x,y,col=TEAL,r=2.5): c.setFillColor(col); c.circle(x,y,r,fill=1,stroke=0)
def fmt(v): return 'R$ {:,.0f}'.format(int(v)).replace(',','.')
def rodape(c):
    box(c,0,0,W,14*mm,col=DARK); ln(c,0,14*mm,W,14*mm,col=TEAL,w=0.5)
    t(c,'naturebr.com  ·  (12) 99601-2821  ·  contato@naturebr.com',W/2,6*mm,sz=8,col=GRAY,align='c')

# ── Páginas PDF ───────────────────────────────────────────────────────────────
def pg_capa(c, orc, foto_path):
    fill(c); m=18*mm
    if foto_path: pimg(c,foto_path,W*0.44,0,W*0.56,H)
    c.setFillColor(colors.Color(0.05,0.18,0.15,alpha=0.35)); c.rect(W*0.44,0,W*0.56,H,fill=1,stroke=0)
    box(c,0,0,4*mm,H,col=TEAL); box(c,4*mm,H-7*mm,W*0.44-4*mm,7*mm,col=GD)
    t(c,'Nature',m+2*mm,H-28*mm,sz=36,col=TEAL,bold=True)
    t(c,'Spas & Banheiras',m+2*mm,H-38*mm,sz=10,col=LGRAY)
    ln(c,m+2*mm,H-43*mm,W*0.41,H-43*mm,col=TEAL,w=1.5)
    box(c,m+2*mm,H-56*mm,84*mm,11*mm,col=TEAL,r=5)
    t(c,'APRESENTAÇÃO COMERCIAL',m+2*mm+42*mm,H-49.5*mm,sz=9,col=TDARK,bold=True,align='c')
    t(c,'Para os seus',m+2*mm,H-74*mm,sz=22,col=WHITE)
    t(c,'melhores momentos',m+2*mm,H-90*mm,sz=30,col=TEAL,bold=True)
    ln(c,m+2*mm,H-96*mm,W*0.40,H-96*mm,col=TEAL,w=2.5)
    t(c,'Nº '+orc['numero'],m+2*mm,H-105*mm,sz=9,col=GRAY)
    t(c,orc['data']+'  ·  Validade: '+orc['validade'],m+2*mm,H-114*mm,sz=9,col=GRAY)
    box(c,m+2*mm,28*mm,W*0.39-m,74*mm,col=PANEL,r=8)
    box(c,m+2*mm,28*mm,3.5,74*mm,col=TEAL)
    t(c,'CLIENTE',m+9*mm,97*mm,sz=7,col=TEAL,bold=True)
    t(c,orc['cliente'],m+9*mm,82*mm,sz=20,col=WHITE,bold=True)
    ln(c,m+9*mm,78*mm,W*0.39-m-4*mm,78*mm,col=TEAL,w=0.5)
    t(c,'VENDEDOR',m+9*mm,70*mm,sz=7,col=GRAY,bold=True)
    t(c,orc['vendedor'],m+9*mm,60*mm,sz=13,col=WHITE)
    t(c,orc['produto']+' — '+orc['versao'],m+9*mm,46*mm,sz=10.5,col=TEAL,bold=True)
    t(c,orc['subtitulo'],m+9*mm,36*mm,sz=8,col=GRAY)
    rodape(c); c.showPage()

def pg_produto(c, orc):
    fill(c); m=18*mm
    t(c,orc['produto'],m,H-23*mm,sz=34,col=WHITE,bold=True)
    badge_w = len('VERSÃO '+orc['versao'])*5.5+20
    box(c,m,H-37*mm,badge_w,11*mm,col=TEAL,r=5)
    t(c,'VERSÃO '+orc['versao'],m+badge_w/2,H-30.5*mm,sz=9,col=TDARK,bold=True,align='c')
    t(c,orc['subtitulo'],m+badge_w+6*mm,H-31*mm,sz=10,col=GRAY)
    ln(c,m,H-44*mm,W-m,H-44*mm,col=TEAL,w=1.5)
    t(c,'ESTE SPA É EQUIPADO COM:',m,H-52*mm,sz=8,col=GRAY,bold=True)
    nc=3; cw=(W-2*m-(nc-1)*5*mm)/nc; rh=11.5*mm
    for i,sp in enumerate(orc['specs']):
        col=i%nc; row=i//nc
        sx=m+col*(cw+5*mm); sy=H-62*mm-row*rh
        box(c,sx,sy-2.5*mm,cw,10*mm,col=PANEL,r=4)
        dot(c,sx+4.5*mm,sy+2.5*mm,r=2)
        t(c,sp,sx+9*mm,sy,sz=9,col=WHITE)
    box(c,0,26*mm,W,16*mm,col=GD); ln(c,0,42*mm,W,42*mm,col=TEAL,w=0.5)
    difs=['Tecnologia Skin Coat','20 anos de garantia estrutural','Acessórios 100% em inox','Motobomba silenciosa','Sistema anti-transbordo']
    seg=W/len(difs)
    for i,d in enumerate(difs):
        cx=i*seg+seg/2; dot(c,cx-len(d)*2.6,34*mm,r=2); t(c,d,cx-len(d)*2.6+5,31*mm,sz=8.5,col=TEAL,bold=True)
    rodape(c); c.showPage()

def pg_galeria(c, fotos):
    fill(c); m=18*mm; pad=3*mm
    gw=(W-2*m-pad)/2; gh=(H-2*pad-pad)/2
    pos=[(m,pad*2+gh),(m+gw+pad,pad*2+gh),(m,pad),(m+gw+pad,pad)]
    for i,(fx,fy) in enumerate(pos):
        if i<len(fotos): pimg(c,fotos[i],fx,fy,gw,gh)
        else: box(c,fx,fy,gw,gh,col=PANEL,r=4)
    c.showPage()

def pg_valores(c, orc, anc, total_ind, economia):
    fill(c); m=18*mm
    t(c,'Valores e',m,H-24*mm,sz=20,col=WHITE)
    t(c,'Investimento',m,H-40*mm,sz=32,col=TEAL,bold=True)
    ln(c,m,H-45*mm,165*mm,H-45*mm,col=TEAL,w=2)
    lw=W*0.54-m-6*mm; ih=16*mm
    t(c,'SE COMPRADO SEPARADO:',m,H-53*mm,sz=7.5,col=GRAY,bold=True)
    for i,(nome,val) in enumerate(anc):
        y=H-62*mm-i*ih
        box(c,m,y-3*mm,lw,13*mm,col=PANEL,r=5)
        t(c,nome,m+5*mm,y+5*mm,sz=9,col=WHITE)
        vstr=fmt(val); t(c,vstr,m+lw-5*mm,y+5*mm,sz=10.5,col=RED,bold=True,align='r')
        vw=len(vstr)*6.0; c.setStrokeColor(RED); c.setLineWidth(1.3)
        c.line(m+lw-5*mm-vw,y+8.5*mm,m+lw-4*mm,y+8.5*mm)
    ti_y=H-62*mm-len(anc)*ih-3*mm
    ln(c,m,ti_y+10*mm,m+lw,ti_y+10*mm,col=LGRAY,w=0.5)
    t(c,'TOTAL se comprado separado:',m,ti_y,sz=8.5,col=GRAY,bold=True)
    tstr=fmt(total_ind); t(c,tstr,m+lw,ti_y,sz=13,col=RED,bold=True,align='r')
    tw=len(tstr)*7; c.setStrokeColor(RED); c.setLineWidth(1.8)
    c.line(m+lw-tw,ti_y+4.5*mm,m+lw+1,ti_y+4.5*mm)
    rx=W*0.54+6*mm; rw=W-m-rx
    t(c,'>',rx-7*mm,H/2-5*mm,sz=22,col=TEAL,bold=True)
    tv_y=H-62*mm-50*mm
    box(c,rx,tv_y,rw,82*mm,col=PANEL,r=10)
    box(c,rx,tv_y+78*mm,rw,4*mm,col=TEAL,r=10)
    t(c,'TUDO POR APENAS',rx+rw/2,tv_y+71*mm,sz=8,col=TDARK,bold=True,align='c')
    t(c,fmt(orc['val_combo']),rx+rw/2,tv_y+46*mm,sz=32,col=TEAL,bold=True,align='c')
    t(c,'À VISTA',rx+rw/2,tv_y+32*mm,sz=11,col=GRAY,bold=True,align='c')
    ln(c,rx+8*mm,tv_y+28*mm,rx+rw-8*mm,tv_y+28*mm,col=LGRAY,w=0.5)
    t(c,'Válido por '+orc['validade'],rx+rw/2,tv_y+20*mm,sz=8,col=LGRAY,align='c')
    if orc['frete']>0:
        t(c,'Frete: '+fmt(orc['frete']),rx+rw/2,tv_y+12*mm,sz=8,col=LGRAY,align='c')
    eco_y=tv_y-14*mm
    boxs(c,rx,eco_y,rw,12*mm,col=GD,scol=TEAL,sw=1,r=5)
    t(c,'Economia de '+fmt(economia)+' no combo!',rx+rw/2,eco_y+4*mm,sz=9.5,col=TEAL,bold=True,align='c')
    rodape(c); c.showPage()

def pg_promocao(c, orc, anc, total_ind):
    fill(c); m=18*mm
    t(c,'PROMOÇÃO',m,H-24*mm,sz=13,col=GRAY,bold=True)
    t(c,'Especial',m,H-42*mm,sz=36,col=TEAL,bold=True)
    ln(c,m,H-48*mm,165*mm,H-48*mm,col=TEAL,w=2)
    inclusos=[orc['produto']+' — versão '+orc['versao']]+orc['adicionais_inclusos']+\
        ['Suporte técnico de instalação','SAC exclusivo pós-venda','20 anos de garantia estrutural']
    if orc['frete']>0: inclusos.append('Frete incluso')
    for i,item in enumerate(inclusos):
        y=H-58*mm-i*12*mm; dot(c,m+3*mm,y+3.5*mm,r=3); t(c,item,m+9*mm,y,sz=10,col=WHITE)
    px=W*0.50+12*mm; pw=W-m-px
    box(c,px,H-62*mm,pw,22*mm,col=PANEL,r=6)
    t(c,'Se comprado separado:',px+pw/2,H-46*mm,sz=8,col=GRAY,align='c')
    tistr=fmt(total_ind); t(c,tistr,px+pw/2,H-60*mm,sz=18,col=RED,bold=True,align='c')
    tw3=len(tistr)*5.5; c.setStrokeColor(RED); c.setLineWidth(2)
    c.line(px+pw/2-tw3,H-54.5*mm,px+pw/2+tw3,H-54.5*mm)
    box(c,px,H-160*mm,pw,82*mm,col=PANEL,r=10)
    box(c,px,H-160*mm+78*mm,pw,4*mm,col=TEAL,r=10)
    t(c,'TUDO POR APENAS',px+pw/2,H-160*mm+71*mm,sz=8,col=TDARK,bold=True,align='c')
    t(c,fmt(orc['val_combo']),px+pw/2,H-160*mm+46*mm,sz=30,col=TEAL,bold=True,align='c')
    t(c,'À VISTA',px+pw/2,H-160*mm+32*mm,sz=11,col=GRAY,bold=True,align='c')
    ln(c,px+8*mm,H-160*mm+28*mm,px+pw-8*mm,H-160*mm+28*mm,col=LGRAY,w=0.5)
    t(c,'Válido por '+orc['validade'],px+pw/2,H-160*mm+20*mm,sz=8,col=LGRAY,align='c')
    rodape(c); c.showPage()

def pg_adicionais(c, adics_opcionais):
    fill(c); m=18*mm
    t(c,'Opções de',m,H-24*mm,sz=20,col=WHITE)
    t(c,'adicionais',m,H-40*mm,sz=32,col=TEAL,bold=True)
    ln(c,m,H-45*mm,W-m,H-45*mm,col=TEAL,w=1.5)
    if not adics_opcionais:
        t(c,'Todos os adicionais já estão inclusos neste orçamento!',W/2,H/2,sz=13,col=TEAL,bold=True,align='c')
        rodape(c); c.showPage(); return
    cw=(W-2*m-6*mm)/2; rh=22*mm
    for i,(nome,desc) in enumerate(adics_opcionais):
        col=i%2; row=i//2
        x=m+col*(cw+6*mm); y=H-55*mm-row*rh
        box(c,x,y-4*mm,cw,19*mm,col=PANEL,r=6)
        box(c,x,y-4*mm,3,19*mm,col=TEAL)
        dot(c,x+8*mm,y+8.5*mm,r=2.5)
        t(c,nome,x+13*mm,y+8.5*mm,sz=10,col=TEAL,bold=True)
        t(c,desc,x+13*mm,y,sz=8.5,col=GRAY)
    rodape(c); c.showPage()

def pg_fim(c, orc, foto_path):
    fill(c); m=18*mm
    box(c,0,H-10*mm,W,10*mm,col=TEAL); box(c,0,0,W,10*mm,col=TEAL)
    if foto_path: pimg(c,foto_path,m,12*mm,W/2-m-12*mm,H-24*mm)
    c.setFillColor(colors.Color(0.05,0.18,0.15,alpha=0.42))
    c.rect(m,12*mm,W/2-m-12*mm,H-24*mm,fill=1,stroke=0)
    rx=W/2+8*mm
    t(c,'Obrigado',rx,H-34*mm,sz=32,col=WHITE,bold=True)
    t(c,'por participar',rx,H-48*mm,sz=20,col=WHITE)
    t(c,'da nossa',rx,H-60*mm,sz=20,col=WHITE)
    t(c,'apresentação',rx,H-74*mm,sz=26,col=TEAL,bold=True)
    ln(c,rx,H-80*mm,W-m,H-80*mm,col=TEAL,w=2)
    t(c,'Proposta para: '+orc['cliente'],rx,H-90*mm,sz=9.5,col=GRAY)
    t(c,orc['produto']+' — Versão '+orc['versao'],rx,H-101*mm,sz=11,col=WHITE,bold=True)
    t(c,fmt(orc['val_combo'])+'  à vista',rx,H-114*mm,sz=17,col=TEAL,bold=True)
    ln(c,rx,H-120*mm,W-m,H-120*mm,col=LGRAY,w=0.5)
    for i,ct in enumerate(['(12) 99601-2821','contato@naturebr.com','naturebr.com','@naturebroficial']):
        t(c,ct,rx,H-130*mm-i*11*mm,sz=9.5,col=GRAY)
    t(c,'Nature',rx,28*mm,sz=26,col=TEAL,bold=True)
    t(c,'Para os seus melhores momentos',rx,18*mm,sz=9,col=LGRAY)
    c.showPage()

# ── Gerador principal ─────────────────────────────────────────────────────────
def gerar_pdf(orc, fotos_paths):
    buf = io.BytesIO()
    cv = canvas.Canvas(buf, pagesize=landscape(A4))
    cv.setTitle(f'Orçamento Nature — {orc["produto"]} — {orc["cliente"]}')
    cv.setAuthor('Nature Spas & Banheiras')

    anc = [(orc['produto']+' — versão '+orc['versao'], orc['val_spa'])]
    for a in orc['adicionais_inclusos']:
        anc.append((a, ADIC_MAP.get(a, 0)))
    if orc['frete'] > 0:
        anc.append(('Frete', orc['frete']))
    total_ind = sum(v for _,v in anc)
    economia  = total_ind - orc['val_combo']

    adics_opcionais = [(n,d) for n,d in TODOS_ADICS if n not in orc['adicionais_inclusos']]

    foto_capa = fotos_paths[0] if fotos_paths else None
    foto_fim  = fotos_paths[-1] if fotos_paths else None

    pg_capa(cv, orc, foto_capa)
    full_img(cv, os.path.join(ASSETS,'pg_quem.png')); cv.showPage()
    full_img(cv, os.path.join(ASSETS,'pg_diferenciais.png')); cv.showPage()
    full_img(cv, os.path.join(ASSETS,'pg_confianca.png')); cv.showPage()
    full_img(cv, os.path.join(ASSETS,'pg_reclame.png')); cv.showPage()
    pg_produto(cv, orc)
    if fotos_paths: pg_galeria(cv, fotos_paths)
    full_img(cv, os.path.join(ASSETS,'pg_entregamos.png')); cv.showPage()
    pg_valores(cv, orc, anc, total_ind, economia)
    pg_adicionais(cv, adics_opcionais)
    pg_fim(cv, orc, foto_fim)

    cv.save()
    buf.seek(0)
    return buf

# ── HTML do formulário ────────────────────────────────────────────────────────
HTML = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nature — Gerador de Orçamentos</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0d2e2a;color:#fff;min-height:100vh;padding:1.5rem 1rem}
.app{max-width:860px;margin:0 auto}
.header{display:flex;align-items:center;justify-content:space-between;margin-bottom:1.5rem;padding-bottom:1rem;border-bottom:1px solid rgba(78,205,196,0.2)}
.logo{font-size:1.6rem;font-weight:900;font-style:italic;color:#4ecdc4}
.logo small{display:block;font-size:.7rem;color:#6a9e99;font-style:normal;font-weight:400;text-transform:uppercase;letter-spacing:1px}
.badge{background:rgba(78,205,196,.12);border:1px solid rgba(78,205,196,.25);color:#4ecdc4;font-size:.68rem;padding:4px 12px;border-radius:20px;font-weight:700}
.card{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:12px;padding:1.25rem;margin-bottom:1rem}
.card-title{font-size:.68rem;font-weight:700;color:#4ecdc4;text-transform:uppercase;letter-spacing:1px;margin-bottom:1rem}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:.75rem}
.g3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:.6rem}
label{display:block;font-size:.7rem;color:rgba(255,255,255,.5);margin-bottom:3px;text-transform:uppercase;letter-spacing:.5px}
input,select{width:100%;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:.6rem .8rem;color:#fff;font-size:.88rem;outline:none;font-family:inherit}
input:focus,select:focus{border-color:#4ecdc4}
select option{background:#163d38}
.adic{background:rgba(255,255,255,.03);border:1.5px solid rgba(255,255,255,.07);border-radius:8px;padding:.6rem .85rem;cursor:pointer;display:flex;align-items:center;gap:8px;user-select:none}
.adic.on{border-color:#4ecdc4;background:rgba(78,205,196,.08)}
.chk{width:15px;height:15px;border-radius:4px;border:1.5px solid rgba(255,255,255,.2);flex-shrink:0;display:flex;align-items:center;justify-content:center;font-size:11px;color:#0a2420}
.adic.on .chk{background:#4ecdc4;border-color:#4ecdc4}
.an{font-size:.82rem;font-weight:500;flex:1}
.ref{background:rgba(78,205,196,.07);border:1px solid rgba(78,205,196,.2);border-radius:8px;padding:.7rem 1rem;margin-top:.6rem;display:none}
.ref label{color:#4ecdc4;font-size:.65rem}
.ref .val{font-size:1.1rem;font-weight:800;color:#4ecdc4}
.anc{background:rgba(255,255,255,.03);border-radius:8px;padding:1rem;margin-top:.8rem;display:none}
.anc-title{font-size:.65rem;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.8px;margin-bottom:.5rem}
.al{display:flex;justify-content:space-between;font-size:.83rem;padding:3px 0;color:rgba(255,255,255,.65)}
.al .rs{text-decoration:line-through;color:rgba(230,90,60,.8)}
.sep{border:none;border-top:1px solid rgba(255,255,255,.08);margin:.4rem 0}
.eco{display:inline-flex;align-items:center;background:rgba(78,205,196,.12);border:1px solid rgba(78,205,196,.2);color:#4ecdc4;border-radius:6px;padding:4px 10px;font-size:.78rem;font-weight:700;margin-top:.5rem}
.total{background:#4ecdc4;border-radius:10px;padding:.9rem 1.2rem;display:none;justify-content:space-between;align-items:center;margin-top:.8rem}
.total .tl{color:#0a2420;font-weight:800;font-size:.82rem;text-transform:uppercase}
.total .tv{color:#0a2420;font-weight:900;font-size:1.5rem}
.upload-area{border:2px dashed rgba(78,205,196,.3);border-radius:10px;padding:1.5rem;text-align:center;cursor:pointer;transition:all .2s}
.upload-area:hover,.upload-area.drag{border-color:#4ecdc4;background:rgba(78,205,196,.05)}
.upload-area p{color:#6a9e99;font-size:.85rem}
.upload-area strong{color:#4ecdc4}
.previews{display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px;margin-top:.8rem}
.preview-img{width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px;border:1px solid rgba(78,205,196,.3)}
.btn{background:#4ecdc4;color:#0a2420;border:none;border-radius:8px;padding:.85rem 2rem;font-weight:800;font-size:.95rem;cursor:pointer;width:100%;margin-top:1rem;display:flex;align-items:center;justify-content:center;gap:8px}
.btn:hover{background:#3abcb4}
.btn:disabled{opacity:.5;cursor:not-allowed}
.loading{display:none;text-align:center;padding:1rem;color:#4ecdc4;font-weight:600}
.sem-foto{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:8px;padding:.8rem;margin-top:.6rem;display:none}
.toggle-row{display:flex;align-items:center;gap:.75rem;font-size:.88rem;cursor:pointer}
.toggle{width:40px;height:22px;border-radius:11px;background:rgba(255,255,255,.1);position:relative;transition:background .2s;flex-shrink:0}
.toggle.on{background:#4ecdc4}
.toggle::after{content:'';position:absolute;width:16px;height:16px;border-radius:50%;background:#fff;top:3px;left:3px;transition:left .2s}
.toggle.on::after{left:21px}
@media(max-width:560px){.g2,.g3{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="app">
  <div class="header">
    <div class="logo">Nature<small>Gerador de Orçamentos</small></div>
    <div class="badge">PAINEL DO VENDEDOR</div>
  </div>

  <form id="form" enctype="multipart/form-data" method="POST" action="/gerar">

    <!-- CLIENTE -->
    <div class="card">
      <div class="card-title">Dados do cliente</div>
      <div class="g2">
        <div><label>Nome do cliente</label><input name="cliente" required placeholder="Ex: João Silva"/></div>
        <div><label>Vendedor responsável</label><input name="vendedor" required placeholder="Ex: Leonardo"/></div>
        <div><label>Cidade / Estado</label><input name="cidade" placeholder="Ex: São Paulo - SP"/></div>
        <div><label>Validade</label>
          <select name="validade"><option>7 dias</option><option selected>15 dias</option><option>30 dias</option></select>
        </div>
      </div>
    </div>

    <!-- PRODUTO -->
    <div class="card">
      <div class="card-title">Produto</div>
      <div class="g3">
        <div>
          <label>Categoria</label>
          <select id="cat" onchange="filtrarModelos()">
            <option value="">Selecionar...</option>
            <option value="spa">Spas</option>
            <option value="banheira">Banheiras</option>
          </select>
        </div>
        <div>
          <label>Modelo</label>
          <select id="modelo" name="produto" onchange="filtrarVersoes()"><option value="">— selecione categoria</option></select>
        </div>
        <div>
          <label>Versão</label>
          <select id="versao" name="versao" onchange="mostrarRef()"><option value="">— selecione modelo</option></select>
        </div>
      </div>
      <div class="ref" id="ref-box">
        <label>Preço de tabela (referência interna)</label>
        <div class="val" id="ref-val"></div>
      </div>
    </div>

    <!-- ADICIONAIS -->
    <div class="card">
      <div class="card-title">Adicionais inclusos neste orçamento</div>
      <div class="g3" id="adics-grid"></div>
      <input type="hidden" name="adicionais" id="adics-hidden"/>
    </div>

    <!-- VALOR -->
    <div class="card">
      <div class="card-title">Valor final do combo</div>
      <div class="g2">
        <div>
          <label>Valor que o cliente paga (R$)</label>
          <input id="vfinal" name="val_combo" type="number" placeholder="Ex: 19000" oninput="calcAnc()" required/>
        </div>
        <div>
          <label>Frete</label>
          <select id="frete-sel" name="frete" onchange="calcAnc()">
            <option value="0">Não incluir frete</option>
            <option value="3000">Sim — R$ 3.000</option>
            <option value="2000">Sim — R$ 2.000</option>
            <option value="2500">Sim — R$ 2.500</option>
          </select>
        </div>
      </div>
      <div class="anc" id="anc-box">
        <div class="anc-title">Ancoragem — preços individuais que aparecerão riscados no PDF</div>
        <div id="anc-linhas"></div>
        <hr class="sep"/>
        <div id="anc-total"></div>
        <div id="anc-eco"></div>
      </div>
      <div class="total" id="total-bar">
        <span class="tl">Oferta — tudo por apenas</span>
        <span class="tv" id="total-show"></span>
      </div>
    </div>

    <!-- FOTOS -->
    <div class="card">
      <div class="card-title">Fotos do produto</div>
      <div class="toggle-row" onclick="toggleFotos()">
        <div class="toggle" id="toggle-fotos"></div>
        <span id="toggle-label">Incluir fotos no orçamento</span>
      </div>
      <div id="fotos-area" class="sem-foto">
        <div class="upload-area" id="upload-area" onclick="document.getElementById('fotos').click()">
          <p><strong>Clique para selecionar</strong> ou arraste as fotos aqui</p>
          <p style="margin-top:4px;font-size:.78rem">Até 4 fotos · JPG ou PNG</p>
        </div>
        <input type="file" id="fotos" name="fotos" multiple accept="image/*" style="display:none" onchange="previewFotos(this)"/>
        <div class="previews" id="previews"></div>
      </div>
    </div>

    <button class="btn" type="submit" id="btn-gerar">&#128196; Gerar PDF do Orçamento</button>
    <div class="loading" id="loading">Gerando seu PDF... aguarde alguns segundos</div>
  </form>
</div>

<script>
const TAB={
  'SPA RUBI':{TOP:11490,EXCLUSIVE:12490,PRIME:13490,'TOP COM DECK':16490,'EXCLUSIVE COM DECK':17490,'PRIME COM DECK':19590},
  'SPA TURQUESA':{'TOP NEW':13990,'TOP NEW COM DECK':19990,TOP:17490,'TOP COM DECK':22990,EXCLUSIVE:18490,'EXCLUSIVE COM DECK':23990,PRIME:19990,'PRIME COM DECK':25490},
  'SPA TURMALINA':{TOP:13490,'TOP COM DECK':18990,EXCLUSIVE:14990,'EXCLUSIVE COM DECK':19490,PRIME:19490,'PRIME COM DECK':24990},
  'SPA SAFIRA':{TOP:9490,'TOP COM DECK':14490,EXCLUSIVE:10490,'EXCLUSIVE COM DECK':15490,PRIME:11490,'PRIME COM DECK':16490},
  'SPA ESMERALDA':{TOP:9490,'TOP COM DECK':14490,EXCLUSIVE:10490,'EXCLUSIVE COM DECK':15490,PRIME:11490,'PRIME COM DECK':16490},
  'SPA DIAMANTE':{TOP:10990,'TOP + DECK':16490,EXCLUSIVE:12490,'EXCLUSIVE + DECK':17490,PRIME:14990,'PRIME + DECK':20490},
  'BANHEIRA JADE INDIVIDUAL':{TOP:4990,EXCLUSIVE:5990,PRIME:6490},
  'BANHEIRA JADE DUPLA':{TOP:6068,EXCLUSIVE:6490,PRIME:6990},
  'BANHEIRA AMETISTA DUPLA':{TOP:6068,EXCLUSIVE:6490,PRIME:6990}
};
const AMAP={'Deck de madeira':5000,'Capa protetora':3000,'Kit Cascata':3000,'Kit Air Blower':3000,'Ozônio':1000,'Escada alongada':3000,'Cromoterapia adicional':500,'Módulo Wi-Fi':800};
const ADICS=[['Deck de madeira'],['Capa protetora'],['Kit Cascata'],['Kit Air Blower'],['Ozônio'],['Escada alongada'],['Cromoterapia adicional'],['Módulo Wi-Fi']];
const sel={};
let temFotos=false;

function fmt(v){return'R$ '+Math.round(v).toLocaleString('pt-BR')}

function filtrarModelos(){
  const cat=document.getElementById('cat').value;
  const mel=document.getElementById('modelo'),vel=document.getElementById('versao');
  mel.innerHTML='<option value="">— selecione</option>';
  vel.innerHTML='<option value="">— selecione</option>';
  document.getElementById('ref-box').style.display='none';
  Object.keys(TAB).forEach(k=>{
    const isSpa=k.startsWith('SPA');
    if((cat==='spa'&&isSpa)||(cat==='banheira'&&!isSpa)){
      const o=document.createElement('option');o.value=k;o.textContent=k;mel.appendChild(o);
    }
  });
}
function filtrarVersoes(){
  const mod=document.getElementById('modelo').value;
  const vel=document.getElementById('versao');
  vel.innerHTML='<option value="">— selecione</option>';
  document.getElementById('ref-box').style.display='none';
  if(!mod)return;
  Object.keys(TAB[mod]).forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v;vel.appendChild(o);});
}
function mostrarRef(){
  const mod=document.getElementById('modelo').value,ver=document.getElementById('versao').value;
  if(!mod||!ver){document.getElementById('ref-box').style.display='none';return;}
  const v=TAB[mod]?.[ver];
  if(v){document.getElementById('ref-val').textContent=fmt(v);document.getElementById('ref-box').style.display='block';}
  calcAnc();
}
function renderAdics(){
  document.getElementById('adics-grid').innerHTML=ADICS.map(([n])=>`
    <div class="adic${sel[n]?' on':''}" onclick="togAdic('${n}')">
      <div class="chk">${sel[n]?'✓':''}</div>
      <div class="an">${n}</div>
    </div>`).join('');
  document.getElementById('adics-hidden').value=Object.keys(sel).join(',');
}
function togAdic(n){sel[n]?delete sel[n]:sel[n]=AMAP[n]||0;renderAdics();calcAnc();}
function calcAnc(){
  const mod=document.getElementById('modelo').value,ver=document.getElementById('versao').value;
  const vf=Number(document.getElementById('vfinal').value)||0;
  const frete=Number(document.getElementById('frete-sel').value)||0;
  if(!vf||!mod||!ver){document.getElementById('anc-box').style.display='none';document.getElementById('total-bar').style.display='none';return;}
  const valSpa=TAB[mod]?.[ver]||0;
  const somaAdic=Object.values(sel).reduce((a,b)=>a+b,0);
  const totalInd=valSpa+somaAdic+frete;
  let l=`<div class="al"><span>${mod} — ${ver}</span><span class="rs">${fmt(valSpa)}</span></div>`;
  Object.entries(sel).forEach(([n,v])=>{l+=`<div class="al"><span>${n}</span><span class="rs">${fmt(v)}</span></div>`;});
  if(frete)l+=`<div class="al"><span>Frete</span><span class="rs">${fmt(frete)}</span></div>`;
  document.getElementById('anc-linhas').innerHTML=l;
  document.getElementById('anc-total').innerHTML=`<div class="al" style="font-weight:600;color:rgba(255,255,255,.85)"><span>Total individual</span><span class="rs" style="font-size:.95rem">${fmt(totalInd)}</span></div>`;
  const eco=totalInd-vf;
  document.getElementById('anc-eco').innerHTML=eco>0?`<div class="eco">Cliente economiza ${fmt(eco)}</div>`:'';
  document.getElementById('anc-box').style.display='block';
  document.getElementById('total-show').textContent=fmt(vf);
  document.getElementById('total-bar').style.display='flex';
}
function toggleFotos(){
  temFotos=!temFotos;
  document.getElementById('toggle-fotos').classList.toggle('on',temFotos);
  document.getElementById('toggle-label').textContent=temFotos?'Incluir fotos no orçamento (ativado)':'Incluir fotos no orçamento';
  document.getElementById('fotos-area').style.display=temFotos?'block':'none';
}
function previewFotos(input){
  const prev=document.getElementById('previews');
  prev.innerHTML='';
  const files=Array.from(input.files).slice(0,4);
  files.forEach(f=>{
    const img=document.createElement('img');
    img.className='preview-img';
    img.src=URL.createObjectURL(f);
    prev.appendChild(img);
  });
}
document.getElementById('form').addEventListener('submit',function(){
  document.getElementById('btn-gerar').disabled=true;
  document.getElementById('loading').style.display='block';
});
renderAdics();
</script>
</body>
</html>'''

# ── Rotas Flask ───────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/gerar', methods=['POST'])
def gerar():
    try:
        produto  = request.form.get('produto','')
        versao   = request.form.get('versao','')
        val_combo= int(request.form.get('val_combo',0))
        frete    = int(request.form.get('frete',0))
        adics_str= request.form.get('adicionais','')
        adicionais_inclusos = [a.strip() for a in adics_str.split(',') if a.strip()]

        val_spa = TABELA.get(produto,{}).get(versao, val_combo)

        orc = {
            'numero'  : 'ORC-'+datetime.date.today().strftime('%Y')+'-'+str(uuid.uuid4())[:4].upper(),
            'data'    : datetime.date.today().strftime('%d/%m/%Y'),
            'validade': request.form.get('validade','15 dias'),
            'cliente' : request.form.get('cliente','Cliente'),
            'vendedor': request.form.get('vendedor','Vendedor'),
            'produto' : produto,
            'versao'  : versao,
            'subtitulo': SUBTITULOS.get(produto,''),
            'specs'   : SPECS.get(produto,[]),
            'adicionais_inclusos': adicionais_inclusos,
            'val_spa' : val_spa,
            'val_combo': val_combo,
            'frete'   : frete,
        }

        # Fotos
        fotos_paths = []
        upload_dir = '/tmp/nature_uploads'
        os.makedirs(upload_dir, exist_ok=True)

        uploaded_files = request.files.getlist('fotos')
        for f in uploaded_files[:4]:
            if f and f.filename:
                path = os.path.join(upload_dir, str(uuid.uuid4())+'.jpg')
                f.save(path)
                fotos_paths.append(path)

        pdf_buf = gerar_pdf(orc, fotos_paths)

        nome_arquivo = f'Orcamento_Nature_{produto.replace(" ","_")}_{orc["cliente"].split()[0]}.pdf'

        # Limpar fotos temporárias
        for p in fotos_paths:
            try: os.remove(p)
            except: pass

        return send_file(pdf_buf, mimetype='application/pdf',
                        as_attachment=True, download_name=nome_arquivo)
    except Exception as e:
        return f'Erro ao gerar PDF: {str(e)}', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
