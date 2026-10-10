# Arte de teste — "Você sabia? Orientação de bancada" (1080x1350)
from PIL import Image, ImageDraw, ImageFont
W,H=1080,1350
VERDE="#05572F"; OLIVA="#8CA554"; OLIVA2="#5E7F22"; FUNDO="#F4F7F3"; TXT="#10291C"
img=Image.new("RGB",(W,H),FUNDO); d=ImageDraw.Draw(img)
B=lambda s:ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",s,index=0)
R=lambda s:ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",s,index=0)
M=lambda s:ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",s)
def wrap(t,f,maxw):
    out=[];line=""
    for w in t.split():
        test=(line+" "+w).strip()
        if d.textlength(test,font=f)<=maxw: line=test
        else: out.append(line); line=w
    out.append(line); return out
# faixa superior
d.rectangle([0,0,W,150],fill=VERDE)
d.text((80,48),"Legiscópio",font=B(46),fill="white")
d.text((W-80,62),"VOCÊ SABIA?",font=M(30),fill="#E3F1E8",anchor="ra")
# selo
d.rounded_rectangle([80,230,430,290],radius=30,fill=OLIVA)
d.text((255,260),"GLOSSÁRIO",font=B(28),fill="white",anchor="mm")
y=340
for l in wrap("O que é orientação de bancada?",B(84),W-160):
    d.text((80,y),l,font=B(84),fill=VERDE); y+=104
y+=30
d.rectangle([80,y,200,y+10],fill=OLIVA2); y+=50
corpo=("Antes de uma votação nominal, o líder de cada partido ou bloco indica "
       "como recomenda que seus deputados votem: Sim, Não, Liberado ou Obstrução.")
for l in wrap(corpo,R(40),W-160):
    d.text((80,y),l,font=R(40),fill=TXT); y+=60
y+=30
corpo2=("A orientação é pública e fica registrada junto de cada votação. "
        "Comparar o voto com a orientação mostra quando alguém votou diferente do próprio partido.")
for l in wrap(corpo2,R(40),W-160):
    d.text((80,y),l,font=R(40),fill=TXT); y+=60
# rodapé
d.line([80,H-170,W-80,H-170],fill=OLIVA,width=3)
d.text((80,H-140),"Fonte: Dados Abertos da Câmara dos Deputados",font=R(28),fill=OLIVA2)
d.text((80,H-95),"@legiscopio",font=B(34),fill=VERDE)
d.text((W-80,H-90),"ARTE DE TESTE",font=M(24),fill="#8a8a8a",anchor="ra")
img.save("teste-voce-sabia-orientacao-bancada.png")
