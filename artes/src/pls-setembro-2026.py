# Legiscópio — "Em números: 226 PLs em setembro de 2026" (1080x1350)
# Paleta oficial (extraída da arte "Hoje no Senado")
import os
from PIL import Image, ImageDraw, ImageFont

FUNDO="#F4F7F3"; VERDE="#05572F"; TEXTO="#10251A"; TEXTO2="#4A5D51"; OLIVA="#5E7F22"
BRANCO="#FFFFFF"; BORDA="#CBD6CC"; TAG_VD="#E6EDD3"; LIMA="#B9D86A"; LIMA_TX="#E4F0C8"

def achar(*cs):
    for c in cs:
        if os.path.exists(c): return c
    raise FileNotFoundError(", ".join(cs))
N="/usr/share/fonts/opentype/noto/"; DJ="/usr/share/fonts/truetype/dejavu/"
F_BLACK=achar(N+"NotoSansCJK-Black.ttc",N+"NotoSansCJK-Bold.ttc",DJ+"DejaVuSans-Bold.ttf")
F_BOLD =achar(N+"NotoSansCJK-Bold.ttc",DJ+"DejaVuSans-Bold.ttf")
F_REG  =achar(N+"NotoSansCJK-Regular.ttc",DJ+"DejaVuSans.ttf")
F_MONO =achar(DJ+"DejaVuSansMono.ttf"); F_MONOB=achar(DJ+"DejaVuSansMono-Bold.ttf",F_MONO)
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
def espacado(x,y,t,f,fill,esp,direita=False):
    larg=sum(d.textlength(c,font=f) for c in t)+esp*(len(t)-1)
    if direita: x=x-larg
    for c in t:
        d.text((x,y),c,font=f,fill=fill); x+=d.textlength(c,font=f)+esp
def tag(x,y,t,f=None):
    f=f or MO(24); tw=d.textlength(t,font=f)
    d.rounded_rectangle([x,y,x+tw+26,y+42],radius=21,fill=TAG_VD)
    d.text((x+13,y+21),t,font=f,fill=TEXTO2,anchor="lm"); return x+tw+26

# cabeçalho
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
espacado(MR,104,"EM NÚMEROS",MO(28),OLIVA,6,direita=True)

# data + número
y=200
d.text((ML,y),"Câmara · setembro de 2026",font=MO(30),fill=TEXTO2); y+=48
d.text((ML-6,y-30),"226",font=BK(230),fill=VERDE)
x=ML+d.textlength("226",font=BK(230))+24
d.text((x,y+68),"projetos de lei",font=BK(52),fill=VERDE)
d.text((x,y+132),"apresentados",font=RG(40),fill=TEXTO2)
y+=262

# card: o que é um PL
def card(y,titulo,texto):
    linhas=wrap(texto,RG(31),MR-ML-60); h=40+50+len(linhas)*42+30
    d.rounded_rectangle([ML,y,MR,y+h],radius=22,fill=BRANCO,outline=VERDE,width=2)
    d.rounded_rectangle([ML,y,ML+16,y+h],radius=8,fill=VERDE); d.rectangle([ML+8,y,ML+16,y+h],fill=VERDE)
    d.text((ML+40,y+34),titulo,font=BD(38),fill=TEXTO)
    yy=y+92
    for l in linhas: d.text((ML+40,yy),l,font=RG(31),fill=TEXTO2); yy+=42
    return y+h+22
y=card(y,"O que é um PL","É o tipo de proposta usado para criar ou mudar leis ordinárias.")

# card: caminho
h=232
d.rounded_rectangle([ML,y,MR,y+h],radius=22,fill=BRANCO,outline=BORDA,width=2)
d.text((ML+40,y+30),"O caminho depois de apresentado",font=BD(36),fill=TEXTO)
f=MO(24); x=ML+40; yy=y+96; seta=lambda x,yy: d.text((x,yy+21),"→",font=MO(26),fill=OLIVA,anchor="lm")
for t in ["COMISSÕES","PLENÁRIO","SENADO"]:
    x=tag(x,yy,t,f)+10; seta(x,yy); x+=36
yy+=60; x=ML+40
x=tag(x,yy,"SANÇÃO OU VETO",f)
y+=h+28

# caixa verde
txt=("Muitos projetos ficam anos em tramitação ou são arquivados sem chegar ao Plenário.")
linhas=wrap(txt,RG(32),MR-ML-64); hb=36+52+len(linhas)*44+30
d.rounded_rectangle([ML,y,MR,y+hb],radius=22,fill=VERDE)
d.text((ML+32,y+32),"Na prática",font=BK(38),fill=LIMA)
yy=y+92
for l in linhas: d.text((ML+32,yy),l,font=RG(32),fill=LIMA_TX); yy+=44

# rodapé
d.text((ML,H-92),"Fonte: Dados Abertos da Câmara dos",font=MO(21),fill=TEXTO2)
d.text((ML,H-64),"Deputados.",font=MO(21),fill=TEXTO2)
d.text((MR,H-64),"app.legiscopio.com.br",font=MB(23),fill=VERDE,anchor="ra")
img.save("pls-setembro-2026.png")
