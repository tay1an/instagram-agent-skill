import cv2, numpy as np, sys
R='/home/user/instagram-agent-skill/.claude/instagram/medya/referans/'
O=sys.argv[1]
def temizle(ad, kutular, kirp):
    im=cv2.imread(R+f'harita-{ad}.jpg')
    for x1,y1,x2,y2 in kutular:
        # kutunun hemen dışındaki şeridin ortanca rengiyle düz doldur
        h,w=im.shape[:2]; a,b,c,d=max(0,x1-8),max(0,y1-8),min(w,x2+8),min(h,y2+8)
        halka=np.concatenate([im[b:y1,a:c].reshape(-1,3),im[y2:d,a:c].reshape(-1,3),im[b:d,a:x1].reshape(-1,3),im[b:d,x2:c].reshape(-1,3)])
        im[y1:y2,x1:x2]=np.median(halka,axis=0)
    x1,y1,x2,y2=kirp
    cv2.imwrite(f'{O}/{ad}.png',im[y1:y2,x1:x2])
# yakın: Cumhuriyet Cd. – İnönü Cad. kesişimi
temizle('yakin',[
 (310,488,645,588),       # giyim mağazası
 (400,945,605,1040),      # eczane
 (418,1095,518,1195),     # restoran simgesi
 (780,965,1100,1075),     # çiğ köfteci
 (700,1175,805,1286),     # hastane simgesi
], (420,370,1090,1225))
# çarşı: Koza Han, Setbaşı, Yeşil Türbe
temizle('carsi',[], (0,300,1045,885))
