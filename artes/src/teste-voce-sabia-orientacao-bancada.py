# Legiscópio — "Você sabia? Orientação de bancada" (1080x1350)
# Paleta oficial (extraída da arte "Hoje no Senado")
import os
from PIL import Image, ImageDraw, ImageFont

FUNDO   = "#F4F7F3"  # fundo da página
VERDE   = "#05572F"  # verde principal: títulos, barras, caixa de destaque, URL
TEXTO   = "#10251A"  # texto forte (títulos de card)
TEXTO2  = "#4A5D51"  # texto secundário, subtítulos, rodapé
OLIVA   = "#5E7F22"  # kicker e rótulos em mono
BRANCO  = "#FFFFFF"  # fundo dos cards
BORDA   = "#CBD6CC"  # borda de card neutro
TAG_VD  = "#E6EDD3"  # etiqueta verde-clara
LIMA    = "#B9D86A"  # título dentro da caixa verde
LIMA_TX = "#E4F0C8"  # texto dentro da caixa verde

def achar(*cs):
    for c in cs:
        if os.path.exists(c): return c
    raise FileNotFoundError(", ".join(cs))
N="/usr/share/fonts/opentype/noto/"; DJ="/usr/share/fonts/truetype/dejavu/"
F_BLACK=achar(N+"NotoSansCJK-Black.ttc",N+"NotoSansCJK-Bold.ttc",DJ+"DejaVuSans-Bold.ttf")
F_BOLD =achar(N+"NotoSansCJK-Bold.ttc",DJ+"DejaVuSans-Bold.ttf")
F_REG  =achar(N+"NotoSansCJK-Regular.ttc",DJ+"DejaVuSans.ttf")
F_MONO =achar(DJ+"DejaVuSansMono.ttf"); F_MONOB=achar(DJ+"DejaVuSansMono-Bold.ttf",F_MONO)
print("Fontes:",F_BLACK,F_BOLD,F_REG,F_MONO)
BK=lambda s:ImageFont.truetype(F_BLACK,s,index=0)
BD=lambda s:ImageFont.truetype(F_BOLD,s,index=0)
RG=lambda s:ImageFont.truetype(F_REG,s,index=0)
MO=lambda s:ImageFont.truetype(F_MONO,s); MB=lambda s:ImageFont.truetype(F_MONOB,s)

W,H=1080,1350; ML=78; MR=W-78
img=Image.new("RGB",(W,H),FUNDO); d=ImageDraw.Draw(img)

def wrap(t,f,maxw):
    out=[];line=""
    for w in t.split():
        test=(line+" "+w).strip()
        if d.textlength(test,font=f)<=maxw: line=test
        else: out.append(line); line=w
    out.append(line); return out
def espacado(x,y,t,f,fill,esp,anchor_dir=False):
    larg=sum(d.textlength(c,font=f) for c in t)+esp*(len(t)-1)
    if anchor_dir: x=x-larg
    for c in t:
        d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+esp

# cabeçalho: logo + kicker
AQUI=os.path.dirname(os.path.abspath(__file__))
logo_p=next((c for c in [os.path.join(AQUI,"..","assets","logo-legiscopio.png"),
                         os.path.join(AQUI,"..","logo-legiscopio.png")] if os.path.exists(c)),None)
print("Logo:",logo_p)
if logo_p:
    lg=Image.open(logo_p).convert("RGBA"); alt=105
    lg=lg.resize((round(lg.width*alt/lg.height),alt),Image.LANCZOS)
    img.paste(lg,(ML+5,68),lg)
else:
    d.text((ML,100),"Legiscópio",font=BK(44),fill=VERDE)
espacado(MR,104,"VOCÊ SABIA?",MO(28),OLIVA,6,anchor_dir=True)

# etiqueta + título
y=210
f=MO(26); tw=d.textlength("GLOSSÁRIO",font=f)
d.rounded_rectangle([ML,y,ML+tw+32,y+46],radius=23,fill=TAG_VD)
d.text((ML+16,y+23),"GLOSSÁRIO",font=f,fill=TEXTO2,anchor="lm")
y+=72
for l in wrap("O que é orientação de bancada?",BK(80),MR-ML):
    d.text((ML,y),l,font=BK(80),fill=VERDE); y+=86
y+=18
d.text((ML,y),"Um termo que aparece em toda votação nominal.",font=RG(34),fill=TEXTO2); y+=74

# card branco com barra verde
def card(y,titulo,texto):
    linhas=wrap(texto,RG(31),MR-ML-60)
    h=40+50+len(linhas)*42+30
    d.rounded_rectangle([ML,y,MR,y+h],radius=22,fill=BRANCO,outline=VERDE,width=2)
    d.rounded_rectangle([ML,y,ML+16,y+h],radius=8,fill=VERDE)
    d.rectangle([ML+8,y,ML+16,y+h],fill=VERDE)
    d.text((ML+40,y+34),titulo,font=BD(38),fill=TEXTO)
    yy=y+92
    for l in linhas: d.text((ML+40,yy),l,font=RG(31),fill=TEXTO2); yy+=42
    return y+h+22
y=card(y,"O que é",
  "Antes de cada votação nominal, o líder de cada partido ou bloco indica como recomenda que seus deputados votem.")
# card das opções
f=MO(26); h=170
d.rounded_rectangle([ML,y,MR,y+h],radius=22,fill=BRANCO,outline=BORDA,width=2)
d.text((ML+40,y+34),"As quatro orientações",font=BD(38),fill=TEXTO)
x=ML+40; yy=y+100
for t in ["SIM","NÃO","LIBERADO","OBSTRUÇÃO"]:
    tw=d.textlength(t,font=f)
    d.rounded_rectangle([x,yy,x+tw+28,yy+44],radius=22,fill=TAG_VD)
    d.text((x+14,yy+22),t,font=f,fill=TEXTO2,anchor="lm"); x+=tw+28+14
y+=h+30

# caixa verde de destaque
txt=("A orientação é pública e fica registrada em cada votação. Comparar o voto "
     "com a orientação mostra quando alguém votou diferente do próprio partido.")
linhas=wrap(txt,RG(32),MR-ML-64); h=36+52+len(linhas)*44+30
d.rounded_rectangle([ML,y,MR,y+h],radius=22,fill=VERDE)
d.text((ML+32,y+32),"Por que importa",font=BK(38),fill=LIMA)
yy=y+92
for l in linhas: d.text((ML+32,yy),l,font=RG(32),fill=LIMA_TX); yy+=44

# rodapé
d.text((ML,H-92),"Fonte: Dados Abertos da Câmara dos",font=MO(21),fill=TEXTO2)
d.text((ML,H-64),"Deputados.",font=MO(21),fill=TEXTO2)
d.text((MR,H-64),"legiscopio.com.br",font=MB(23),fill=VERDE,anchor="ra")
img.save("teste-voce-sabia-orientacao-bancada.png")
# TikTok (contas Business) não aceita PNG: salva também em JPEG
img.save("teste-voce-sabia-orientacao-bancada.jpg", quality=92, optimize=True)
